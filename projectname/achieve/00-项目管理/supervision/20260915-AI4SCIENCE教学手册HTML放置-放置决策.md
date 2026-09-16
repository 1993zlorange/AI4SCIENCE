---
title: "AI4SCIENCE教学手册HTML文件放置决策"
document_id: "PLACE-20260915-HTML-01"
produced_at: "2026-09-15"
status: "已批准执行"
owner: "项目监理"
---

# AI4SCIENCE教学手册HTML文件放置决策

| 产物 | 类型 | 负责人 | 生命周期 | 最终路径 | 命名规则 | 引用影响 | 清理/归档 |
|---|---|---|---|---|---|---|---|
| AI4SCIENCE 教学手册 | HTML 工程文档 | 文档维护者 | 随模板演进 | `projectname/project/docs/20260915-AI4SCIENCE教学手册-教学手册.html` | `YYYYMMDD-内容简述-文档类型.扩展名` | 以项目相对路径链接源文档与流程图 | 重大修订新增日期文件；小修经评审后更新并记录 |
| HTML 教学手册空白模板 | HTML 管理模板 | 项目监理 | 长期 | `projectname/achieve/00-项目管理/templates/20260915-HTML教学手册-模板.html` | `YYYYMMDD-内容简述-模板.html` | 供后续同类型文档使用 | 与文档类型登记同步维护 |
| 浏览器视觉证据 | PNG 质量证据 | 项目监理 | 随本批质量记录保留 | `projectname/achieve/00-项目管理/quality/20260915-AI4SCIENCE教学手册-桌面视图-证据.png`、`projectname/achieve/00-项目管理/quality/20260915-AI4SCIENCE教学手册-移动视图-证据.png` | `YYYYMMDD-对象-视图或状态-证据.png` | 支持质量门禁复核 | 不作为第二事实源，仅证明渲染状态 |

## 新目录判断

- 是否已有合适责任目录：是，正式手册使用 `projectname/project/docs/`，模板使用项目管理 `templates/`。
- 新目录是否由具体产物触发：否，不新建目录。
- 目录职责和非职责：`docs/` 保存工程文档和手册；不保存成果卡、工作流交接书或原始参考材料。
- 需要同步的 AGENTS/README/架构：不改变目录结构；通过本决策和文档类型登记追溯。
- 迁移、兼容和回滚：新增文件，不移动既有文件；可按 Git 工作区删除新增文件回滚。
- 人工决定：用户明确请求 HTML 教学手册，本地生成视为已授权；对外发布未授权。

