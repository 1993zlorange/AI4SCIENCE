---
title: "Axiom-reporter远端推送质量门禁"
document_id: "QG-20261012-AXIOM-PUSH"
produced_at: "2026-10-12"
status: "安装提交已同步"
owner: "项目监理"
writing_level: "C"
---

# Axiom-reporter远端推送质量门禁

| 层级 | 检查项 | 命令/方法 | 环境/样本 | 结果 | 证据 | 处置 |
|---|---|---|---|---|---|---|
| L1 | 安装内容未变 | 主代理SHA核对、标记和F003路径检查 | 四个安装文件、功能登记 | SHA与上次一致；begin/end各1；F003 active且所有路径存在 | 主代理报告；上次安装质量记录 | 保留原安装结论 |
| L1 | 差异范围 | git diff --check；git diff --cached --check | 安装及入口记录13文件 | 均exit 0；无关20260918等内容未提交 | 主代理报告 | 选择性暂存 |
| L1 | 项目治理 | python projectname/project/scripts/f001_governance_validate.py --project-root projectname/project --check | 推送前 | exit 0；ERROR 0 / WARNING 12，均既有 | 主代理报告 | 不修无关警告 |
| L1 | 管理记录结构 | ps_04_validate_management_document.py <document> --strict | 本批六份记录 | 全部exit 0；errors 0 warnings 0 | 监理实际执行输出 | 结构检查通过，不代替事实核对 |
| L5 | 普通推送 | git -c credential.interactive=never push origin main | 当前origin/main | exit 0；a07f2bc..2b59259 main -> main | 主代理报告 | 无强制推送 |
| L5 | 远端提交核对 | git ls-remote --heads origin main；git diff --quiet HEAD | 首次推送后 | 远端SHA为2b59259d89a0ff8faa7766c947374cc5319e573a；差异命令exit 0 | 主代理报告 | 安装提交已同步 |

## 结论

- 门禁结论：安装提交推送通过；本批管理记录随后同步。
- 未执行项及原因：本次仅推送既有安装，不重跑来源测试、全工程测试或科研实验；本批记录自身的推送尚待执行。
- 残余风险：沿用上次安装质量记录的客户端发现限制和既有12项警告。
- 下一步：主代理推送本批记录并核对最终远端提交。
