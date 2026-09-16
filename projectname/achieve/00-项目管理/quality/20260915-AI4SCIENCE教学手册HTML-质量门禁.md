---
title: "AI4SCIENCE教学手册HTML质量门禁"
document_id: "QG-20260915-HTML-01"
produced_at: "2026-09-15"
status: "已复核"
owner: "项目监理"
---

# AI4SCIENCE教学手册HTML质量门禁

| 层级 | 检查项 | 命令/方法 | 环境/样本 | 结果 | 证据 | 处置 |
|---|---|---|---|---|---|---|
| L1 | HTML 标签配平、锚点、资源路径、68 工作包行数 | Python `html.parser` 自定义只读检查 | `20260915-AI4SCIENCE教学手册-教学手册.html` | 通过：74049 bytes、20 个 id、68 个 SR 行、内部锚点缺失 0、资源路径缺失 0、未闭合标签 0 | 本表与日志验证表 | 通过 |
| L1 | 浏览器控制台错误 | Playwright CLI：本地 HTTP 打开后执行 `console error` | Chromium，页面从项目根相对路径加载 | 通过：Errors=0，Warnings=0 | 日志验证表 | 通过 |
| L2 | 源内容覆盖与一致性 | 人工交叉核对 5 个 Markdown 参考文档、PDF 文本样本和流程图 | `reference/` 全部 5 个 Markdown 与 PDF/流程图索引 | 通过：覆盖三层分工、12 工作流、Gate、68 工作包、成效卡/交接、目录命名、工程架构、外部实践 | 手册第 1～14 章 | 参考文档中的历史命名和路径冲突已显式标注由当前 AGENTS.md 裁决 |
| L3 | 桌面与移动用户路径 | Playwright 打开、导航、1440×1000 桌面截图、390×844 移动截图 | Chromium；本地文件经 HTTP 服务访问 | 通过：桌面最终视觉复核无溢出/重叠/乱码；移动端无横向溢出或文字重叠 | `quality/20260915-AI4SCIENCE教学手册-桌面视图-证据.png`、`quality/20260915-AI4SCIENCE教学手册-移动视图-证据.png` | 修复过元信息卡片 nowrap 溢出和按钮折行问题后复验通过 |
| L4 | 打印样式与响应式 CSS | 代码检查 `@media print`、`@media (max-width)`；未输出 PDF | 静态代码 | 通过：打印隐藏导航/控件，移动端切换单列；PDF 未生成 | 手册源码 | PDF 非本轮验收必需 |
| L5 | 治理登记与目录归属 | `python projectname/project/scripts/f001_governance_validate.py --project-root projectname/project --check` | Windows PowerShell / Python | 通过：ERROR=0，WARNING=1；警告指向既有 `.codex/skills/ps-09-daily-log-summary/agents/openai.yaml` 固定名称例外 | 验证输出记录于日志 | 本轮不修改既有 Skill；警告作为模板既有残余风险移交后续治理 |

## 外部实践检索证据

| 来源 | 检索方式 | 采用结论 | 未采用内容 |
|---|---|---|---|
| `Roritharr/diataxis-skill` | GitHub 只读检索 | 借鉴“先分类文档类型、教程单一路径、每步可见结果”的教学写法 | 未安装 Skill，未复制 CC BY-SA 正文 |
| `BennettPhil/builder-layered-docs-builder` | GitHub 只读检索 | 借鉴快速参考、教学、深层参考的分层阅读路径 | 未安装或复用代码 |
| `wesammustafa/opencode-primer` | GitHub 只读检索 | 借鉴读者路径、心智模型和参考链接组织方式 | 未复制品牌、长文或项目事实 |

## 结论

- 门禁结论：带条件通过。
- 未执行项及原因：未生成 PDF、未提交 Git、未发布网页；用户仅要求 HTML，发布和提交需另行授权。
- 残余风险：治理校验器存在 1 个既有固定名称警告，与本次手册无关；HTML 在不同浏览器中可能有细微渲染差异。
- 下一步：如需对外发布，应另建发布需求并执行浏览器兼容、可访问性和部署验证。
