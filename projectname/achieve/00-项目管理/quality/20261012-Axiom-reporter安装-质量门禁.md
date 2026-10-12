---
title: "Axiom-reporter安装质量门禁"
document_id: "QG-20261012-AXIOM-01"
produced_at: "2026-10-12"
status: "完成"
owner: "项目监理"
writing_level: "C"
---

# Axiom-reporter安装质量门禁

| 层级 | 检查项 | 命令/方法 | 环境/样本 | 结果 | 证据 | 处置 |
|---|---|---|---|---|---|---|
| L1 | 项目入口、授权、落点与命名 | 根/工程 AGENTS.md、编程规范、git status 与来源说明对照 | 当前项目及来源提交 ab624f98da6cb9bf162a4dbf66e175976cd3acce | 入口登记完成 | requirements/20261012-Axiom-reporter安装-需求记录.md；supervision/20261012-Axiom-reporter安装-监督记录.md | 本次根级 .codex/skills/Axiom-reporter 是来源明确落点例外；唯一配置不改 |
| L1 | 来源安装器人工检查 | 主代理完整审阅来源 AGENTS、README、规则、scripts/install_rules.py | 指定来源版本 | 主代理报告只读源规则/技能并写目标规则、备份和技能；无联网、凭据、子进程或隐藏持久化 | 主代理安装证据与最终字节核对 | 已按预览范围安装 |
| L1 | 第三方 Skill 安全扫描 | scanner 2.0.13；static、bytecode、pipeline、behavioral、trigger | 来源完整 skills/Axiom-reporter | 主代理报告 0 CRITICAL/HIGH/MEDIUM，1 LOW、1 INFO；无 unavailable | TRIGGER_DESCRIPTION_TOO_SHORT；MANIFEST_INVALID_NAME | 中文连续词被识别为 1 word，语义完整；保留上游大写名称并登记兼容限制。扫描不等于安全证明 |
| L2 | 上游安装器测试 | 来源根 python -m unittest discover -s tests -v | 来源版本 | exit 0，9/9 通过，主代理执行并报告 | 来源 tests | 不替代当前项目文件核对 |
| L3 | 项目实际安装与备份完整性 | python <来源>/scripts/install_rules.py . --write --with-skill | 当前项目 | exit 0；根规则追加 86 行、技能新建、verified True | AGENTS.md；AGENTS.md.bak-20261012-222157；.codex/skills/Axiom-reporter | 原文完整保留；备份匹配安装前 SHA256；未实际恢复目标 |
| L3 | 规则、技能、许可一致性 | 主代理断言 new.startswith(backup.read_text())、唯一 begin/end、正文与来源一致、Skill/LICENSE 字节一致 | 目标文件与指定来源 | 全部通过 | 下方哈希表 | 原始治理规则保留 |
| L3 | 重复安装幂等 | 主代理通过 importlib 调用原安装模块 install(Path.cwd(), write=True, with_skill=True)，并 _print_result | 同一项目第二次写入调用 | unchanged；verified True；无备份；hash/mtime 全部未变 | 主代理断言结果 | 不产生额外变更 |
| L3 | CLI 重复安装 | python <来源>/scripts/install_rules.py . --write --with-skill | 当前项目再次调用 | exit 0；AGENTS/技能 unchanged，验证通过 | 主代理 CLI 结果 | 幂等通过 |
| L1 | 项目治理基线 | python projectname/project/scripts/f001_governance_validate.py --project-root projectname/project --check | 安装前 | 主代理报告 exit 0，ERROR 0，WARNING 12，全部既有 | 主代理基线结果 | 最终检查需对比新增错误和警告 |
| L1 | 最终项目治理 | python projectname/project/scripts/f001_governance_validate.py --project-root projectname/project --check | 安装后 | exit 0，ERROR 0，WARNING 12；与基线完全相同 | 主代理最终治理结果 | 既有警告保留，不修无关文件 |
| L1 | Git 差异 | git diff --check | 本次变更 | exit 0；主代理报告仅 features 换行提示 | git diff 与状态 | 没有破坏；不自动格式化无关内容 |
| L1 | 管理文档结构 | ps_04_validate_management_document.py <本批文档> --strict | 六类记录 | 最终 errors 0，warnings 0，全部 exit 0 | 同日需求、监督、质量、日志、变更、成本记录 | 初查两处长句已拆分，再查通过 |
| L4 | 客户端自动发现 | 未执行 | 当前客户端会话 | 未执行 | 上游 name 为 Axiom-reporter | 技能是否进入新会话列表仍有兼容性边界；根规则可直接生效 |
| L5 | 许可与来源可追溯 | 上游 LICENSE、来源提交及安装字节核对 | MIT 上游包 | LICENSE 与来源字节一致 | .codex/skills/Axiom-reporter/LICENSE | 保留通知，不改写上游技能 |

## 哈希与复现信息

| 对象 | SHA256 / 固定版本 | 结论 |
|---|---|---|
| 来源提交 | ab624f98da6cb9bf162a4dbf66e175976cd3acce | Git 提交，不是 SHA256 |
| 安装前 AGENTS.md / 实际备份 | dd26e32359de6cf9c6b5768e6839104b7c570484e44766bb008324223c51a294 | 备份与安装前一致 |
| 安装后 AGENTS.md | 52517925db52b3140f4b6a5f1b152789b6dc5b40b673d569bf538f1fdd529f5b | 来源标记 begin 在 230 行，end 在 314 行 |
| SKILL.md | 7479c814bb8938b7e63f28691e60f92165d9a839d7ff7ba0ddb07a2062dd1b87 | 与来源字节一致 |
| LICENSE | 521fde1a6e27af905138e22eccfa194e64caa54f32c4d62ace4a7102004a126d | 与来源字节一致 |

| 扫描复现命令 | 退出码 |
|---|---|
| skill-scanner scan <来源>/skills/Axiom-reporter --use-behavioral --use-trigger --format markdown --detailed | 0 |

<来源> 表示固定提交的本地读取副本。未把机器绝对路径写入记录。

## 结论

- 门禁结论：带条件通过，本地文件安装、备份、幂等、来源一致性及项目治理通过。
- 未执行项及原因：工程 Python 源码、算法、接口和实验未变，不运行全工程 Ruff/mypy/pytest；不调用科学工作流。客户端自动发现未验证。无全局 Skill 晋升，不运行晋升安装流程。
- 适用边界：本次安装现有第三方沟通技能，不创作新 Skill。技能只约束对话，不产生持久文档，因此不新增中文文档模板。来源安装器只用于本次安装，不创建项目脚本工具。
- 残余风险：来源 name 大写可能影响部分客户端发现；扫描提示不构成已确认产品缺陷。原 12 项治理警告保持不变。客户端发现尚未验证。
- 下一步：本批结束；后续升级时固定来源版本并保留备份完整性证据。
