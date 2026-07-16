# 研究项目模板

这是一个遵循 KISS 原则的人机协作研究模板。模板只规定必要的文件职责，不预建空的数据、脚本、图片或模块目录。

## 快速上手

1. 先整理需求：明确项目是什么、要做什么、交付什么以及什么时候停止，然后写入 `AGENTS.md` 的“项目概述”。
2. 按项目需要补充或修改 `AGENTS.md` 中要使用的 skill、工作流程和项目规范；不需要的内容不增加。
3. 遇到需要人明确控制的内容，在对应位置放置 `manual.md` 并由人手动说明。只有确实需要全局与模块分层时，才拆分为根目录 `manual.md` 和 `modules/<模块>/manual.md`。
4. 让 agent 读取 `AGENTS.md`，先交流确认需求，再明确要求实现。其他上下文和工作流由 `AGENTS.md` 引导。
5. agent 到达停止条件或遇到需要人决定的问题时暂停并汇报。人验收接受后，agent 再更新 `docs_graph/agent_notes.md`；人补充或修改要求后，进入下一轮迭代。

**重要**:如果手动提交git要注意确定当前所处分支，Agent会在自身循环中创建自己的分支用于记录自身尝试并在只在用户通过时合入用户分支

## 核心分工

- `AGENTS.md`：人维护的最高项目约束，记录工作流程和项目规范，agent 只读不改。
- `manual.md`：人维护的全文骨架，规定文章主线、章节顺序和跨模块关系。
- `modules/<模块>/manual.md`：人维护的模块内容。模块存在真实工作时再创建。
- `docs_graph/agent_notes.md`：agent 维护的项目进度、上下文入口、自动纠偏和用户画像（协作习惯）。
- `project_points/`：agent 自动维护的项目笔记与关系图，保存短技术点、证据状态、模型假设、否定结果和决策关系。人工只需保留该路径，无需手动操作。
- 最终报告、检索记录、数据、脚本和图片：agent 执行并维护，人负责验收。

## Git 记录

agent 会自动创建 `agent/<任务名>` 分支，用于保留探索和迭代记录。人工确认本轮结果后，agent 再将结果合入人工使用的分支。

## 推荐结构

```text
.
├── README.md
├── AGENTS.md
├── manual.md
├── docs_graph/
│   └── agent_notes.md
└── project_points/
    ├── README.md
    ├── skill.md
    ├── graph.py
    ├── nodes.jsonl
    ├── edges.jsonl
    └── index/
        └── README.md
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

## Project Points

人工无需学习或执行 `project_points` 命令。保留 `project_points/` 目录即可，agent 会根据 `AGENTS.md` 自动检索和维护其中的技术点与证据状态。
