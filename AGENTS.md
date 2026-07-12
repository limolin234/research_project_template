# workflow

本文件由人维护，规定项目工作流程和项目规范，agent 不修改。

## 项目维护

### 要使用的 skill

1. `docs-graph`：维护项目进度、上下文入口、项目风格和稳定的用户协作习惯。
2. `project_points`：维护可复用技术点、证据状态、假设和否定结果。
3. 论文 skill：检索和核验技术证据，优先使用相关领域期刊和原始论文，重要结论尽量多方验证。

### 文件交互规范

1. `AGENTS.md` 和各处 `manual.md` 完全由人维护，agent 只读。
2. `docs_graph/agent_notes.md` 记录已确认的项目进度、上下文入口和协作习惯。
3. 项目知识写入 `project_points/`；长内容放入对应项目文件，知识点只保存简短结论和来源指向。
4. 创建文件和目录时使用通用名称，按实际需要创建，不预建空结构。

#### Git 管理

1. 项目初始化时，agent 从用户当前分支创建 `agent/<任务名>` 分支，后续工作只在该分支进行。
2. 每轮 `HumanReview` 结束后，无论用户是否接受，都提交一次，保留完整迭代过程。
3. 每次提交前检查并按需更新 `.gitignore`，优先匹配生成物或临时文件的大类，不逐个添加文件名，也不排除应纳入版本管理的必要文件。
4. 用户未接受时，保留本轮提交并继续在 agent 分支修改。
5. 用户接受时，先更新 docs graph 和已确认的 project points，再提交并合入用户分支。

### 人机交流规范

1. 项目交流以完成任务为主，不使用多余的鼓励、表情或无关内容。
2. 用户说“先讨论”“先不改动”等表达时，只读取和讨论，不修改文件。
3. 涉及方向变化、不可逆操作或大量文件修改时，先停止并询问用户。
4. 方案复杂度明显超过实际需要时，按照 KISS 原则指出并简化。

## 工作状态机

初始状态为 `Start`。

### 状态

- `Start`
  - 读取 `AGENTS.md`、`docs_graph/agent_notes.md` 和相关 `manual.md`。
  - 创建并切换到 agent 分支。

- `Align`
  - 读取相关 `project_points`。
  - 根据已有用户习惯和项目风格与用户对齐需求、交付物和停止条件。
  - 本状态不更新 docs graph。

- `Working`
  - 根据人工文件和用户指令执行任务。
  - 涉及技术证据时使用论文 skill。
  - 使用 `project_points` 维护本轮产生的技术知识。

- `AutoReview`
  - 检查产物是否满足需求，验证实现和技术证据。
  - 可自行修复的问题返回 `Working`。
  - 审查中发现的错误同步到 `project_points`。

- `HumanReview`
  - 向用户汇报产物、验证结果和待确认问题。
  - 用户未接受时，不更新 docs graph，提交本轮结果后继续修改。
  - 用户接受时，使用 `docs-graph` 更新项目进度、项目风格和稳定的用户习惯，确认相关 project points，提交并合入用户分支。

- `End`
  - 项目达到停止条件或用户明确终止。

### 状态转移

```text
Start → Align
条件：项目上下文已经读取，agent 分支已经建立

Align → Working
条件：需求、交付物和停止条件已经确定，用户要求执行

Working → Align
条件：需求或人工约束需要重新确认

Working → AutoReview
条件：形成可审查的阶段产物

AutoReview → Working
条件：发现可由 agent 自行修复的问题

AutoReview → HumanReview
条件：自动审查完成，或问题需要用户决定

HumanReview → Working
条件：用户未接受，但需求不变

HumanReview → Align
条件：用户改变需求，或接受阶段成果后继续下一轮

HumanReview → End
条件：用户接受最终成果并达到停止条件，或用户明确终止
```

## 项目概述

待填写。
