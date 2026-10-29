# 工程接口与记录检查

只记录已经实现的接口。本模板尚无算法产品API；以下为F001只读治理接口，不能作为性能或科学结论证明。

## 命令行

```bash
python scripts/f001_governance_validate.py --project-root . --check
```

从工程根执行，`--project-root` 指向含configs的工程目录；`--check` 表示只读，省略也只读。无联网、移动、删除、改写或提交。stdout输出中文问题及ERROR/WARNING计数，退出0表示本次配置作用域内无错误，退出1表示错误或配置无法读取。旧命名提示仍是warning，不把历史提示冒充本次新缺陷。

## 配置来源与范围

同一 `configs/features.yaml` 维护功能身份、`record_policy` 和 `artifact_policy`，不新建第二配置源。根AGENTS的 `record_policy_registry` 供日记录工具定位策略。记录目录相对于项目外层根；责任扫描目录相对于工程根，所有解析结果必须在本项目边界内。

- `record_policy`：enabled、effective_date、timezone、project_id、profile、types、legacy_paths、current_entries、exports。类型映射包含aliases、directory、filename_body和label。当前入口仅填真实文件，没有成果时保持空。
- `artifact_policy`：governed_paths与ownership_rules（pattern/owner）。只在声明作用域内检查每文件恰好一个责任规则，不推断未配置范围。
- 功能的 `validate_paths: true` 启用实现/测试/证据路径存在性检查。既有未标注历史功能不被自动修改或重建；新受管功能必须启用。

## 日记录与引用

当前可写日记录使用 `daily-record/1.0` 文件级元数据：project_id、record_date（YYYY-MM-DD）、record_type、timezone（Asia/Shanghai）和record_profile（research）。日文件名称与目录由类型固定，别名先归一，跨目录/格式同类多份也报错。

每条由 `<!-- daily-entry {JSON} -->` 及 `<a id="entry-条目ID"></a>` 构成，JSON包含entry_id、event_key、attempt_id、recorded_at、occurred_at、status；科研日志还含research_point与research_source。真实重跑用不同尝试，修订声明revision_of；不能重复ID或同一事件/尝试。时间必须带时区，recorded_at转换上海日后与文件日一致。

只有生效日前无日记录schema的旧文及策略显式legacy_paths兼容为历史；文件自称archived不能逃避。正式实体文档与原始run不是日记录。只读导出通过exports的path/source声明真实母版，不可成为第二编辑源。文件#锚点分别检查；超出本项目的引用需要明确范围，不暗中读取或修改兄弟项目。

中文空白结构见成效目录既有templates中的同日科研记录模板。没有内容不创建日文件，不为每次追加另写“记录写入记录”。
