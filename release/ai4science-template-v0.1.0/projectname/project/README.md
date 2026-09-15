# [项目名称]

<!--
将方括号占位内容替换为真实信息。只保留已经启用且链接有效的徽章。
建议顺序：CI、PyPI/发布版本、Python 版本、许可证、文档、覆盖率、DOI。
-->

> [用一句话说明项目解决什么问题、面向谁，以及最重要的差异。]

**项目状态：** `v0.1.0` 本地模板发行版。本模板尚未实现算法、CLI 或 HTTP 服务，不应被描述为可用于生产。

## 项目简介

[用 1-3 段回答以下问题：]

- 要解决的具体问题是什么？
- 目标用户是研究人员、算法工程师、应用开发者还是其他角色？
- 项目提供的是算法库、训练工具、推理服务，还是它们的组合？
- 哪些场景明确不在项目范围内？

## 主要能力

- [能力一：使用可观察的用户结果描述，不写“先进”“强大”等空泛形容词。]
- [能力二：说明支持的数据、模型或任务类型。]
- [能力三：说明可复现、可扩展或可集成能力。]

## 安装

### 环境要求

- Python 3.12 或更高版本
- [CPU/GPU、CUDA、操作系统等实际约束]
- [数据或模型访问前提]

### 从源码安装

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
uv sync --all-groups
```

[发布到 PyPI 后，再增加稳定版本的安装命令。不要让默认安装指向未发布包。]

## 快速开始

README 的第一个示例必须短小、可复制，并从公开 API 导入。以下代码是接口模板，不代表已经实现：

```python
from ai_project import train

result = train(
    algorithm="classification.linear",
    config={"learning_rate": 0.01, "epochs": 20},
    dataset="file:///path/to/train.parquet",
    output="file:///path/to/runs/demo-001",
    seed=42,
)
print(result.run_id)
```

CLI 接口实现后，补充与 Python API 语义一致的示例：

```bash
ai-project train --config configs/examples/demo.yaml --output var/runs/demo-001 --json
```

不要在 README 中发布未经自动测试的命令和结果。

## 公共接口

| 接口         | 面向对象                | 稳定性                | 文档                       |
| ------------ | ----------------------- | --------------------- | -------------------------- |
| Python API   | Python、Notebook 和测试 | [experimental/stable] | [docs/api.md](docs/api.md) |
| CLI          | 本地用户和自动化脚本    | [experimental/stable] | [补充 CLI 文档链接]        |
| HTTP API     | 跨语言或远程调用方      | 尚未启用              | [启用后补充 OpenAPI 链接]  |
| Run manifest | 画图、追踪和其他程序    | [schema 版本]         | [补充 schema 文档链接]     |

## 项目结构

本项目采用“可导入算法库 + 薄应用入口 + 独立运行产物”的模块化单体。算法返回结构化结果；测试、CLI、HTTP、Notebook 和画图复用相同的 application/API 层。

```text
.
├── src/ai_project/
│   ├── algorithms/       # 算法实现和显式注册表；不处理 CLI、HTTP 或画图
│   ├── application/      # train/evaluate/predict/inspect 用例编排
│   ├── data/             # 数据契约、加载、变换和输入校验
│   ├── evaluation/       # 指标和结构化评估报告
│   ├── visualization/    # ResultBundle -> FigureSpec -> 渲染器
│   ├── tracking/         # 日志、指标和运行事件适配器
│   ├── artifacts/        # RunManifest、产物引用和本地存储
│   ├── cli/              # 命令行参数、退出码和呈现
│   ├── server/           # 可选 HTTP composition root 和路由
│   ├── api.py            # 稳定 Python 调用门面
│   ├── contracts.py      # Algorithm、Reporter、ArtifactWriter 等协议
│   └── schemas.py        # 跨进程和持久化 DTO/schema
├── tests/
│   ├── unit/             # 纯算法和规则测试
│   ├── contract/         # 所有算法/适配器共享的契约测试
│   ├── integration/      # 本地文件、结果重载和画图往返
│   ├── e2e/              # 已安装 CLI/HTTP 的用户路径
│   └── regression/       # 已修复缺陷、固定夹具和容差结果
├── benchmarks/           # 性能测量，不替代正确性测试
├── configs/              # 可提交且不含密钥的默认/示例配置
├── examples/             # 只使用公开 API 的可运行示例
├── notebooks/            # 探索和演示，不拥有生产逻辑
├── docs/                 # 架构、API、算法说明和 ADR
├── scripts/              # 开发、发布和迁移辅助脚本，不是产品入口
├── docker/               # 确有容器发布需求后使用
└── var/runs/             # 本地运行数据，除占位文件外不提交 Git
```

详细的文件放置规则见 [AGENTS.md](AGENTS.md)，强制编码要求见 [PROGRAMMING_STANDARDS.md](PROGRAMMING_STANDARDS.md)。依赖方向为：

```text
cli/server/api -> application -> algorithms/evaluation/contracts
tracking/artifacts adapters -> contracts
visualization -> versioned result schemas
algorithms -X-> cli/server/visualization/concrete storage
```

## 运行结果与可复现性

每次训练或评估使用唯一 `run_id`，在 `var/runs/<date>/<run_id>/` 下关联：

- `manifest.json`：状态、算法/代码版本、输入摘要、环境和产物哈希；
- `config.resolved.yaml`：合并后的非敏感配置；
- `logs/events.jsonl`：必需的 UTF-8 JSON Lines 结构化事件，字段和脱敏规则见 [工程运行日志模板](docs/20260913-工程运行日志-模板.md)；
- `logs/` 中其他文件：可选的人类可读日志，不能替代 `events.jsonl`；
- `metrics/`：逐步指标和最终摘要；
- `artifacts/`：模型、表格和预测；
- `checkpoints/`：可恢复中间状态；
- `plots/`：由指标/表格派生，可删除后重新生成。

[补充本项目的确定性级别、数据版本规则、模型许可和复现实验命令。]

## 配置

配置优先级固定为：函数显式参数 > CLI 参数 > 环境变量 > 项目配置 > 用户配置 > 内置默认值。

```yaml
# configs/examples/demo.yaml
algorithm: classification.linear
seed: 42
[补充实际 schema]
```

密钥不得写入 YAML、README、日志或 run manifest。请记录项目实际使用的环境变量或 secret reference，但只提供安全占位值。

## 开发

```bash
uv sync --all-groups
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest
```

新增代码前先阅读 [PROGRAMMING_STANDARDS.md](PROGRAMMING_STANDARDS.md)；使用编码代理时还必须阅读 [AGENTS.md](AGENTS.md)。测试、类型检查和格式检查全部通过后才能提交。

## 文档

- [架构](docs/architecture.md)
- [公共 API](docs/api.md)
- [算法说明](docs/algorithms/)
- [架构决策记录](docs/adr/)
- [编程规范](PROGRAMMING_STANDARDS.md)

## 路线图

- [ ] 明确首个用户问题和验收指标
- [ ] 批准首个算法契约和 result schema
- [ ] 实现一个 CPU 最小算法及共享契约测试
- [ ] 实现本地 run store 和 plot round-trip
- [ ] 根据真实调用方决定是否需要 CLI/HTTP

路线图只包含已经讨论过的候选工作；批准状态和负责人应在 issue/里程碑中维护。

## 贡献

欢迎问题报告、文档改进和经过讨论的代码贡献。提交前请：

1. 先搜索已有 issue；较大功能先提交设计问题并确认范围。
2. 遵守 [PROGRAMMING_STANDARDS.md](PROGRAMMING_STANDARDS.md)。
3. 为可观察行为增加适当层级的测试。
4. 运行开发章节中的全部质量检查。
5. 同步更新公共接口、配置、示例、变更日志和文档。

[完善维护者响应时间、贡献协议、行为准则和 PR 模板。]

## 安全

不要在公开 issue 中提交密钥、私有数据、模型权重或未脱敏日志。安全问题请按 [SECURITY.md](SECURITY.md) 中的私密渠道报告；在渠道建立前，不应宣称已有安全响应 SLA。

## 引用

派生研究项目应在首次成果发行前填写 `CITATION.cff` 的作者、标题、版本、DOI 和仓库地址；本模板发行版不提供科研成果引用信息。

## 许可证

本模板采用 [MIT License](LICENSE)。派生项目须另行声明第三方模型、数据和成果材料的许可限制。

## 致谢与参考

README 的信息顺序参考了高采用度 AI/科学计算项目的官方 README，包括 [Hugging Face Transformers](https://github.com/huggingface/transformers)、[PyTorch](https://github.com/pytorch/pytorch) 和 [scikit-learn](https://github.com/scikit-learn/scikit-learn)。本模板为重新组织和编写，不复制这些项目的品牌、声明或实现。
