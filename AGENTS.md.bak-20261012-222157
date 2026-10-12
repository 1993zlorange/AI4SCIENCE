# 通用科研项目根级 Agent 协同规则

本文件是科研项目模板的根级治理入口。`projectname` 是待替换的项目目录占位符；从模板建立真实项目时，应把配置中的 `projectname` 改为实际项目目录名，并保持同一项目只有一个有效映射。不得把开发者机器的绝对路径写入 Agent、Skill、脚本或项目文档。

根级规则与 `projectname/project/AGENTS.md` 共同生效：本文件负责项目监理、科研编排、证据门、成效归档和跨角色交接；工程级文件负责代码、数据、实验、测试与运行约束。任何局部规则都不得取消根级监督、证据、命名和人工决策要求。

## 1. 目录边界与唯一配置

```research-project
project_container = "projectname"
research_implementation_root = "projectname/project"
research_achievement_root = "projectname/achieve"
engineering_agents = "projectname/project/AGENTS.md"
```

```project-supervision
project_management_root = "projectname/achieve/00-项目管理"
requirements_dir = "requirements"
supervision_dir = "supervision"
logs_dir = "logs"
reflections_dir = "reflections"
changes_dir = "changes"
quality_dir = "quality"
costs_dir = "costs"
skills_dir = "skills"
tools_dir = "tools"
templates_dir = "templates"
engineering_root = "projectname/project"
project_skills_root = "projectname/project/.codex/skills"
scripts_root = "projectname/project/scripts"
programming_standard = "projectname/project/PROGRAMMING_STANDARDS.md"
feature_registry = "projectname/project/configs/features.yaml"
skill_promotion_registry = "projectname/project/configs/skill-promotion.yaml"
governance_validator = "projectname/project/scripts/f001_governance_validate.py"
evolution_review_days = 14
repeat_problem_threshold = 3
```

- `projectname/project` 只存科研实施材料：源代码、实验脚本、配置、测试、数据处理、环境定义、可复现运行记录及其直接产物。
- `projectname/achieve` 只存科研成效材料：成果卡、工作流交接书、人工决定、阶段报告、论文材料、审查材料、正式图表和项目管理记录。
- 成效文件通过项目相对路径引用工程证据；不得复制一份工程证据到成效目录后制造两个事实来源。
- 目录仅在首次产生对应具体产物时创建。不得为了“补齐结构”批量建立空目录，也不得移动、改名或合并既有目录。
- 现有 `.gitkeep` 或空目录视为历史/模板占位，不因本次治理自动删除；新目录必须先在需求记录中登记责任、用途、生命周期和首个具体产物。治理校验器只允许已登记根目录、含具体产物的目录或带 `.gitkeep` 的历史占位目录。

## 2. 每次项目操作的固定入口

所有项目相关操作，包括只读调查、科研规划、检索、设计、编码、数据处理、实验、分析、写作、测试、脚本、Skill、Git、发布和维护，均按下列顺序执行：

1. 调用全局 `pr-ps-00-project-supervisor`，由 `$pr-ps-00-project-supervision` 登记用户要求、范围、目标路径、权限、风险和验收方式。
2. 若任务属于科研推进，调用 `sr-research-project-lead` 判断阶段与下一步；若只是工程实现，在科研工作流和人工基线已经明确后调用相应工程 Agent。
3. 专业 Agent 先提交工作契约，再执行获准范围；涉及高成本、外部写入、科学结论或阶段门时停在人工检查点。
4. 专业 Agent 产出逐叶子成果卡和工作流交接书后，返回 `sr-research-project-lead` 执行交接验收。
5. 最后返回 `pr-ps-00-project-supervisor` 核对文件位置、命名、验证证据、日志、问题/反思、变更和成本记录后关闭本次操作。

项目监理不替代科研负责人，科研负责人不替代专业科研 Agent，任何 Agent 都不替代博士生或导师的科学判断。

## 3. 实际科研 Agent 与职责

| 实际 Agent 名称 | 角色 | 允许负责的工作流 |
| --- | --- | --- |
| `sr-research-project-lead` | 科研项目负责人 | RPL-01、RPL-02、RPL-03、RPL-04；不拥有 SR 叶子任务 |
| `sr-principal-investigator` | 首席研究员 | PI-E01、PI-X01、PI-P01 |
| `sr-method-builder` | 方法构建者 | MB-E01、MB-X01、MB-P01 |
| `sr-experimenter` | 实验员 | EX-E01、EX-X01、EX-P01 |
| `sr-critical-reviewer` | 批判性评审员 | CR-E01、CR-X01、CR-P01 |

同一工作流只能由其唯一主责 Agent 执行。批判性评审必须独立于被评审材料的生产者。专业 Agent 只能调用自己已配置的 SR 叶子 Skill，不得借交接名义越权完成其他角色的工作。

## 4. 科研项目负责人如何运行

`sr-research-project-lead` 有两种模式。

### 4.1 默认只读评估模式

用户仅要求“查看、评估、判断阶段、给出建议”时，负责人不得修改科研材料、启动实验或调用其他 Agent，必须依次执行：

1. `RPL-01`：遍历 `projectname/project` 和 `projectname/achieve`，盘点成果卡、交接书、工作契约、代码、配置、运行、数据、图表、报告和人工决定，报告断链、冲突和来源不明材料。
2. `RPL-02`：按最早未通过的关键依赖判断主阶段、并行次阶段、最后通过的 Gate、下一个受阻 Gate 及判断置信度。
3. `RPL-03`：只给一个 P0、最多两个 P1；每项写明目标 Agent、工作流、必要叶子 Skill、已验证输入、缺失前提、交付物、完成标准、人工检查点、停止条件和可直接使用的调用语句。

调用示例：

```text
先调用 pr-ps-00-project-supervisor 登记本次只读评估。然后调用 sr-research-project-lead，
以 projectname 为项目容器，projectname/project 为实施目录，projectname/achieve 为成效目录，
依次执行 RPL-01、RPL-02、RPL-03。只读，不调用其他 Agent；所有判断引用项目相对证据路径。
```

### 4.2 明确授权后的编排模式

只有用户明确要求“执行、派发、按建议推进”时，负责人才能调用专业 Agent。负责人必须：

1. 选择已批准的一个工作项，不把总体授权扩张为后续所有工作流的授权。
2. 仅发送已验证的最小输入、工作流编号、必要叶子 Skill 和上游交接。
3. 要求专业 Agent 先返回工作契约；未记录预算、停止条件和人工检查点时，不启动高成本或外部操作。
4. 专业 Agent 移交、暂停、阻塞或关闭后，立即执行 `RPL-04`，逐项核验成果卡、原始证据、交接字段和人工决定。
5. 只有验收改变了证据门状态，才重新运行 `RPL-01`、`RPL-02` 并更新 P0/P1；不得自动串行启动下一项昂贵工作。

调用示例：

```text
调用 sr-research-project-lead，按已批准的 P0 进入编排模式。
只调用指定的专业 Agent 和工作流，先返回工作契约，在约定人工检查点暂停；
收到交接后执行 RPL-04，不自动启动下一工作流。
```

## 5. 十二个专业科研工作流

以下“输出目录”均相对于 `projectname/achieve`。详细的逐项成果卡读取范围由各专业 Agent 的共享工作流契约决定；这里定义项目级路由和最低输入。

| 阶段 | 工作流 | 主责 Agent | 目标与最低输入 | 工作流交接目录 |
| --- | --- | --- | --- | --- |
| 探索 | `PI-E01` | `sr-principal-investigator` | 收敛问题、范围、价值、周期和 P0；读取既有周期决定与最新问题定义 | `08-项目推进与下一步计划/PI-E01/` |
| 探索 | `MB-E01` | `sr-method-builder` | 从文献证据形成假设、创新点、架构和模型蓝图；读取 PI-E01 与问题类成果卡 | `02-文献调研与领域结构/MB-E01/` |
| 探索 | `CR-E01` | `sr-critical-reviewer` | 独立挑战问题有效性、最近邻差异和机制反例；读取 PI-E01、MB-E01 及其证据 | `01-研究问题与选题/CR-E01/` |
| 探索 | `EX-E01` | `sr-experimenter` | 设计最小证伪、资源预算和失败回退；读取 PI-E01、MB-E01、CR-E01 | `05-实验设计与执行/EX-E01/` |
| 执行 | `MB-X01` | `sr-method-builder` | 冻结数据/实现契约、基线、模块、接口并处理阻塞；读取探索交接和 Gate F 决定 | `04-技术方案与方法设计/MB-X01/` |
| 执行 | `EX-X01` | `sr-experimenter` | 建立数据质控和正式实验矩阵并保留完整运行证据；读取 EX-E01、MB-X01 和 Gate F 决定 | `05-实验设计与执行/EX-X01/` |
| 执行 | `CR-X01` | `sr-critical-reviewer` | 审计结果完整性、泄漏、误差、归因和最小诊断；读取 MB-X01、EX-X01 | `06-结果分析与问题诊断/CR-X01/` |
| 执行 | `PI-X01` | `sr-principal-investigator` | 执行 Gate F、结果证据门、资源和路线决策；读取对应探索或执行阶段全部必要交接 | `08-项目推进与下一步计划/PI-X01/` |
| 表达 | `EX-P01` | `sr-experimenter` | 完成定量分析、切片、案例、机制证据和核心图；读取实验、审计与 PI-X01 决定 | `06-结果分析与问题诊断/EX-P01/` |
| 表达 | `MB-P01` | `sr-method-builder` | 根据冻结设计和真实运行记录撰写可复现方法与实验；读取实现、实验、审计和分析证据 | `07-论文与成果表达/MB-P01/` |
| 表达 | `PI-P01` | `sr-principal-investigator` | 收敛主张、叙事、修改、报告、开放和归档决定；读取 EX-P01、MB-P01，修改时读取 CR-P01 | `07-论文与成果表达/PI-P01/` |
| 表达 | `CR-P01` | `sr-critical-reviewer` | 对草稿执行独立同行评审和意见拆解；读取分析、方法写作和 PI-P01 草稿交接 | `07-论文与成果表达/CR-P01/` |

推荐依赖流如下；这是可回退的依赖图，不是必须一次跑完的流水线：

```text
PI-E01
  -> MB-E01 <-> CR-E01
  -> EX-E01
  -> PI-X01（Gate F）
  -> MB-X01 -> EX-X01 -> CR-X01
  -> PI-X01（结果证据门）
  -> EX-P01 + MB-P01
  -> PI-P01（草稿） -> CR-P01 -> PI-P01（修改/交付/归档）
  -> 下一周期 PI-E01
```

评审否定、实验失败或 Gate 未通过时，必须按交接退回责任工作流；不能跳过未通过的前置证据门，也不能用后期论文或图表倒推前期已经完成。

## 6. 如何调用专业科研 Agent

科研负责人派发时使用以下统一结构，不需要把一个工作流的所有叶子 Skill 机械跑完：

```text
调用 <实际 Agent 名称>，执行 <工作流编号>。
项目实施目录：projectname/project；项目成效目录：projectname/achieve。
目标：<本轮唯一目标>。
仅使用：<完成当前闭环所需的 SR 叶子 Skill>。
必须读取：<已验证成果卡路径>、<已验证交接书路径>。
先输出工作契约，记录 cards_read、handoffs_read、预期产物、人工检查点和停止条件；
每个关闭的叶子 Skill 独立输出成果卡，移交/暂停/阻塞/关闭时输出交接书；不得生成聚合工作流成果卡。
```

路由规则：方向、证据门、资源路线和最终主张交给首席研究员；文献、假设、模型、架构、实现契约和方法写作交给方法构建者；最小证伪、数据、实验、分析和图表交给实验员；问题挑战、完整性诊断和同行评审交给批判性评审员。

## 7. 工作契约、成果卡与交接书

专业 Agent 开始实质工作前，工作契约至少记录：项目相对根、工作流编号、叶子 Skill、单一目标、范围外事项、`cards_read`、`handoffs_read`、输入状态、预期产物、完成标准、人工检查点、停止条件和授权状态。缺失、断链、冲突或仅有旧式文件时必须如实记录，不得从对话补造。

每个实际调用且关闭的 SR-01 至 SR-68 叶子任务各自产出一张成果卡，不存在“一个工作流一张聚合成果卡”。成果卡必须包含 SR ID、Agent、工作流、状态、尝试、发现、证据定位、产物、结论、不能得出的结论、偏差、人工裁决和下一工作流。

工作流在控制权转移、暂停、阻塞或关闭时生成交接书。交接书必须列出读过和新产出的全部卡片，并逐项包含：尝试了什么、发现了什么、支持证据、当前局限性、产出了什么、下一步该做什么。接收者先验证路径和状态，再建立自己的工作契约。

## 8. 八类成效目录与命名

| SR 范围 | `projectname/achieve` 下的成效目录 |
| --- | --- |
| SR-01 至 SR-06 | `01-研究问题与选题/` |
| SR-07 至 SR-14 | `02-文献调研与领域结构/` |
| SR-15 至 SR-21 | `03-Idea科学假设与创新点/` |
| SR-22 至 SR-29 | `04-技术方案与方法设计/` |
| SR-30 至 SR-40 | `05-实验设计与执行/` |
| SR-41 至 SR-48 | `06-结果分析与问题诊断/` |
| SR-49 至 SR-58 | `07-论文与成果表达/` |
| SR-59 至 SR-68 | `08-项目推进与下一步计划/` |

若已有同一数字前缀但中文名称略有差异的目录，沿用已有目录，不创建语义重复目录。

- 所有管理类、技术类和科研文档使用 `YYYYMMDD-内容简述-文档类型.扩展名`。
- 成果卡使用 `YYYYMMDD-成果简称-成果卡.md`，SR ID 写入 frontmatter，不写进文件名前缀。
- 交接书使用 `YYYYMMDD-工作简述-交接书.md`；同日多次交接用不同的明确内容简述区分，不靠覆盖旧文件解决重名。
- 阶段报告、论文材料、审查记录、日志、反思、模板和 API 说明遵循同一日期规则。
- 代码文件、包、模块、类、函数、变量、常量和测试按工程编程规范命名。
- 旧式 `SR-NN-*`、`SR-NN_*` 或无日期文件仅作为历史证据候选；不得静默改名、覆盖或直接认定为合规新成果。
- 文档型 Skill 必须配中文结构化空白模板；模板只描述字段、章节、填写规则和验收标准，不出现具体项目事实或参考文档名称。
- 每个功能性文件必须能追溯到 `projectname/project/configs/features.yaml` 中的功能身份：`feature_id`（如 `F001`）、`feature_code`（大写稳定代码）和 `feature_name`（中文功能名）。代码文件、测试文件和脚本继续遵循语言/工具的可导入命名；功能编号、代码、功能三元组写入注册表、模块 docstring 或相邻契约，不以破坏 Python 导入规则为代价强行改名。
- 配置、脚本、测试和文档输出都必须在注册表中声明责任、实现路径、测试路径、状态和证据；新增功能先登记再实现。`scripts/f001_governance_validate.py` 是只读门禁，未通过不得关闭任务。

## 9. 三个阶段门与人工决定

| 阶段 | 必需工作流证据 | 通过条件 |
| --- | --- | --- |
| Explore | PI-E01、MB-E01、CR-E01、EX-E01 | 相关叶子任务真实关闭，设计边界清楚，并有博士生或导师的研究设计冻结决定 |
| Execute | MB-X01、EX-X01、CR-X01、PI-X01 | 运行完成或偏差已解释，完整性审计与主张边界明确，并有人工路线决定 |
| Express | EX-P01、MB-P01、PI-P01、CR-P01 | 分析、图表、写作和独立评审均可追溯，主张受证据约束，并有人工交付决定 |

以下事项始终需要博士生或导师决定：研究问题、范围、假设、创新点、数据纳入与许可/伦理、高成本资源、异常剔除、统计解释、机制与主张强度、合作与署名、投稿、专利、开源和公开发布。没有具名人工裁决的 `accepted` 只能按 `partial` 处理。

## 10. 与工程 `AGENTS.md` 的配合

在 `projectname/project` 内工作时，按顺序读取本根级文件和 `projectname/project/AGENTS.md`：

1. 根级文件决定项目监理、科研阶段、Agent 路由、成效目录、命名、交接和人工 Gate。
2. 工程级文件决定代码结构、数据边界、算法实现、测试、运行、脚本和编程规范。
3. 科研工作流先给出已批准的科学目标、输入契约和验收指标；工程 Agent 只能在该范围内实现，不得自行改变研究问题、实验设计或主张。
4. 工程实现和运行证据留在 `projectname/project`；专业科研 Agent 在 `projectname/achieve` 建成果卡和交接书并链接这些证据。
5. 若两个文件发生冲突，停止冲突分支，由项目监理记录问题，科研负责人判断科研影响，项目建立责任人决定目录或治理基线；不得静默选择。

## 11. 新项目启动与关闭

建立新项目时：先将 `projectname` 替换为实际项目目录名并复核两个配置块；确认工程 `AGENTS.md` 与编程规范可读；调用项目监理登记初始需求；再调用科研项目负责人执行 RPL-01 至 RPL-03。没有现有证据时应明确标记 `new_project`，通常从 PI-E01 开始，不得伪造历史成果卡。

任务只有在需求状态、实际产物、文件归属、命名、验证证据、成果卡/交接书、日志、问题/反思、变更、成本、限制和下一步均已如实记录后才能关闭。提交、推送、发布、删除、覆盖、凭据、付费服务、远程计算和外部系统写入必须另有明确授权。

## 12. Skill、脚本与进化规则

- 新 Skill 使用 `<代号>-<英文技能名称>`，并明确唯一责任、触发与非目标、输入输出、权限、失败边界、幂等、维护人和验证。
- 新 Skill 只在重复问题有证据、现有能力无法覆盖且人工批准后建立；凡生成文档，必须同步提供中文空白模板。
- 新脚本工具使用参数化相对路径，默认预览、拒绝覆盖、不隐式联网或提交，并同步生成 `YYYYMMDD-内容简述-API说明.md`。
- 用户每项要求进入需求记录；用户指出的问题和实际缺陷进入反思。达到 14 天评估周期或同类问题累计 3 次后，基于证据提出保留、优化、合并或淘汰 Skill/规则的建议，未经批准不得自动改变全局能力。
- 项目 Skill 晋升必须经过 `skill-promotion.yaml` 登记、项目试点、独立评审、安全扫描、人工批准、版本/哈希记录、全局安装计划和回滚证据；`f002_skill_promotion_audit.py` 只生成审查/安装计划，不自动修改全局 Skill。
- 日志除事实动作外，必须独立记录 `why`、`expected_impact`、`actual_impact`、`affected_requirements`、`affected_files`、`affected_downstream` 和 `decision_basis`；事实、推测和未执行项分栏记录，不得用“目标”代替“为什么”，不得用“结果”代替“影响”。

## 13. 固定技术文件名例外

代码入口、包初始化文件、配置入口和工具链强制文件可保留稳定名称（例如 `README.md`、`AGENTS.md`、`SKILL.md`、`pyproject.toml`、`PROGRAMMING_STANDARDS.md`、`docs/api.md`、`docs/architecture.md`、`__init__.py`）。该例外只覆盖文件名，不免除目录归属、中文正文、版本/变更记录、功能身份和验证要求；交付记录、阶段报告、日志、反思、成果卡和 API 说明仍必须日期化。
