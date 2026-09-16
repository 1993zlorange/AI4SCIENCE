---
title: "AI4SCIENCE教学手册HTML变更记录"
document_id: "CHG-20260915-HTML-01"
produced_at: "2026-09-15"
status: "已实施"
owner: "项目监理"
---

# AI4SCIENCE教学手册HTML变更记录

| 变更 ID | 类型 | 变更对象 | 原因 | 用户/下游影响 | 兼容性 | 验证状态 | 回滚/迁移 |
|---|---|---|---|---|---|---|---|
| CHG-01 | 新增 | `projectname/project/docs/20260915-AI4SCIENCE教学手册-教学手册.html` | 用户要求将参考文档改写为通俗 HTML 教学手册 | 新读者可按文档站布局学习 AI4SCIENCE 全貌 | 不影响既有代码；使用项目相对路径链接 | 通过 HTML、浏览器、视觉和治理检查 | 删除新增 HTML 即可回滚 |
| CHG-02 | 新增 | `projectname/achieve/00-项目管理/templates/20260915-HTML教学手册-模板.html` 和文档类型登记 | 新文件类型需要中文空白模板和登记 | 后续 HTML 教学手册有统一结构 | 模板仅作新文档起点 | 登记、存在性和内容检查通过 | 删除模板并撤销登记 |
| CHG-03 | 新增 | 需求、监督、放置、质量、日志、成本记录和两张浏览器证据 PNG | 项目治理要求闭环 | 操作可追溯；证据可复核 | 管理记录互不覆盖 | 治理校验 ERROR=0，WARNING=1（既有） | 删除本批新增管理文件即可回滚 |

## 关联材料

- 需求/问题：`requirements/20260915-AI4SCIENCE教学手册HTML请求-需求记录.md`
- 实现/设计：`supervision/20260915-AI4SCIENCE教学手册HTML放置-放置决策.md`；`templates/20260915-HTML教学手册-文档类型登记.md`
- 测试/证据：`quality/20260915-AI4SCIENCE教学手册HTML-质量门禁.md`
- 发布/验收状态：本地生成已完成；正式发布和 Git 提交未授权。
