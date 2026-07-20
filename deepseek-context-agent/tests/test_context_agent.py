from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "context_agent.py"
SPEC = importlib.util.spec_from_file_location("context_agent", SCRIPT)
assert SPEC and SPEC.loader
context_agent = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(context_agent)


class ContextAgentTests(unittest.TestCase):
    def test_env_fallback_does_not_override_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "DEEPSEEK_API_KEY=file-key\nDEEPSEEK_MODEL='file-model'\n",
                encoding="utf-8",
            )
            old_key = os.environ.get("DEEPSEEK_API_KEY")
            old_model = os.environ.get("DEEPSEEK_MODEL")
            try:
                os.environ["DEEPSEEK_API_KEY"] = "shell-key"
                os.environ.pop("DEEPSEEK_MODEL", None)
                context_agent.load_env_fallback(env_file)
                self.assertEqual(os.environ["DEEPSEEK_API_KEY"], "shell-key")
                self.assertEqual(os.environ["DEEPSEEK_MODEL"], "file-model")
            finally:
                if old_key is None:
                    os.environ.pop("DEEPSEEK_API_KEY", None)
                else:
                    os.environ["DEEPSEEK_API_KEY"] = old_key
                if old_model is None:
                    os.environ.pop("DEEPSEEK_MODEL", None)
                else:
                    os.environ["DEEPSEEK_MODEL"] = old_model

    def test_env_fallback_ignores_non_deepseek_variables_and_fills_empty_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "DEEPSEEK_API_KEY=file-key\nHTTPS_PROXY=https://untrusted.invalid\nUNRELATED=value\n",
                encoding="utf-8",
            )
            names = ("DEEPSEEK_API_KEY", "HTTPS_PROXY", "UNRELATED")
            old_values = {name: os.environ.get(name) for name in names}
            try:
                os.environ["DEEPSEEK_API_KEY"] = "   "
                os.environ.pop("HTTPS_PROXY", None)
                os.environ.pop("UNRELATED", None)
                context_agent.load_env_fallback(env_file)
                self.assertEqual(os.environ["DEEPSEEK_API_KEY"], "file-key")
                self.assertNotIn("HTTPS_PROXY", os.environ)
                self.assertNotIn("UNRELATED", os.environ)
            finally:
                for name, old_value in old_values.items():
                    if old_value is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = old_value

    def test_remember_writes_typed_record_without_id_or_relation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "context.md"
            context_agent.append_context(
                path,
                entry_type="hypothesis",
                basis="inference",
                sources=["user discussion", "source/note.md"],
                content="A possible explanation.\nStill unverified.",
                scope="prototype",
            )
            stored = path.read_text(encoding="utf-8")
            self.assertIn("type: hypothesis", stored)
            self.assertIn("basis: inference", stored)
            self.assertIn('  - "source/note.md"', stored)
            self.assertIn("A possible explanation.", stored)
            self.assertNotIn("id:", stored.lower())
            self.assertNotIn("relation", stored.lower())

    def test_type_basis_pair_is_enforced(self) -> None:
        with self.assertRaises(context_agent.ContextAgentError):
            context_agent.format_entry(
                "decision",
                "speculative",
                ["agent inference"],
                "This is not an accepted decision.",
                None,
            )

    def test_consults_are_independent_and_do_not_modify_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fact_path = root / "fact.md"
            context_path = root / "context.md"
            prompt_path = root / "prompt.md"
            fact_path.write_text("Verified fact from source/fact.txt.\n", encoding="utf-8")
            context_path.write_text("Noisy working context only.\n", encoding="utf-8")
            prompt_path.write_text("Return JSON.\n", encoding="utf-8")
            original_fact = fact_path.read_bytes()
            original = context_path.read_bytes()
            payloads: list[dict[str, Any]] = []

            def transport(
                endpoint: str,
                api_key: str,
                payload: dict[str, Any],
                timeout: float,
            ) -> dict[str, Any]:
                payloads.append(payload)
                return {
                    "model": "deepseek-v4-flash",
                    "choices": [
                        {
                            "message": {
                                "reasoning_content": "private reasoning must not escape",
                                "content": json.dumps(
                                    {
                                        "content": f"Formal answer {len(payloads)}",
                                        "supporting_information": [
                                            {
                                                "content": "Supported statement",
                                                "credibility": "medium",
                                                "basis": "inference",
                                                "sources": ["context source"],
                                                "analysis": "nested analysis must be discarded",
                                            }
                                        ],
                                        "logical_connections": [
                                            {
                                                "relation": "supports",
                                                "content": "A formal relation",
                                                "reasoning": "nested reasoning must be discarded",
                                            }
                                        ],
                                        "conflicts": [],
                                        "uncertainties": [],
                                        "analysis": "must be discarded",
                                    }
                                ),
                            }
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "prompt_cache_hit_tokens": 8,
                        "prompt_cache_miss_tokens": 2,
                        "completion_tokens": 3,
                        "total_tokens": 13,
                    },
                }

            first = context_agent.consult_context(
                fact_path=fact_path,
                context_path=context_path,
                system_prompt_path=prompt_path,
                question="first unique question",
                focus=None,
                api_key="secret",
                model="deepseek-v4-flash",
                base_url="https://api.deepseek.com",
                thinking="enabled",
                timeout=1,
                max_tokens=100,
                transport=transport,
            )
            second = context_agent.consult_context(
                fact_path=fact_path,
                context_path=context_path,
                system_prompt_path=prompt_path,
                question="second unique question",
                focus=None,
                api_key="secret",
                model="deepseek-v4-flash",
                base_url="https://api.deepseek.com",
                thinking="enabled",
                timeout=1,
                max_tokens=100,
                transport=transport,
            )

            first_wire = json.dumps(payloads[0])
            second_wire = json.dumps(payloads[1])
            self.assertIn("first unique question", first_wire)
            self.assertNotIn("first unique question", second_wire)
            self.assertIn("second unique question", second_wire)
            self.assertNotIn("Formal answer 1", second_wire)
            self.assertIn("<project_facts>", first_wire)
            self.assertIn("<working_context>", first_wire)
            self.assertEqual(fact_path.read_bytes(), original_fact)
            self.assertEqual(context_path.read_bytes(), original)
            self.assertNotIn("reasoning", json.dumps(first))
            self.assertNotIn("analysis", json.dumps(first))
            self.assertEqual(
                set(first),
                {
                    "content",
                    "supporting_information",
                    "logical_connections",
                    "conflicts",
                    "uncertainties",
                },
            )
            self.assertEqual(second["content"], "Formal answer 2")

    def test_http_transport_sends_expected_request(self) -> None:
        response_body = json.dumps({"choices": []}).encode("utf-8")

        class FakeResponse:
            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self) -> bytes:
                return response_body

        with patch.object(context_agent.urllib.request, "urlopen", return_value=FakeResponse()) as call:
            result = context_agent._http_post_json(
                "https://api.deepseek.com/chat/completions",
                "test-key",
                {"model": "deepseek-v4-flash"},
                3.0,
            )
        request = call.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(json.loads(request.data), {"model": "deepseek-v4-flash"})
        self.assertEqual(result, {"choices": []})

    def test_chat_endpoint_accepts_base_and_full_endpoint(self) -> None:
        expected = "https://api.deepseek.com/chat/completions"
        self.assertEqual(context_agent.chat_endpoint("https://api.deepseek.com/"), expected)
        self.assertEqual(context_agent.chat_endpoint(expected), expected)

    def test_budget_estimate_warns_and_rejects_conservative_limits(self) -> None:
        report = context_agent.request_budget(
            "system", "fact", "x" * 100, "question", None, 20,
            warn_tokens=100, hard_tokens=500
        )
        self.assertTrue(report["warning"])
        with self.assertRaises(context_agent.ContextAgentError):
            context_agent.request_budget(
                "system", "fact", "x" * 1000, "question", None, 20,
                warn_tokens=100, hard_tokens=500
            )

    def test_budget_command_does_not_call_api(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fact_path = Path(directory) / "fact.md"
            context_path = Path(directory) / "context.md"
            fact_path.write_text("A verified fact.", encoding="utf-8")
            context_path.write_text("A small context.", encoding="utf-8")
            args = context_agent.build_parser().parse_args(
                [
                    "budget",
                    "What is relevant?",
                    "--fact",
                    str(fact_path),
                    "--context",
                    str(context_path),
                ]
            )
            report = context_agent.run(args)
            self.assertEqual(report["reserved_output_tokens"], 1800)
            self.assertLess(report["estimated_total_tokens"], 600_000)

    def test_fact_or_context_may_be_absent_but_not_both(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fact_path = root / "fact.md"
            context_path = root / "context.md"

            fact_path.write_text("Fact with source: source/test.txt", encoding="utf-8")
            facts, context = context_agent.read_project_documents(fact_path, context_path)
            self.assertIn("source/test.txt", facts)
            self.assertEqual(context, "")

            fact_path.write_text("\n", encoding="utf-8")
            context_path.write_text("A working idea.", encoding="utf-8")
            facts, context = context_agent.read_project_documents(fact_path, context_path)
            self.assertEqual(facts, "")
            self.assertEqual(context, "A working idea.")

            context_path.write_text("\n", encoding="utf-8")
            with self.assertRaises(context_agent.ContextAgentError):
                context_agent.read_project_documents(fact_path, context_path)

    def test_invalid_utf8_is_reported_as_context_agent_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fact.md"
            path.write_bytes(b"\xff\xfe\xfa")
            with self.assertRaisesRegex(context_agent.ContextAgentError, "valid UTF-8"):
                context_agent.read_optional_document(path, "Fact file")

    def test_script_runs_by_absolute_path_from_external_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "types"],
                cwd=directory,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("negative-result", result.stdout)

    def test_invalid_cli_arguments_follow_json_error_contract(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "remember", "text", "--type", "invalid"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(set(json.loads(result.stderr)), {"error"})
        self.assertNotIn("usage:", result.stderr)

    def test_remember_writes_context_only_when_fact_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fact_path = root / "fact.md"
            context_path = root / "context.md"
            env_file = root / ".env"
            fact_path.write_text("Verified fact. Source: source.txt\n", encoding="utf-8")
            original_fact = fact_path.read_bytes()
            env_file.write_text(
                f'DEEPSEEK_FACT_FILE="{fact_path}"\n'
                f'DEEPSEEK_CONTEXT_FILE="{context_path}"\n',
                encoding="utf-8",
            )
            names = ("DEEPSEEK_FACT_FILE", "DEEPSEEK_CONTEXT_FILE")
            old_values = {name: os.environ.pop(name, None) for name in names}
            try:
                args = context_agent.build_parser().parse_args(
                    [
                        "remember",
                        "A rejected route.",
                        "--type",
                        "negative-result",
                        "--basis",
                        "direct",
                        "--source",
                        "experiment/test",
                        "--env-file",
                        str(env_file),
                    ]
                )
                context_agent.run(args)
                self.assertEqual(fact_path.read_bytes(), original_fact)
                self.assertIn("A rejected route.", context_path.read_text(encoding="utf-8"))
            finally:
                for name, old_value in old_values.items():
                    if old_value is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = old_value

    def test_remember_rejects_fact_and_context_as_the_same_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shared_path = root / "fact.md"
            env_file = root / ".env"
            original = "Verified fact. Source: source.txt\n"
            shared_path.write_text(original, encoding="utf-8")
            env_file.write_text(
                f'DEEPSEEK_FACT_FILE="{shared_path}"\n'
                f'DEEPSEEK_CONTEXT_FILE="{shared_path}"\n',
                encoding="utf-8",
            )
            names = ("DEEPSEEK_FACT_FILE", "DEEPSEEK_CONTEXT_FILE")
            old_values = {name: os.environ.pop(name, None) for name in names}
            try:
                args = context_agent.build_parser().parse_args(
                    [
                        "remember",
                        "An unverified idea.",
                        "--type",
                        "hypothesis",
                        "--basis",
                        "inference",
                        "--source",
                        "agent inference",
                        "--env-file",
                        str(env_file),
                    ]
                )
                with self.assertRaisesRegex(context_agent.ContextAgentError, "must be different"):
                    context_agent.run(args)
                self.assertEqual(shared_path.read_text(encoding="utf-8"), original)
            finally:
                for name, old_value in old_values.items():
                    if old_value is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = old_value

    def test_remember_rejects_invalid_existing_context_encoding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "context.md"
            original = b"\xff\xfeinvalid"
            path.write_bytes(original)
            with self.assertRaisesRegex(context_agent.ContextAgentError, "valid UTF-8"):
                context_agent.append_context(
                    path,
                    entry_type="hypothesis",
                    basis="inference",
                    sources=["agent inference"],
                    content="Do not append this.",
                    scope=None,
                )
            self.assertEqual(path.read_bytes(), original)

    def test_remember_rejects_unencodable_input_without_creating_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "remember",
                    "--type",
                    "caution",
                    "--basis",
                    "direct",
                    "--source",
                    "test",
                ],
                cwd=directory,
                input=b"\xff",
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(set(json.loads(result.stderr.decode("utf-8"))), {"error"})
            self.assertFalse((Path(directory) / "deepseek_context.md").exists())

    def test_env_context_path_is_loaded_before_remember(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            configured_context = root / "from-env.md"
            env_file = root / ".env"
            env_file.write_text(
                f'DEEPSEEK_CONTEXT_FILE="{configured_context}" # portable fallback\n',
                encoding="utf-8",
            )
            old_context = os.environ.pop("DEEPSEEK_CONTEXT_FILE", None)
            try:
                args = context_agent.build_parser().parse_args(
                    [
                        "remember",
                        "A bounded warning.",
                        "--type",
                        "caution",
                        "--basis",
                        "inference",
                        "--source",
                        "agent inference",
                        "--env-file",
                        str(env_file),
                    ]
                )
                context_agent.run(args)
                self.assertTrue(configured_context.is_file())
            finally:
                if old_context is None:
                    os.environ.pop("DEEPSEEK_CONTEXT_FILE", None)
                else:
                    os.environ["DEEPSEEK_CONTEXT_FILE"] = old_context


if __name__ == "__main__":
    unittest.main()
