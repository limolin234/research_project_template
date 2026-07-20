#!/usr/bin/env python3
"""Stateless DeepSeek context advisor with explicit typed appends."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable


DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_FACT_FILE = "fact.md"
DEFAULT_CONTEXT_FILE = "deepseek_context.md"
DEFAULT_TIMEOUT = 120.0
DEFAULT_MAX_TOKENS = 1800
DEFAULT_WARN_TOKENS = 600_000
DEFAULT_HARD_TOKENS = 900_000
ENV_ALLOWLIST = frozenset(
    {
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_MODEL",
        "DEEPSEEK_BASE_URL",
        "DEEPSEEK_THINKING",
        "DEEPSEEK_FACT_FILE",
        "DEEPSEEK_CONTEXT_FILE",
    }
)

TYPE_BASES: dict[str, frozenset[str]] = {
    "source-note": frozenset({"direct", "source-backed"}),
    "decision": frozenset({"direct", "user-confirmed"}),
    "hypothesis": frozenset({"inference", "speculative", "unknown"}),
    "insight": frozenset({"source-backed", "inference"}),
    "caution": frozenset({"direct", "source-backed", "inference"}),
    "negative-result": frozenset({"direct", "source-backed", "user-confirmed"}),
    "open-question": frozenset({"inference", "unknown"}),
}

SUPPORTING_CREDIBILITY = frozenset({"high", "medium", "low", "unknown"})
SUPPORTING_BASIS = frozenset(
    {"direct", "source-backed", "user-confirmed", "inference", "speculative", "unknown"}
)
LOGICAL_RELATIONS = frozenset({"supports", "conflicts", "depends-on", "limits", "extends"})


class ContextAgentError(RuntimeError):
    """Expected user-facing failure."""


class JsonArgumentParser(argparse.ArgumentParser):
    """Route command-line validation failures through the JSON error contract."""

    def error(self, message: str) -> None:
        raise ContextAgentError(message)


def _parse_env_value(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith('"'):
        try:
            parsed, end = json.JSONDecoder().raw_decode(value)
        except json.JSONDecodeError as exc:
            raise ContextAgentError(f"Invalid double-quoted .env value: {raw!r}") from exc
        if not isinstance(parsed, str):
            raise ContextAgentError(f"Expected a string .env value: {raw!r}")
        trailing = value[end:].strip()
        if trailing and not trailing.startswith("#"):
            raise ContextAgentError(f"Unexpected text after .env value: {raw!r}")
        return parsed
    if value.startswith("'"):
        end = value.find("'", 1)
        if end < 0:
            raise ContextAgentError(f"Invalid single-quoted .env value: {raw!r}")
        trailing = value[end + 1 :].strip()
        if trailing and not trailing.startswith("#"):
            raise ContextAgentError(f"Unexpected text after .env value: {raw!r}")
        return value[1:end]
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def load_env_fallback(env_path: Path) -> None:
    """Load a small, cross-platform .env subset without overriding the process."""

    if not env_path.is_file():
        return
    try:
        lines = env_path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise ContextAgentError(f"Cannot read .env file: {env_path}") from exc
    except UnicodeError as exc:
        raise ContextAgentError(f".env file is not valid UTF-8: {env_path}") from exc
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise ContextAgentError(f"Invalid .env line {line_number}: missing '='")
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ContextAgentError(f"Invalid .env key on line {line_number}: {key!r}")
        if key not in ENV_ALLOWLIST:
            continue
        if not os.environ.get(key, "").strip():
            os.environ[key] = _parse_env_value(raw_value)


def default_system_prompt_path() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "system_prompt.md"


def resolve_context_path(explicit: str | None) -> Path:
    configured = explicit or os.environ.get("DEEPSEEK_CONTEXT_FILE") or DEFAULT_CONTEXT_FILE
    return Path(configured).expanduser().resolve()


def resolve_fact_path(explicit: str | None) -> Path:
    configured = explicit or os.environ.get("DEEPSEEK_FACT_FILE") or DEFAULT_FACT_FILE
    return Path(configured).expanduser().resolve()


def read_optional_document(path: Path, label: str) -> str:
    if not path.exists():
        return ""
    if not path.is_file():
        raise ContextAgentError(f"{label} path is not a file: {path}")
    try:
        content = path.read_text(encoding="utf-8-sig").strip()
    except OSError as exc:
        raise ContextAgentError(f"Cannot read {label.lower()}: {path}") from exc
    except UnicodeError as exc:
        raise ContextAgentError(f"{label} is not valid UTF-8: {path}") from exc
    return content


def read_required_document(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ContextAgentError(f"Cannot read {label.lower()}: {path}") from exc
    except UnicodeError as exc:
        raise ContextAgentError(f"{label} is not valid UTF-8: {path}") from exc


def ensure_separate_memory_paths(fact_path: Path, context_path: Path) -> None:
    if fact_path == context_path:
        raise ContextAgentError(
            "Fact and context files must be different; remember may never write to the fact file."
        )


def read_project_documents(fact_path: Path, context_path: Path) -> tuple[str, str]:
    ensure_separate_memory_paths(fact_path, context_path)
    facts = read_optional_document(fact_path, "Fact file")
    context = read_optional_document(context_path, "Context file")
    if not facts and not context:
        raise ContextAgentError(
            "No usable project memory was found. Add source-traceable facts to "
            f"{fact_path} or working material to {context_path}."
        )
    return facts, context


def build_messages(
    system_prompt: str,
    facts: str,
    context: str,
    question: str,
    focus: str | None,
) -> list[dict[str, str]]:
    request = question.strip()
    if not request:
        raise ContextAgentError("The consultation question cannot be empty.")
    if focus:
        request += f"\n\nFocus: {focus.strip()}"
    messages = [{"role": "system", "content": system_prompt.strip()}]
    if facts:
        messages.append(
            {"role": "user", "content": f"<project_facts>\n{facts}\n</project_facts>"}
        )
    if context:
        messages.append(
            {
                "role": "user",
                "content": f"<working_context>\n{context}\n</working_context>",
            }
        )
    messages.append(
        {
            "role": "user",
            "content": f"<current_request>\n{request}\n</current_request>",
        }
    )
    return messages


def estimate_tokens(text: str) -> int:
    """Conservatively estimate tokens from character classes."""

    cjk = 0
    ascii_word_like = 0
    ascii_symbols = 0
    for char in text:
        codepoint = ord(char)
        if codepoint < 128:
            if char.isalnum() or char.isspace():
                ascii_word_like += 1
            else:
                ascii_symbols += 1
        elif (
            0x3400 <= codepoint <= 0x4DBF
            or 0x4E00 <= codepoint <= 0x9FFF
            or 0xF900 <= codepoint <= 0xFAFF
        ):
            cjk += 1
    other = len(text) - ascii_word_like - ascii_symbols - cjk
    raw_estimate = ascii_word_like * 0.5 + ascii_symbols + cjk + other * 2
    return max(1, math.ceil(raw_estimate * 1.1))


def request_budget(
    system_prompt: str,
    facts: str,
    context: str,
    question: str,
    focus: str | None,
    max_tokens: int,
    warn_tokens: int = DEFAULT_WARN_TOKENS,
    hard_tokens: int = DEFAULT_HARD_TOKENS,
) -> dict[str, Any]:
    if max_tokens <= 0:
        raise ContextAgentError("max-tokens must be greater than zero.")
    if warn_tokens <= 0 or hard_tokens <= 0 or warn_tokens >= hard_tokens:
        raise ContextAgentError("Token warning and hard limits are invalid.")
    request_text = question.strip()
    if focus:
        request_text += f"\n\nFocus: {focus.strip()}"
    message_text = system_prompt.strip()
    if facts:
        message_text += f"\n<project_facts>\n{facts}\n</project_facts>"
    if context:
        message_text += f"\n<working_context>\n{context}\n</working_context>"
    message_text += f"\n<current_request>\n{request_text}\n</current_request>"
    estimated_input = estimate_tokens(message_text) + 64
    estimated_total = estimated_input + max_tokens
    if estimated_total > hard_tokens:
        raise ContextAgentError(
            "Estimated request is too large: "
            f"{estimated_total:,} tokens including reserved output exceeds the "
            f"conservative hard limit of {hard_tokens:,}."
        )
    return {
        "estimated_input_tokens": estimated_input,
        "reserved_output_tokens": max_tokens,
        "estimated_total_tokens": estimated_total,
        "status": "warning" if estimated_total >= warn_tokens else "ok",
        "warning": estimated_total >= warn_tokens,
        "warn_limit": warn_tokens,
        "hard_limit": hard_tokens,
    }


def chat_endpoint(base_url: str) -> str:
    stripped = base_url.rstrip("/")
    if stripped.endswith("/chat/completions"):
        return stripped
    return stripped + "/chat/completions"


def _http_post_json(
    endpoint: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_bytes = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ContextAgentError(f"DeepSeek API returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ContextAgentError(f"DeepSeek API request failed: {exc.reason}") from exc
    except (TimeoutError, OSError) as exc:
        raise ContextAgentError(f"DeepSeek API request failed: {exc}") from exc
    try:
        raw = response_bytes.decode("utf-8")
        result = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContextAgentError("DeepSeek API returned invalid JSON.") from exc
    if not isinstance(result, dict):
        raise ContextAgentError("DeepSeek API returned an unexpected response shape.")
    return result


def parse_formal_content(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ContextAgentError("DeepSeek final content was not valid JSON.") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("content"), str):
        raise ContextAgentError("DeepSeek final content is missing the string field 'content'.")

    supporting = parsed.get("supporting_information", [])
    connections = parsed.get("logical_connections", [])
    conflicts = parsed.get("conflicts", [])
    uncertainties = parsed.get("uncertainties", [])
    if not isinstance(supporting, list) or not all(isinstance(item, dict) for item in supporting):
        raise ContextAgentError("DeepSeek field 'supporting_information' must be a list of objects.")
    if not isinstance(connections, list) or not all(isinstance(item, dict) for item in connections):
        raise ContextAgentError("DeepSeek field 'logical_connections' must be a list of objects.")
    if not isinstance(conflicts, list) or not all(isinstance(item, str) for item in conflicts):
        raise ContextAgentError("DeepSeek field 'conflicts' must be a list of strings.")
    if not isinstance(uncertainties, list) or not all(isinstance(item, str) for item in uncertainties):
        raise ContextAgentError("DeepSeek field 'uncertainties' must be a list of strings.")

    formal_supporting: list[dict[str, Any]] = []
    for item in supporting:
        item_content = item.get("content")
        credibility = item.get("credibility")
        basis = item.get("basis")
        sources = item.get("sources")
        if not isinstance(item_content, str):
            raise ContextAgentError("Each supporting item requires string 'content'.")
        if credibility not in SUPPORTING_CREDIBILITY:
            raise ContextAgentError("Each supporting item has an invalid 'credibility'.")
        if basis not in SUPPORTING_BASIS:
            raise ContextAgentError("Each supporting item has an invalid 'basis'.")
        if not isinstance(sources, list) or not all(isinstance(source, str) for source in sources):
            raise ContextAgentError("Each supporting item requires a string list 'sources'.")
        formal_supporting.append(
            {
                "content": item_content.strip(),
                "credibility": credibility,
                "basis": basis,
                "sources": sources,
            }
        )

    formal_connections: list[dict[str, str]] = []
    for item in connections:
        relation = item.get("relation")
        item_content = item.get("content")
        if relation not in LOGICAL_RELATIONS or not isinstance(item_content, str):
            raise ContextAgentError("Each logical connection requires a valid relation and content.")
        formal_connections.append({"relation": relation, "content": item_content.strip()})

    # Reconstruct every nested object from allow-listed fields. Extra analysis is discarded.
    return {
        "content": parsed["content"].strip(),
        "supporting_information": formal_supporting,
        "logical_connections": formal_connections,
        "conflicts": conflicts,
        "uncertainties": uncertainties,
    }


def consult_context(
    *,
    fact_path: Path,
    context_path: Path,
    system_prompt_path: Path,
    question: str,
    focus: str | None,
    api_key: str,
    model: str,
    base_url: str,
    thinking: str,
    timeout: float,
    max_tokens: int,
    transport: Callable[[str, str, dict[str, Any], float], dict[str, Any]] = _http_post_json,
    warning_sink: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    facts, context = read_project_documents(fact_path, context_path)
    system_prompt = read_required_document(system_prompt_path, "System prompt")
    if timeout <= 0:
        raise ContextAgentError("Timeout must be greater than zero.")
    budget = request_budget(system_prompt, facts, context, question, focus, max_tokens)
    if budget["warning"] and warning_sink is not None:
        warning_sink(
            "Warning: estimated request size is "
            f"{budget['estimated_total_tokens']:,} tokens; synthesis quality may degrade "
            f"before the hard limit of {budget['hard_limit']:,}."
        )
    messages = build_messages(system_prompt, facts, context, question, focus)
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "max_tokens": max_tokens,
        "stream": False,
        "thinking": {"type": thinking},
    }
    if thinking == "enabled":
        payload["reasoning_effort"] = "high"

    response = transport(chat_endpoint(base_url), api_key, payload, timeout)
    try:
        message = response["choices"][0]["message"]
        final_content = message["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ContextAgentError("DeepSeek API response did not contain final message content.") from exc
    if not isinstance(final_content, str) or not final_content.strip():
        raise ContextAgentError("DeepSeek API returned empty final message content.")

    formal = parse_formal_content(final_content)
    return formal


def validate_entry(entry_type: str, basis: str, sources: list[str], content: str) -> None:
    allowed = TYPE_BASES.get(entry_type)
    if allowed is None:
        raise ContextAgentError(f"Unknown record type: {entry_type}")
    if basis not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ContextAgentError(
            f"Basis {basis!r} is invalid for type {entry_type!r}; choose one of: {choices}."
        )
    if not sources or any(not source.strip() for source in sources):
        raise ContextAgentError("At least one non-empty source is required.")
    if not content.strip():
        raise ContextAgentError("Record content cannot be empty.")


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def format_entry(
    entry_type: str,
    basis: str,
    sources: list[str],
    content: str,
    scope: str | None,
) -> str:
    validate_entry(entry_type, basis, sources, content)
    lines = ["---", f"type: {entry_type}", f"basis: {basis}", "source:"]
    lines.extend(f"  - {_yaml_string(source.strip())}" for source in sources)
    if scope and scope.strip():
        lines.append(f"scope: {_yaml_string(scope.strip())}")
    lines.append("content: |")
    lines.extend(f"  {line}" if line else "" for line in content.strip().splitlines())
    return "\n".join(lines) + "\n"


def append_context(
    path: Path,
    *,
    entry_type: str,
    basis: str,
    sources: list[str],
    content: str,
    scope: str | None,
) -> None:
    entry = format_entry(entry_type, basis, sources, content, scope)
    try:
        entry.encode("utf-8")
    except UnicodeError as exc:
        raise ContextAgentError("Record fields and content must be valid UTF-8.") from exc
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size:
            existing = path.read_bytes()
            try:
                existing.decode("utf-8-sig")
            except UnicodeError as exc:
                raise ContextAgentError(f"Context file is not valid UTF-8: {path}") from exc
            prefix = "\n" if not existing.endswith(b"\n") else ""
        else:
            prefix = (
                "# DeepSeek Project Context\n\n"
                "Append-only working material for the context advisor. "
                "Consultation history is never stored here.\n\n"
            )
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(prefix)
            handle.write(entry)
    except OSError as exc:
        raise ContextAgentError(f"Cannot append context file: {path}") from exc


def _read_content_argument(value: str | None) -> str:
    if value is not None:
        return value
    if sys.stdin.isatty():
        raise ContextAgentError("Provide record content as an argument or through stdin.")
    try:
        return sys.stdin.read()
    except UnicodeError as exc:
        raise ContextAgentError("Record content from stdin is not valid UTF-8.") from exc


def _add_context_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--context",
        help=f"Context file (default: ./{DEFAULT_CONTEXT_FILE} or DEEPSEEK_CONTEXT_FILE).",
    )


def _add_fact_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--fact",
        help=f"Fact file (default: ./{DEFAULT_FACT_FILE} or DEEPSEEK_FACT_FILE).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        description="Consult or append a stateless DeepSeek project context."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    consult = subparsers.add_parser("consult", help="Consult without storing query history.")
    consult.add_argument("question", help="Natural-language request for the context advisor.")
    consult.add_argument("--focus", help="Optional focus or output constraint.")
    _add_fact_option(consult)
    _add_context_option(consult)
    consult.add_argument("--env-file", default=".env", help="Fallback env file (default: ./.env).")
    consult.add_argument("--model", help=f"Model (default: {DEFAULT_MODEL}).")
    consult.add_argument("--base-url", help=f"API base URL (default: {DEFAULT_BASE_URL}).")
    consult.add_argument(
        "--thinking",
        choices=("enabled", "disabled"),
        help="DeepSeek thinking mode (default: enabled).",
    )
    consult.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    consult.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)

    remember = subparsers.add_parser("remember", help="Append one validated context record.")
    remember.add_argument("content", nargs="?", help="Record content; reads stdin when omitted.")
    remember.add_argument("--type", required=True, choices=tuple(TYPE_BASES))
    remember.add_argument(
        "--basis",
        required=True,
        choices=tuple(sorted({basis for values in TYPE_BASES.values() for basis in values})),
    )
    remember.add_argument("--source", required=True, action="append", dest="sources")
    remember.add_argument("--scope")
    _add_context_option(remember)
    remember.add_argument("--env-file", default=".env", help="Fallback env file (default: ./.env).")

    budget = subparsers.add_parser("budget", help="Estimate context size without calling DeepSeek.")
    budget.add_argument("question", nargs="?", default="", help="Optional question to include.")
    budget.add_argument("--focus", help="Optional focus to include in the estimate.")
    _add_fact_option(budget)
    _add_context_option(budget)
    budget.add_argument("--env-file", default=".env", help="Fallback env file (default: ./.env).")
    budget.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)

    types = subparsers.add_parser("types", help="Print allowed write type/basis combinations.")
    types.set_defaults(show_types=True)
    return parser


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "types":
        return {key: sorted(value) for key, value in TYPE_BASES.items()}

    env_path = Path(args.env_file).expanduser().resolve()
    load_env_fallback(env_path)
    context_path = resolve_context_path(args.context)
    if args.command == "budget":
        fact_path = resolve_fact_path(args.fact)
        facts, context = read_project_documents(fact_path, context_path)
        prompt_path = default_system_prompt_path()
        prompt = read_required_document(prompt_path, "System prompt")
        return request_budget(prompt, facts, context, args.question, args.focus, args.max_tokens)
    if args.command == "remember":
        ensure_separate_memory_paths(resolve_fact_path(None), context_path)
        content = _read_content_argument(args.content)
        append_context(
            context_path,
            entry_type=args.type,
            basis=args.basis,
            sources=args.sources,
            content=content,
            scope=args.scope,
        )
        return {
            "written": True,
            "context": str(context_path),
            "type": args.type,
            "basis": args.basis,
            "sources": args.sources,
        }

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ContextAgentError(
            "DEEPSEEK_API_KEY is missing from the process environment and fallback .env."
        )
    model = args.model or os.environ.get("DEEPSEEK_MODEL") or DEFAULT_MODEL
    base_url = args.base_url or os.environ.get("DEEPSEEK_BASE_URL") or DEFAULT_BASE_URL
    thinking = args.thinking or os.environ.get("DEEPSEEK_THINKING") or "enabled"
    if thinking not in {"enabled", "disabled"}:
        raise ContextAgentError("DEEPSEEK_THINKING must be 'enabled' or 'disabled'.")
    return consult_context(
        fact_path=resolve_fact_path(args.fact),
        context_path=context_path,
        system_prompt_path=default_system_prompt_path(),
        question=args.question,
        focus=args.focus,
        api_key=api_key,
        model=model,
        base_url=base_url,
        thinking=thinking,
        timeout=args.timeout,
        max_tokens=args.max_tokens,
        warning_sink=lambda message: print(message, file=sys.stderr),
    )


def main() -> int:
    parser = build_parser()
    try:
        result = run(parser.parse_args())
    except ContextAgentError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
