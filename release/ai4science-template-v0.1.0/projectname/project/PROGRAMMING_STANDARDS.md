# Python AI 项目编程规范

| 项目           | 内容                                                     |
| -------------- | -------------------------------------------------------- |
| 状态           | 项目强制基线；采用模板后由维护者批准版本                 |
| 适用范围       | `src`、`tests`、`benchmarks`、入口、配置、脚本和技术文档 |
| 主要语言       | Python 3.12+                                             |
| 格式与静态检查 | Ruff、mypy strict、pytest                                |

规范关键词：**必须**、**禁止**是合并门禁；**应**是默认做法，偏离时必须在 PR 中说明；**可**表示按实际需要选择。

## 1. 优先级与例外

在安全规则和明确的当前需求之后，本文件是项目内编程工作的第一规范。架构文档决定模块边界，已有实现提供局部风格，但不能覆盖本规范中的强制条款。

规范冲突时按以下顺序处理：

1. 安全、法律、许可证和明确的当前用户需求；
2. 本编程规范；
3. 已批准的架构、接口 schema 和 ADR；
4. 已有代码的局部惯例。

确需例外时，必须缩小到最小范围，在代码附近说明原因，在 PR 中记录影响和替代方案；长期例外必须建立 issue 或 ADR。禁止通过文件级 `noqa`、关闭 strict 模式或删除测试掩盖问题。

## 2. 基线

- Python 最低版本为 3.12；文件使用 UTF-8、4 空格缩进和 LF/工具统一换行。
- 使用 `src/` layout；所有 Python 包目录包含 `__init__.py`。
- 依赖只在 `pyproject.toml` 声明，锁文件由 `uv lock` 生成，禁止手改生成的锁内容。
- 行宽目标 100；URL、哈希和无法合理拆分的机器字符串可例外。
- 禁止提交虚拟环境、缓存、构建结果、运行产物、真实数据、模型权重、密钥和本机绝对路径。
- 格式、lint、类型和测试规则由 `pyproject.toml` 统一配置，CI 不得维护第二套冲突命令。

## 3. 架构和依赖

允许的主要依赖方向：

```text
api/cli/server -> application -> algorithms/evaluation/contracts/schemas
tracking/artifacts adapters -> contracts/schemas
visualization -> schemas and persisted result data
algorithms -> Python standard library and approved numerical frameworks
```

强制规则：

- `algorithms` 禁止导入 `cli`、`server`、`visualization`、具体 tracker 或具体 artifact store。
- `application` 禁止接收 HTTP request、CLI namespace 或返回框架 response。
- `cli`/`server` 只做协议解析、用例调用、错误映射和呈现，不实现训练循环或指标公式。
- `visualization` 只消费版本化结果、指标和表格，不读取算法私有成员，不触发训练。
- Notebook 和 `examples` 必须从公开 API 导入，禁止成为权威实现。
- 不建立笼统的 `utils.py`、`helpers.py` 或 `Manager`；代码进入有明确所有者的模块。
- 只有真实存在多个实现、外部依赖易变或需要测试替身时才增加 `Protocol`。
- 禁止通过 import side effect 自动注册算法；使用显式 registry，并在重复 ID 时失败。

## 4. 文件放置

| 内容                   | 位置                                                     |
| ---------------------- | -------------------------------------------------------- |
| 算法数学/训练行为      | `src/ai_project/algorithms/<domain>/<name>/algorithm.py` |
| 算法配置和校验         | 同算法目录的 `config.py`                                 |
| 训练/评估/推理编排     | `src/ai_project/application`                             |
| 数据契约、加载和纯变换 | `src/ai_project/data`                                    |
| 指标计算               | `src/ai_project/evaluation`                              |
| 图表 spec 和渲染器     | `src/ai_project/visualization`                           |
| 日志与运行事件适配器   | `src/ai_project/tracking`                                |
| manifest 和产物存储    | `src/ai_project/artifacts`                               |
| CLI/HTTP 协议          | `src/ai_project/cli`、`src/ai_project/server`            |
| 正确性测试             | `tests` 对应层级                                         |
| 性能测量               | `benchmarks`                                             |
| 用户示例/探索          | `examples`、`notebooks`                                  |
| 架构/API/算法/ADR      | `docs` 对应目录                                          |
| 本地运行数据           | `var/runs`，不提交 Git                                   |

空白文件不是必须填充的任务清单。只有需求需要该边界时才写入实现；不为“完成目录”添加无调用方的抽象或占位逻辑。

## 5. 命名与导入

| 对象       | 规则                              | 示例                                       |
| ---------- | --------------------------------- | ------------------------------------------ |
| 包、模块   | `snake_case`，使用明确名词        | `run_manifest.py`                          |
| 类、异常   | `PascalCase`，异常以 `Error` 结尾 | `InvalidDataError`                         |
| 函数、变量 | `snake_case`，函数用动词          | `load_run`                                 |
| 常量       | `UPPER_SNAKE_CASE`                | `MAX_BATCH_SIZE`                           |
| Protocol   | 描述能力                          | `Reporter`、`ArtifactWriter`               |
| 布尔值     | `is_`、`has_`、`can_`、`should_`  | `is_cancelled`                             |
| 测试       | `test_<行为>_<条件>_<结果>`       | `test_fit_empty_batch_raises_invalid_data` |

- 代码标识符使用英文；用户可见文字使用项目选定语言。
- 避免含糊缩写和跨多行逻辑中的 `data`、`info`、`item`、`obj`、`tmp`。
- 数学代码可在小作用域使用论文中的标准符号，但必须引用来源；公共接口仍使用描述性名称。
- 优先绝对导入；禁止 `import *`，禁止修改 `sys.path` 解决包结构问题。
- `__init__.py` 只通过 `__all__` 重导出稳定公共 API，禁止 I/O、注册或对象初始化。
- 仅类型检查需要且会造成循环时使用 `TYPE_CHECKING`；其他循环依赖必须修正边界。

## 6. 函数、类型和状态

- 公共 API、Protocol、DTO、算法入口和复杂内部函数必须有完整类型标注。
- mypy 使用 strict；禁止无说明的 `Any`。不可信第三方对象在 adapter 边界立即校验和收窄。
- 使用 `X | None` 显式表达可空；集合无结果返回空集合，单资源无结果才返回 `None`。
- 参数超过 5 个时，应评估是否需要不可变配置/请求对象；禁止把整个 Settings 传给只需要一个字段的函数。
- 禁止可变默认参数；不使用多个布尔 flag 驱动互不相同的工作流。
- 多个相关返回值使用命名 dataclass/DTO，不返回难以理解的 tuple 或“成功 bool + 错误字符串”。
- 领域值默认使用 `@dataclass(frozen=True, slots=True)`；时间必须是 timezone-aware UTC。
- 单位进入字段名或相邻单位字段；禁止裸物理量跨边界。JSON 中禁止 NaN 和 Infinity。
- 时间、ID、随机数、文件、网络和持久化从边界注入；禁止算法深处读取环境变量或用户目录。
- 函数应完成一个可命名动作。超过约 40 行有效逻辑时评估拆分，但禁止为行数制造无意义包装。
- 优先纯函数和组合，其次是窄 Protocol；继承只用于稳定的 is-a 关系。

## 7. 算法契约

每个可注册算法必须声明稳定 `id`、语义版本、配置 schema、输入/输出类型和支持能力，并实现项目批准的 `Algorithm` 契约。

- `fit`/`predict` 不解析 CLI 或 HTTP，不选择全局输出路径。
- 训练配置与数据分开传入；构造函数不得接收训练数据或执行训练。
- 进度和指标通过注入的 `Reporter` 上报；检查点通过 `ArtifactWriter` 写入。
- 返回结构化 `TrainResult`；调用方不得依赖算法的 `_private` 状态。
- `fit` 的重复调用、warm start、随机性、设备差异、输入修改和输出顺序语义必须有文档与测试。
- 不支持的 dtype、shape、空数据、NaN/Inf 和取消必须给出稳定错误。
- 新算法必须加入显式 registry，并通过所有算法共享的 contract test。
- 算法公式、变量、单位、适用区间和论文/标准来源必须写入算法文档或关键 docstring。

## 8. Run、文件和画图

- 每次运行先获得不可复用的 `run_id`，先原子创建 `running` manifest，再写产物，最后原子替换终态。
- manifest 至少记录 schema 版本、状态、算法/代码/环境版本、数据引用、配置、种子、时间和产物 SHA-256。
- 重要文件采用临时文件、校验、必要时 flush/fsync、原子替换；不能让部分写入看起来成功。
- 进程崩溃后未完成 run 标记为 `interrupted`；不得默认重做可能已有外部副作用的操作。
- 路径必须 resolve 后确认仍在允许根目录；归档解压必须防路径穿越、压缩炸弹和总大小失控。
- 大文件流式处理；禁止无界 `read_bytes()`、结果集合或内存缓存。
- 不反序列化不可信 pickle；NumPy 读取外部 NPZ 时禁止 object pickle。
- 图表生成分为 `ResultBundle -> FigureSpec -> renderer`；测试分别覆盖数据 spec、文件可打开和关键视觉回归。
- `plots` 是可重建派生产物；原始指标、manifest 和最终模型的删除必须是显式操作。

## 9. 日志、配置和密钥

- 使用模块级 logger；消息短且稳定，动态值放结构化字段。
- 每次运行在 `var/runs/<YYYYMMDD>/<run_id>/logs/events.jsonl` 写入 UTF-8 JSON Lines 结构化事件；每行恰有一个 JSON 对象，字段契约见 `docs/20260913-工程运行日志-模板.md`。可选的人类可读日志只能同目录保存，不能代替 `events.jsonl`。
- 每条结构化事件至少含 `timestamp`（含时区的 ISO 8601 时间）、`level`、`service`、`run_id` 和 `event`；动态值放 `fields` 对象。`event` 使用稳定的 `lowercase_underscore` 名称，指标、大数组和原始样本写入 `metrics/` 或受控产物，不写入日志字段。
- `Reporter` 仅由 tracking adapter 负责写入事件；`ArtifactWriter` 仅由 artifacts adapter 负责写入 manifest、检查点和产物。算法层通过注入端口上报，不直接打开日志文件或拼接运行路径。
- 同一异常通常只在拥有 request/run 上下文的边界记录一次。错误事件保留异常类型和安全的诊断信息，不记录密钥、令牌、连接串、原始敏感样本、完整 manifest、大数组和不必要的绝对路径。
- CLI 的日志写 stderr，`--json` 最终结果写 stdout；调用方不得解析自然语言日志获得指标。
- 错误日志保留异常链；用户消息提供修复方向但不暴露堆栈或内部路径。
- 配置优先级：显式函数参数 > CLI > 环境变量 > 项目配置 > 用户配置 > 默认值。
- 合并后的非敏感配置进入 run；密钥只来自环境/凭据库/secret reference。
- 环境差异必须由配置表达，禁止用主机名或开发者路径分支。

## 10. 错误与资源生命周期

- 异常名称以 `Error` 结尾，携带稳定 `code` 和结构化字段；调用方禁止解析 message。
- 只捕获能够恢复、补充上下文或转换的异常；禁止 `except Exception: pass`。
- adapter 使用 exception chaining 将底层异常转换为项目异常；算法层不抛 HTTP 异常。
- CLI 和 HTTP 在最外层统一映射错误码、退出码/状态码和脱敏信息。
- `assert` 只用于测试和内部不变量，不能验证用户输入或替代运行时检查。
- 文件、锁、连接和进程使用 context manager 或明确 `finally` 清理。
- 长任务必须有所有者、状态、超时、取消和恢复行为；并发有上限，重试有界且仅用于确认可重试的幂等操作。

## 11. CLI 与 HTTP

- `main()`/router 应保持薄层，只做解析、调用、映射和呈现。
- 导入模块不得启动服务、解析参数、建立连接、扫描文件或写入目录。
- CLI 退出码和 JSON schema 是公共契约；日志不得污染 JSON stdout。
- 只有真实跨语言/远程需求存在时才实现 HTTP，不能为“架构完整”创建空服务。
- HTTP 路径使用复数资源名，GET 无副作用；验证错误、未认证、无权限、不存在、冲突、限流和不可用不能全部返回 200/500。
- 请求/响应 schema 默认拒绝未知字段；分页、排序、过滤和幂等语义从首版明确。
- 公共 schema 变更必须进行兼容 diff；breaking change 走 major 版本或正式弃用周期。

## 12. 测试与基准

- 测试从用户公开路径导入；不读源码文本断言实现细节，不 mock 被测对象的私有函数。
- Unit：纯算法、规则、状态转换，无网络、GPU或用户目录 I/O。
- Contract：同一套测试验证所有算法、Reporter、ArtifactWriter 和 schema 实现。
- Integration：真实本地文件、结果保存/重载、plot round-trip，使用临时目录。
- E2E：少量已安装 CLI/HTTP 用户路径，覆盖成功、无效输入、取消和失败。
- Regression：先复现已确认缺陷，再修复；数值结果声明 `rtol/atol` 和硬件/确定性条件。
- Benchmark：测延迟、吞吐、峰值内存/显存和产物大小；不得作为正确性单测，也不得在未知硬件上宣称性能提升。
- 默认测试禁止真实网络；GPU、下载和付费外部服务必须显式标记并在专门任务中运行。
- 测试独立、可重复，不依赖执行顺序；fixture 小、许可清晰，不包含真实敏感数据。
- 目标覆盖率：算法与 application 至少 90%，项目总体至少 80%；关键状态、路径和安全分支必须覆盖。覆盖率不能替代有意义断言。

## 13. 文档、提交和评审

- 公共 API、Protocol、用例和复杂算法必须有 docstring，说明非直观语义、副作用、幂等性、异常、单位和顺序保证。
- 注释解释原因、不变量和来源，不复述代码。TODO 使用 `TODO(owner, issue): reason`，不得无限期存在。
- 用户可见行为、配置、接口或错误变化必须同步 README/docs/examples/CHANGELOG。
- 新框架、持久化模型、公开 schema 版本、模块所有权或服务边界变化必须先写 ADR。
- 每个 PR 聚焦一个可说明的目的；禁止混入无关格式化、重命名或生成物变化。
- 贡献者对 AI 辅助生成的所有代码、测试、引用和许可证兼容性负完全责任；必须人工检查，不能以工具输出代替证据。

## 14. 质量命令

本地修改顺序：

```bash
uv sync --all-groups
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest
```

CI 使用只读检查：

```bash
uv sync --frozen --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
```

禁止为通过检查而降低规则、扩大 ignore、删除失败测试或伪造运行结果。

## 15. Definition of Done

一项变更只有同时满足以下条件才完成：

1. 范围、公共行为、失败行为和不做事项明确。
2. 文件位于正确模块，依赖方向无反转，无无调用方抽象。
3. 公共接口类型完整，错误、空值、单位、随机性和副作用明确。
4. 正常、边界、无效输入及相关恢复路径有适当层级的测试。
5. Ruff format、Ruff lint、mypy strict 和 pytest 在最终文件状态通过。
6. 日志和指标可诊断且不泄密，运行产物可追溯、可校验。
7. README、API/算法文档、schema、示例和变更日志按影响更新。
8. 评审者仅凭代码、类型、测试和文档即可理解行为，不依赖口头说明。

## 16. 参考来源

本规范针对本项目重新整理，参考以下公开官方规范和高采用度 AI/科学计算项目实践，不照搬其组织专用规则：

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)：导入、异常、全局状态、命名、main、函数聚焦和类型标注。
- [Microsoft APM CONTRIBUTING](https://github.com/microsoft/apm/blob/main/CONTRIBUTING.md)：以 Ruff/测试命令作为 CI 可复现门禁、集成测试前提和文档同步。
- [PyTorch CONTRIBUTING](https://github.com/pytorch/pytorch/blob/main/CONTRIBUTING.md)：贡献范围、分层测试、lint/type check、文档和 AI 辅助责任。
- [scikit-learn Estimator 开发规范](https://scikit-learn.org/stable/developers/develop.html)：统一 `fit`/`predict` 接口、参数可检查性、公共导入路径和共享 estimator checks。
- [Microsoft Azure REST API Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md)：HTTP 资源、状态、兼容和错误接口原则。
