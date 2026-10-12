---
title: "Axiom-reporter安装监督记录"
document_id: "SUP-20261012-AXIOM-01"
produced_at: "2026-10-12"
status: "完成"
owner: "项目监理"
governing_baseline: "根AGENTS.md及工程AGENTS.md"
writing_level: "B"
---

# Axiom-reporter安装监督记录

## 1. 操作登记

| 项目 | 内容 |
|---|---|
| 关联需求/任务 ID | REQ-20261012-AXIOM-01 / AXIOM-01、AXIOM-02 |
| 专业执行角色 | 主代理安装与验证；项目监理登记与收尾 |
| 目标与非目标 | 按来源说明安装现有沟通技能到当前项目；不科研推进、不全局安装、不提交推送 |
| 输入与目标产物 | 来源 https://github.com/1993zlorange/Axiom-reporter，提交 ab624f98da6cb9bf162a4dbf66e175976cd3acce；根规则追加段、自动备份、根级技能与许可证通知 |
| 权限与副作用 | 用户已明确授权安装并按来源说明执行；必要本地规则变更与备份在范围内；不调用凭据、付费服务或外部写入 |
| 验收和验证 | 来源安装器预览、来源测试、安全扫描、安装文件一致性、备份完整性检查、幂等验证、只读治理检查 |
| 停止条件 | 来源危险行为、未知同名内容、规则不可调和冲突或新增治理错误时停止相应分支 |

## 2. 文件放置与命名

| 产物 | 负责人 | 生命周期 | 最终路径 | 命名检查 | 引用影响 | 清理/归档 |
|---|---|---|---|---|---|---|
| 来源规则标记段 | 主代理 | 项目规则有效期间 | AGENTS.md | 固定入口例外 | 当前项目回复 | 卸载时移除标记段；保留原规则 |
| 安装器备份 | 主代理 | 恢复窗口及审计期 | AGENTS.md.bak-20261012-222157 | 上游自动命名例外 | 恢复安装前字节 | 不自动清理，后续授权后归档 |
| 技能入口与许可 | 主代理 | 指定版本使用期间 | .codex/skills/Axiom-reporter/SKILL.md；同目录 LICENSE | 固定入口；上游名称原样例外 | 当前项目技能发现与许可通知 | 按来源版本恢复；不移动既有目录 |
| 功能登记 | 主代理 | 随功能保留 | projectname/project/configs/features.yaml | 固定配置入口 | F003 / AXIOM_REPORTER | 撤销本次条目需同时检查引用 |
| 需求与监督 | 项目监理 | 长期审计 | requirements/20261012-Axiom-reporter安装-需求记录.md；supervision/20261012-Axiom-reporter安装-监督记录.md | 日期化；分别使用 A、B 模板 | 安装授权与范围 | 随项目保留 |
| 验证与事实记录 | 项目监理 | 长期审计 | 管理根 quality、logs、changes、costs 下 20261012-Axiom-reporter安装 对应记录 | 使用现有中文模板；不新增文档类型 | 验收证据与恢复说明 | 随项目保留 |

根 .codex、skills、Axiom-reporter 目录首次具体产物和责任已在关联需求记录中登记。本次来源明确落点是局部安装例外，唯一 project_skills_root 配置不改。

## 3. 执行证据

| 动作 | 实际结果 | 命令/证据路径 | 状态 | 偏差 |
|---|---|---|---|---|
| 项目入口检查 | 已读根/工程规则、编程规范、现有管理说明、近期日志、功能登记与工作区状态 | AGENTS.md；projectname/project/AGENTS.md；projectname/achieve/00-项目管理/README.md | 完成 | 既有未跟踪内容保留 |
| 来源规则和预览 | 主代理报告已完整审阅来源规则、README、安装器；预览计划追加标记段并创建技能 | 来源 scripts/install_rules.py . --with-skill | 完成，最终文件已核对 | 无联网、凭据、子进程或隐藏持久化 |
| 上游测试 | 主代理报告 9/9 通过 | 安装后质量记录汇总 | 完成，待证据汇总 | 不替代项目安装核对 |
| 安全扫描 | 主代理报告 scanner 2.0.13 五种分析器运行；0 高/中危，1 LOW、1 INFO | 安装后质量记录汇总 | 完成，待证据汇总 | 中文描述词数与上游大写名称提示已登记 |
| 基线治理 | 主代理报告 exit 0、ERROR 0、WARNING 12，均既有 | 项目 f001_governance_validate.py | 完成，最终结果与基线一致 | 未新增治理错误或警告 |
| 项目安装 | 主代理报告 exit 0，根规则追加 86 行，Skill 新建，verified True | python <来源>/scripts/install_rules.py . --write --with-skill；质量记录 | 完成 | 原文完整保留 |
| 备份与字节核对 | 备份 SHA256 匹配安装前；标记唯一、正文匹配；Skill/LICENSE 与来源字节一致 | quality/20261012-Axiom-reporter安装-质量门禁.md | 完成 | 无 |
| 重复安装 | 原安装模块 install(Path.cwd(), write=True, with_skill=True) 返回 unchanged、verified True；无新增备份，hash/mtime 不变 | 主代理安装模块调用与断言 | 完成 | 无 |
| CLI 重复安装 | 再次运行相同 --write --with-skill 命令，exit 0，AGENTS/技能 unchanged，验证通过 | 来源 scripts/install_rules.py | 完成 | 未实际覆盖恢复目标文件 |
| 最终治理及差异 | exit 0、ERROR 0、WARNING 12；与基线相同；git diff --check exit 0 | python projectname/project/scripts/f001_governance_validate.py --project-root projectname/project --check | 完成 | 既有警告不作为本次缺陷 |

## 4. 结论与闭环

- 监理结论：带条件通过，本地安装完成；条件是保留客户端发现未验证与来源名称兼容限制，不作额外能力承诺。
- 未执行项：客户端新会话自动发现未验证；未运行无关全工程测试、科研工作流、全局晋升或发布。
- 问题与反思：无新增确认缺陷、失败或重复返工；扫描提示按兼容限制记录，不新增反思。
- 残余风险：上游名称含大写；客户端技能发现尚未验证。根规则标记段已安装，项目根规则可直接生效。
- 人工决定：用户已授权指定来源项目安装；不存在科学决定或全局能力变更。
- 下一步：本批已完成。如以后升级或卸载，先核对现有规则与备份差异，按明确授权执行。
