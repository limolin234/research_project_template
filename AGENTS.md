# workflow

本文件由人维护，规定项目工作流程和项目规范，agent 不修改。

## 项目维护

### 要使用的 skill

1. `docs-graph`：维护项目进度、上下文入口、项目风格和稳定的用户协作习惯。
2. `$deepseek-context-agent`：模板内置于 `deepseek-context-agent/`，首次使用前读取其中的 `SKILL.md`；结合根目录 `fact.md` 与按需生成的 `deepseek_context.md` 整合相关信息、逻辑关系和可信度；思路、尝试、否定路线和其他噪声工作材料通过该 skill 写入 `deepseek_context.md`，查询记录不保存。
3. 各类论文skill：检索和核验技术证据，优先使用相关领域期刊和原始论文，重要结论尽量多方验证；没有可用的论文 skill 时，仍以原始论文和期刊来源为证据。

### 文件交互规范

1. `AGENTS.md` 和各处 `manual.md` 完全由人维护，agent 只读。
2. `docs_graph/agent_notes.md` 记录已确认的项目进度、上下文入口和协作习惯。
3. 根目录 `fact.md` 由 agent 自动维护，只记录已经核验且可追溯到明确来源的事实；思路、假设、尝试和未确认内容不得写入。`fact.md` 是项目资产，纳入版本管理。
4. `deepseek_context.md` 由 `$deepseek-context-agent` 在首次实际写入时创建，保存思路、尝试、否定路线和其他有用但噪声较高的工作材料；不得保存查询、回答或模型推理过程。创建后作为项目资产纳入版本管理。
5. 创建文件和目录时使用通用名称，按实际需要创建，不预建空结构。
6. 上下文压缩或会话恢复后，继续工作前重新读取 `AGENTS.md`、`docs_graph/agent_notes.md`、`fact.md` 和相关 `manual.md`，并按任务需要查询 `$deepseek-context-agent`。

#### Git 管理

完整任务使用以下 Git 路径；短路径任务按“工作状态机”的 `ShortPath` 处理。

1. 项目初始化时，agent 从用户当前分支创建 `agent/<任务名>` 分支，后续
工作只在该分支进行。
2. AutoReview 完成并修复后，agent 必须先在 `agent/<任务名>` 分支提交
本轮候选产物，再进入 HumanReview。
3. HumanReview 只决定候选产物是否接受、是否继续修改、是否合入用户分
支。
4. 用户未接受时，保留本轮提交，继续在 agent 分支追加修改。
5. 用户接受时，先更新 docs graph 并复核 `fact.md` 中本轮事实，再提交
确认状态并合入用户分支。
6. 每次提交前检查并按需更新 `.gitignore`，优先匹配生成物或临时文件的
大类，不逐个添加文件名，也不排除应纳入版本管理的必要文件。
7. agent 分支已存在时继续使用；合入用户分支后切回 agent 分支进行下一
轮。

### 人机交流规范

1. 项目交流以完成任务为主，不使用多余的鼓励、表情或无关内容。
2. 用户说“先讨论”“先不改动”等表达时，只读取和讨论，不修改文件。
3. 涉及方向变化、不可逆操作或大量文件修改时，先停止并询问用户。
4. 方案复杂度明显超过实际需要时，按照 KISS 原则指出并简化。
5. 简单、低风险、无新增项目知识的小改动优先走短路径，不强制触发
AutoReview、docs graph、项目记忆或 Git 分支维护。

## 工作状态机

初始状态为 `Start`。

### 状态

- `Start`
  - 读取 `AGENTS.md`、`docs_graph/agent_notes.md` 和相关 `manual.md`。
  - 不判断任务复杂度，不创建短路径；统一进入 `Align`。

- `Align`
  - 读取相关 `fact.md`，并按任务需要查询 `$deepseek-context-agent`。
  - 根据已有用户习惯和项目风格与用户对齐需求、交付物和停止条件。
  - 判断任务走 `ShortPath` 还是完整 `Working` 路径。
  - 本状态不更新 docs graph。

- `ShortPath`
  - 适用于少量文字、格式、轻微图示调整、简单查询或用户明确要求快速处理的任务。
  - 不创建或切换 agent 分支，不执行 AutoReview；没有新增事实或工作材料时不更新项目记忆。
  - 完成后进入 `HumanReview` 给用户确认；如果过程中发现任务变复杂，转入 `Working`。

- `Working`
  - 根据人工文件和用户指令执行任务。
  - 完整路径下，agent 分支不存在时从用户当前分支创建；已存在时直接切换。
  - 涉及技术证据时优先使用论文 skill；不可用时回退到原始论文和期刊来源。
  - 已核验且来源明确的事实写入 `fact.md`。
  - 思路、尝试、否定路线和其他需要保留的工作材料通过 `$deepseek-context-agent` 写入 `deepseek_context.md`。

- `AutoReview`
  - 使用没有实现上下文的独立 agent 严格审查产物，验证实现、技术证据和项目要求是否一致。
  - 独立 agent 不继承实现过程或主 agent 推理，只接收项目规则、任务需求、待审产物和必要证据。
  - 主 agent 阅读审查结果并决定后续状态。
  - 可自行修复的问题返回 `Working`。
  - 审查中确认的事实修正同步到 `fact.md`；值得保留的失败原因或否定路线写入 `deepseek_context.md`。

- `HumanReview`
  - 向用户汇报产物、验证结果和待确认问题。
  - 用户未接受时，不更新 docs graph，提交本轮结果后继续修改。
  - 用户接受时，使用 `docs-graph` 更新项目进度、项目风格和稳定的用户习惯，复核相关事实，提交并合入用户分支。

### 状态转移

```text
Start → Align
条件：项目上下文已经读取

Align → ShortPath
条件：任务简单低风险，不产生需要沉淀的项目知识或复杂审查需求

ShortPath → HumanReview
条件：短任务产物已完成，需要用户确认

ShortPath → Working
条件：短任务过程中发现需求、证据或改动范围超出简单处理

Align → Working
条件：完整任务的需求、交付物和停止条件已经确定，用户要求执行

Working → Align
条件：需求或人工约束需要重新确认

Working → AutoReview
条件：形成可审查的阶段产物

AutoReview → Working
条件：发现可由 agent 自行修复的问题

AutoReview → HumanReview
条件：自动审查完成，或问题需要用户决定

HumanReview → Working
条件：用户未接受，且修改已超出短路径

HumanReview → Align
条件：用户改变需求，或接受阶段成果后继续下一轮

HumanReview → ShortPath
条件：用户只要求少量快速修改
```

## 项目概述

待填写。
