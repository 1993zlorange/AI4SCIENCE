# 模板工程 Agent 协同规则

## 0. 根级科研治理协同

本目录是科研实施目录，不是独立项目容器。开始任何工作前，必须先读取上两级根目录的 `AGENTS.md`，再读取本文件；保持本模板目录结构时，相对路径为 `../../AGENTS.md`。根级文件是项目监理、科研 Agent 路由、十二个科研工作流、证据门、成效归档和人工决定的唯一治理来源，本文件只细化工程实施。

项目目录边界如下：

```research-project
project_container = ".."
research_implementation_root = "."
research_achievement_root = "../achieve"
root_agents = "../../AGENTS.md"
```

- 本目录保存源代码、数据处理、实验脚本、配置、测试、环境定义、可复现运行记录和直接运行产物。
- 科研成果卡、工作流交接书、人工决定、阶段报告、论文材料、审查材料和正式成效统一写入 `../achieve`，不得在本目录另建第二套成效体系。
- 工程证据保留在本目录，由成效文件使用项目相对路径引用；不得复制证据后制造两个事实来源。
- 项目监理始终使用根级 `AGENTS.md` 中唯一的 `project-supervision` 配置。不得在本文件重定义监理根目录，以免日志和成效分裂。

开始工作先由项目监督能力核对已授权目标、文件归属和完成条件；普通小修可直接在已有范围执行，不强制新增角色和整套记录。科研负责人维护唯一已批准性能队列；工程 Agent 仅实现既定目标，不改研究问题、实验设计或主张。同一批次的剩余单元、必要工程修复、恢复、汇总与复核连续执行，不因换角色、叶技能结束、工具等待或科学接受待确认反复停止。只在实际资源/权限/科学条件改变处暂停相关分支。

记录类文件执行根级同日同类型唯一规则，类型/别名/固定主体/目录来自 `configs/features.yaml` 的 `record_policy`；任务、Agent、阶段和格式不得拆分。每条使用稳定entry_id、实际带时区记录时间、来源和独立状态，修订保留原身份。从2026-10-30起只生成需求与重要科研日志日文件；取消默认科研成果卡/契约/交接及监督/变更/反思/质量/成本独立过程稿。范围决定写需求、结果在实际专题正文、接续在已有run状态；原始证据、独立评审与人工决定原件保留。正式报告和API等实体文档按对象持续维护，源码/配置/固定输入/原始run不强行并入日记。新功能先在features登记责任、实现/测试与状态；新文档型Skill仍需中文空白模板，新脚本维护API说明。

固定技术入口（如 `README.md`、`AGENTS.md`、`SKILL.md`、`pyproject.toml`、`PROGRAMMING_STANDARDS.md`、`docs/api.md`、`docs/architecture.md`、`__init__.py`）允许保留稳定名称；该例外不免除归属、中文正文、变更记录、功能身份和验证要求。新目录仅在具体产物需要时创建；已有 `.gitkeep` 占位不自动删除。

# 编码 Agent 说明

本文件适用于在此模板项目中工作的所有编码代理。开始任何修改前必须完整阅读 [PROGRAMMING_STANDARDS.md](PROGRAMMING_STANDARDS.md)，并以它作为第一项目级编程规范。明确的当前用户范围、安全要求和已批准架构高于局部代码习惯；发现冲突时停止冲突分支并说明，不得静默选择。

## 1. 开始工作前

依次完成：

1. 阅读 `PROGRAMMING_STANDARDS.md`、`README.md`、`pyproject.toml`。
2. 阅读与任务相关的 `docs/architecture.md`、`docs/api.md`、`docs/algorithms/` 和 ADR。
3. 检查相关源文件、公开导出、测试、配置和运行入口；不要只根据文件名推断实现。
4. 写下本次范围、可观察成功/失败行为、涉及的公共接口、目标文件、测试和明确不做事项。
5. 检查工作区已有修改并保留用户内容；禁止为了方便回退或覆盖无关文件。
6. 读取并更新 `configs/features.yaml`；若新增功能没有稳定编号、代码、中文功能名和测试映射，先登记再编码。

本模板包含许多空白文件。空白只表示预留的责任位置，不表示每项任务都要填写它们。只修改完成当前需求所必需的文件。

## 2. 文件选择规则

| 要实现的内容       | 写入位置                                                 | 同步检查                                                    |
| ------------------ | -------------------------------------------------------- | ----------------------------------------------------------- |
| 新算法             | `src/ai_project/algorithms/<domain>/<name>/algorithm.py` | 同目录 `config.py`、registry、contract/unit tests、算法文档 |
| 训练/评估/推理流程 | `src/ai_project/application`                             | 端口、错误、集成测试、公共 API                              |
| 数据格式和加载     | `src/ai_project/data`                                    | schema、许可/溯源、无效输入测试                             |
| 指标               | `src/ai_project/evaluation/metrics.py`                   | 单位、聚合定义、数值容差测试                                |
| 评估摘要/表格      | `src/ai_project/evaluation/reports.py`                   | result schema、plot 消费契约                                |
| 画图               | `src/ai_project/visualization`                           | FigureSpec 单测、渲染/重载集成测试                          |
| 日志和运行事件     | `src/ai_project/tracking`                                | 脱敏、run_id、adapter contract tests                        |
| manifest/产物存储  | `src/ai_project/artifacts`                               | 原子写、哈希、路径安全、恢复测试                            |
| Python 公共调用    | `src/ai_project/api.py` 和包级导出                       | API 文档、示例、兼容测试                                    |
| CLI                | `src/ai_project/cli`                                     | application 复用、退出码、stdout/stderr E2E                 |
| HTTP               | `src/ai_project/server`                                  | 真实需求、schema/OpenAPI、错误/鉴权 E2E                     |
| 性能测试           | `benchmarks`                                             | 固定环境说明；不得混入正确性测试                            |
| 开发/发布/迁移工具 | `scripts`                                                | 不得成为产品功能的唯一入口                                  |

不要新建通用 `utils.py`、`helpers.py`、`common.py`、万能 service/repository 或第二套训练入口。找不到位置通常意味着职责尚未说清，先澄清责任而不是创建杂物目录。

## 3. 新算法的填写顺序

新增算法时按以下顺序工作：

1. 在 `docs/algorithms/<algorithm_id>.md` 记录问题、输入/输出、公式来源、单位、随机性、支持设备、限制和验收指标。
2. 在算法目录 `config.py` 定义类型化严格配置；禁止把 CLI namespace 或全局 Settings 传入算法。
3. 在 `algorithm.py` 实现 `Algorithm` 契约。算法不得解析入口、决定输出根、直接画图或依赖具体 tracker/store。
4. 在 `algorithms/registry.py` 显式注册稳定 ID 和版本；重复 ID 必须失败，禁止 import side effect 注册。
5. 如需完整工作流，在 `application/train.py`、`evaluate.py` 或 `predict.py` 编排数据、算法、Reporter、ArtifactWriter 和终态。
6. 指标进入 `evaluation`；画图只从结构化结果生成 `FigureSpec`，不得读取算法私有成员。
7. Python、CLI、HTTP 和示例调用同一个 application/API 用例，不能复制训练循环。
8. 先写最小 CPU unit/contract tests，再按真实边界补 integration/E2E/benchmark。
9. 更新公共导出、README/API 文档、示例和 CHANGELOG；未实现的入口不得出现在可复制快速开始中。

## 4. 其他常见任务

### 数据与 schema

- 原始输入在 `data` 边界严格校验并转换为类型化对象。
- 新增跨进程/持久化格式时在 `schemas.py` 定义版本和兼容策略。
- fixture 只放 `tests/regression/fixtures`，必须小、许可清晰、无敏感数据。
- 不把真实数据、下载缓存或生成模型提交到仓库。

### 日志与产物

- 正确性、边界和必要回归检查属于内部质量保障，只保存必要工程证据，不单独生成用户正确性结论、科研成果卡或科研日志。影响性能有效性的缺陷在对应性能条目说明。
- 科研日志从2026-10-30起使用group-meeting/1.0逐条契约，按研究问题、actions、result、interpretation、limitations和next_step讲述；有research_point/source、guide_questions及evidence。工作类型限定literature/method/performance/analysis/writing/research_blocker，性能及分析另含comparison_conditions与metrics。完整字段与题号范围遵根规则；旧条目兼容，新条目不能省略契约绕开。正文不含工程/管理附录。
- 获准历史提炼视图按event_date展示、compiled_at标记真实整理时间，精确登记且只读，不能伪造旧记录时间或追加新工作。
- 仅需求与重要科研日志有真实内容时创建；同一天同类型由一个写入者追加，不每日补齐、不按任务拆分，冲突重读合并。旧过程日文件只读兼容，不追加新取消类型条目。

- 算法通过 `Reporter` 和 `ArtifactWriter` 端口报告，不直接打开全局日志或拼运行路径。
- 所有事件、指标、模型、表格和图表使用同一 `run_id`。
- 重要写入使用临时文件、校验和原子替换；失败/取消/中断也必须保留真实终态。
- 长任务保存唯一执行者、逐单元终态和断点，恢复核对输入/代码/配置并跳过已完成单元。总时限、单次选择限、节点/评价次数及仿真期限分开配置；工具等待超时不等于运行终止。
- 测试使用内存实现或临时目录，不写 `var/runs` 和用户目录。

### 画图

- 先实现并测试 `ResultBundle -> FigureSpec`，再实现具体 Matplotlib/Plotly 渲染器。
- 图表必须能从保存结果重新生成，不触发数据下载或训练。
- Web 需要图表时消费版本化 spec/表格，不在前端复制指标算法。

### CLI 与 HTTP

- 入口是 composition root：选择真实 adapter 后调用 application。
- CLI 日志到 stderr，机器 JSON 到 stdout；错误码和退出码保持稳定。
- 不因模板已有 `server/` 就默认实现 HTTP。只有明确调用方和安全边界后才启用。
- 变更 HTTP/server 契约时同步 schema、API 文档和 contract/E2E tests。

## 5. 编码要求

- 严格执行 `PROGRAMMING_STANDARDS.md` 的命名、依赖、类型、异常、I/O、安全和文档规则。
- 保持函数职责单一；I/O、计算和呈现分开；优先纯函数和组合。
- 公共 API 使用完整类型和稳定错误，禁止无说明 `Any`、可变默认参数和含糊 bool flag。
- 只捕获能够处理或转换的异常；不得吞错、伪造成功或在日志中泄密。
- 注释说明原因、不变量和来源，不叙述语法；不保留无 owner/issue 的 TODO。
- 不引入新框架、数据库、队列、服务、插件系统或网络依赖，除非需求明确且 ADR 已批准。

## 6. 测试与验证

测试行为而不是实现文本。新功能按风险覆盖正常、边界、无效输入、依赖失败、取消、恢复和兼容；缺陷修复先保留能复现根因的回归测试。

先运行与变更风险相称的相关测试；影响包级行为或公共契约时再运行全套。以下是开发工具命令，按需执行，不机械安装/联网或重复无关检查：

```bash
uv sync --all-groups
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest
```

CI/只读验证使用 `ruff format --check`，不得自动修复后把未审阅修改当作验证结果。GPU、联网、下载、凭据、付费或远程测试必须显式标记和授权；未运行就如实报告。

## 7. 完成条件

交付前逐项确认：

- 修改满足当前需求，没有填充无关空白文件或增加推测功能。
- 文件位置和依赖方向符合编程规范。
- 测试、CLI、HTTP、Notebook、画图没有各自复制算法流程。
- 公共类型、schema、错误、状态、随机性、单位和副作用有文档与测试。
- 运行结果按 `run_id` 可追溯，路径、日志、反序列化和密钥处理安全。
- 格式、lint、类型和适用测试在最终文件状态通过；不能运行的项目已明确说明。
- 用户可见行为、公共接口或使用方式变化已同步 README/docs/examples/CHANGELOG。
- 没有调试输出、机器路径、密钥、未经许可数据、无界任务或大范围 ignore。
- 已运行 `scripts/f001_governance_validate.py --project-root . --check`；涉及Skill晋升时再运行F002。必要结果保存在已有内部证据和run状态，范围决定写需求；不为验收另建成果卡/契约/交接/监督/质量/成本等过程文档。


组会要点在可见正文中必须写出具体问题，不能只显示4.4.Q10一类编号。编号保留在机器元数据便于核对，生成器按group-meeting-questions.json展开。面向领导和导师，用完整句说明做了什么、结果说明什么、还有什么不足、接下来做什么；首次解释必要术语，禁止未解释的A/B/C、S0/S1、宏、固定流、待决等简称。保留所有必要数字、条件、负结果和结论边界，不能把改写写成新实验。

历史需求视图使用research-requirement-history/1.0及historical_readonly，event_date标明核实事件日、compiled_at标明真实整理时间，精确登记且不可追加；不伪造旧recorded_at/daily-entry。精简不取消适用测试、科学质量与独立评审，只停止重复成稿。


## 工程文档按对象维护

docs仅保存当前代码的使用与维护说明：README导航、architecture实际结构、api接口导航，以及interfaces、commands、algorithms、adr。相同模块、脚本组或文件格式维护唯一当前正文，使用稳定对象名，日期与适用版本放元数据，不因修复或每次运行新增日期API文档。简单脚本优先--help及必要注释，相关脚本共用运行指南；复杂独立工具确需说明时维护一份对象文档。文档必须讲输入输出、错误、限制及真实命令，不能以目录模板补造未实现能力。

工作契约、工程交付/复验、检查成绩、修订流水、补丁和源码快照不进入docs，必要原始证据留既有run。旧的“每个新脚本新增日期API说明”要求由本节替代；这是维护现行说明，不取消必要用法文档。科研结果、图表解释和主张归achieve并引用唯一原始来源。架构决定按实际决定对象保留，不为普通修复或文件整理另写ADR。

迁移前检查当前代码、配置、命令及历史来源绑定；被封存运行绑定的原件不得覆盖、改指纹或改写旧manifest。保留原路径只读例外须逐文件登记原SHA与用途并在导航标明非现行稿，其余旧件移出日常docs。归并先提取有效字段、边界及运行语义，过程部分原件保全。文档唯一性按对象/适用版本判断，不把不同模块同日的合法文档并成一个日文件。新目录有实际文档才建，工程检查不进入科研日志。
