# 研究项目模板

这是一个遵循 KISS 原则的人机协作研究模板。模板只规定必要的文件职责，不预建空的数据、脚本、图片或模块目录。

## 快速上手

1. 先整理需求：明确项目是什么、要做什么、交付什么以及什么时候停止，然后写入 `AGENTS.md` 的“项目概述”。
2. 按项目需要补充或修改 `AGENTS.md` 中要使用的 skill、工作流程和项目规范；不需要的内容不增加。
3. DeepSeek key 默认从 shell 环境变量读取；需要文件回退时，将根目录 `.env.example` 复制为 `.env` 并填写，`.env` 不提交。
4. 遇到需要人明确控制的内容，在对应位置放置 `manual.md` 并由人手动说明。只有确实需要全局与模块分层时，才拆分为根目录 `manual.md` 和 `modules/<模块>/manual.md`。
5. 让 agent 读取 `AGENTS.md`，先交流确认需求，再明确要求实现。其他上下文和工作流由 `AGENTS.md` 引导。
6. agent 到达停止条件或遇到需要人决定的问题时暂停并汇报。人验收接受后，agent 再更新 `docs_graph/agent_notes.md`；人补充或修改要求后，进入下一轮迭代。
7. 少量文字、格式或简单图示调整可走短路径：agent 直接完成并汇报，不强制进入 AutoReview、项目记忆、画像维护或 Git 分支流程。

**重要**:如果手动提交git要注意确定当前所处分支。完整任务中，Agent会在自身循环中创建自己的分支用于记录自身尝试，并只在用户通过时合入用户分支。

## 核心分工

- `AGENTS.md`：人维护的最高项目约束，记录工作流程和项目规范，agent 只读不改。
- `manual.md`：人维护的全文骨架，规定文章主线、章节顺序和跨模块关系。
- `modules/<模块>/manual.md`：人维护的模块内容。模块存在真实工作时再创建。
- `docs_graph/agent_notes.md`：agent 维护的项目进度、上下文入口、自动纠偏和用户画像（协作习惯）。
- `fact.md`：agent 自动维护的事实文件，只保存已核验、可追溯到明确来源的事实。
- `deepseek-context-agent/`：模板内置的项目级通用上下文 skill；通过 `consult` 查询、通过 `remember` 写入同目录的 `deepseek_context.md`，不保存查询历史。模板只提供空占位，不预置具体项目知识。
- 最终报告、检索记录、数据、脚本和图片：agent 执行并维护，人负责验收。

DeepSeek 上下文的读写统一由 skill 脚本完成：

```bash
# 明确保留一条工作上下文
python deepseek-context-agent/scripts/context_agent.py remember \
  --type hypothesis --basis inference --source "user discussion" \
  "待验证的思路"

# 查询现有上下文，不保存本次问题和回答
python deepseek-context-agent/scripts/context_agent.py consult "当前有哪些未验证假设？"
```

空占位文件不需要手工编辑；尚未写入任何记录时，`consult` 会明确提示先使用 `remember`。完整参数和记录类型见 `deepseek-context-agent/SKILL.md`。

## Git 记录

完整任务中，agent 会自动创建 `agent/<任务名>` 分支，用于保留探索和迭代记录。人工确认本轮结果后，agent 再将结果合入人工使用的分支。短路径任务不强制创建分支。

`fact.md` 和 `deepseek-context-agent/deepseek_context.md` 都是项目内容，随项目一起版本管理；包含 API key 的 `.env` 不提交。

## 推荐结构

```text
.
├── README.md
├── AGENTS.md
├── manual.md
├── fact.md
├── .env.example
├── deepseek-context-agent/
│   ├── SKILL.md
│   ├── deepseek_context.md
│   └── scripts/context_agent.py
├── docs_graph/
│   └── agent_notes.md
```

真实工作出现后再增加：

```text
modules/<模块>/manual.md   # 人写的模块内容
sources/                  # 原始论文、标准和来源记录
data/                     # 输入数据和生成表格
scripts/                  # 可复现命令和程序
figures/                  # 有来源或脚本的图片
writing/                  # 正式稿和编译产物
```

## 人工手稿用法

根目录 `manual.md` 只描述全文主线和模块关系。具体内容写入对应模块的 `manual.md`：

```text
modules/
├── background/manual.md
├── physical_model/manual.md
├── manufacturing/manual.md
└── comparison/manual.md
```

模块名按项目实际内容确定，不要求使用上面的示例。Agent 默认只读人工 `manual.md`；需要改动时必须由用户明确授权。

## 项目记忆

人工无需维护索引或关系图。Agent 根据 `AGENTS.md` 自动维护根目录
`fact.md`；只有实际出现值得跨任务保留的思路或尝试时，才通过模板内置
的 `$deepseek-context-agent` 向 `deepseek-context-agent/deepseek_context.md` 写入内容。
