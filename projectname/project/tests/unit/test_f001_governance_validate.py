"""F001 日记录归并、引用和文件职责的行为回归。"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "f001_governance_validate.py"
SPEC = importlib.util.spec_from_file_location("science_governance", SCRIPT)
assert SPEC and SPEC.loader
GOVERNANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GOVERNANCE)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "research" / "project"
    (root / "configs").mkdir(parents=True)
    policy = {
        "enabled": True,
        "effective_date": "2026-10-29",
        "timezone": "Asia/Shanghai",
        "project_id": "research",
        "profile": "research",
        "legacy_paths": [],
        "current_entries": {},
        "exports": [],
        "types": {
            "change": {
                "aliases": ["变更记录"],
                "directory": "research/achieve/00-项目管理/changes",
                "filename_body": "项目变更",
                "label": "变更记录",
            },
            "log": {
                "aliases": ["日志", "项目日志", "科研日志"],
                "directory": "research/achieve/00-项目管理/logs",
                "filename_body": "科研进度",
                "label": "日志",
            },
            "achievement": {
                "aliases": ["成果卡"],
                "directory": "research/achieve/08-项目推进与下一步计划",
                "filename_body": "科研结果",
                "label": "成果卡",
            },
        },
    }
    write_registry(root, {"features": [], "record_policy": policy})
    return root


def write_registry(root: Path, data: dict[str, Any]) -> None:
    (root / "configs" / "features.yaml").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )


def configure(root: Path, key: str, value: Any) -> None:
    path = root / "configs" / "features.yaml"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["record_policy"][key] = value
    write_registry(root, data)


def entry(identifier: str, **overrides: Any) -> dict[str, Any]:
    result = {
        "entry_id": identifier,
        "event_key": identifier,
        "attempt_id": "1",
        "recorded_at": "2026-10-29T10:00:00+08:00",
        "occurred_at": "2026-10-29T09:00:00+08:00",
        "status": "completed",
    }
    result.update(overrides)
    return result


def record(
    root: Path,
    kind: str = "change",
    entries: list[dict[str, Any]] | None = None,
    relative: str | None = None,
    body: str = "",
    **metadata: str,
) -> Path:
    data = json.loads((root / "configs" / "features.yaml").read_text(encoding="utf-8"))
    spec = data["record_policy"]["types"][kind]
    path = root.parent.parent / (
        relative or f"{spec['directory']}/20261029-{spec['filename_body']}-{spec['label']}.md"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": "daily-record/1.0",
        "project_id": "research",
        "record_date": "2026-10-29",
        "record_type": kind,
        "timezone": "Asia/Shanghai",
        "record_profile": "research",
    }
    meta.update(metadata)
    text = "---\n" + "\n".join(f"{k}: {v}" for k, v in meta.items()) + "\n---\n\n"
    for item in entries or [entry("one")]:
        text += (
            "<!-- daily-entry "
            + json.dumps(item, ensure_ascii=False)
            + " -->\n"
            + f'<a id="entry-{item["entry_id"]}"></a>\n## 实际工作\n\n'
        )
    path.write_text(text + body, encoding="utf-8")
    return path


def test_two_tasks_are_independent_entries_in_one_day_file(project: Path) -> None:
    record(project, entries=[entry("method"), entry("analysis")])
    assert GOVERNANCE.validate_daily_records(project) == []


def test_alias_in_another_directory_cannot_create_second_daily_log(project: Path) -> None:
    details = {"research_point": "比较性能", "research_source": "研究要点原文"}
    record(project, "log", [entry("first", **details)])
    record(
        project,
        "log",
        [entry("second", **details)],
        relative="research/achieve/other/20261029-任务B-项目日志.md",
        record_type="项目日志",
    )
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("同日同类型多份" in value for value in errors)
    assert any("落点或固定文件名不符" in value for value in errors)


def test_role_and_sr_do_not_create_another_result_file(project: Path) -> None:
    record(project, "achievement", [entry("sr-a")])
    record(
        project,
        "achievement",
        [entry("sr-b")],
        relative="research/achieve/04-技术方案/MB-X01/20261029-任务B-成果卡.md",
    )
    assert any("同日同类型多份" in e for e in GOVERNANCE.validate_daily_records(project))


def test_html_is_not_another_editable_record_source(project: Path) -> None:
    record(project)
    record(
        project,
        entries=[entry("html")],
        relative="research/achieve/00-项目管理/changes/20261029-项目变更-变更记录.html",
    )
    assert any("同日同类型多份" in e for e in GOVERNANCE.validate_daily_records(project))


def test_declared_read_only_export_requires_real_source(project: Path) -> None:
    source = record(project)
    target = source.with_suffix(".html")
    target.write_text("<p>从母版导出的只读副本</p>", encoding="utf-8")
    repo = project.parent.parent
    configure(
        project,
        "exports",
        [
            {
                "path": target.relative_to(repo).as_posix(),
                "source": source.relative_to(repo).as_posix(),
            }
        ],
    )
    assert GOVERNANCE.validate_daily_records(project) == []
    source.unlink()
    assert any("导出母版无效" in e for e in GOVERNANCE.validate_daily_records(project))


def test_historical_files_are_read_only_compatible_without_fabricated_metadata(
    project: Path,
) -> None:
    old = project.parent / "achieve" / "old" / "20260918-旧任务-项目日志.md"
    old.parent.mkdir(parents=True)
    old.write_text("历史原文不能为满足新规则补写当时记录。", encoding="utf-8")
    assert GOVERNANCE.validate_daily_records(project) == []


def test_self_declared_archived_state_cannot_bypass_current_policy(project: Path) -> None:
    path = record(
        project,
        relative="research/achieve/old/20261029-旧任务-变更记录.md",
        record_state="archived",
    )
    assert any("落点" in e for e in GOVERNANCE.validate_daily_records(project))
    configure(project, "legacy_paths", [path.relative_to(project.parent.parent).as_posix()])
    assert GOVERNANCE.validate_daily_records(project) == []


def test_duplicate_entry_and_repeated_event_are_rejected(project: Path) -> None:
    record(project, entries=[entry("same"), entry("same")])
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("条目ID重复" in e for e in errors)
    assert any("事件和尝试重复" in e for e in errors)


def test_real_retry_and_explicit_revision_remain_independent(project: Path) -> None:
    record(
        project,
        entries=[
            entry("first", event_key="event"),
            entry("retry", event_key="event", attempt_id="2"),
            entry("correction", event_key="event-correction", revision_of="first"),
        ],
    )
    assert GOVERNANCE.validate_daily_records(project) == []


def test_cross_midnight_uses_shanghai_record_day(project: Path) -> None:
    record(
        project,
        entries=[
            entry(
                "late",
                recorded_at="2026-10-28T16:30:00+00:00",
                occurred_at="2026-10-28T10:00:00+00:00",
            )
        ],
    )
    assert GOVERNANCE.validate_daily_records(project) == []
    record(project, entries=[entry("wrong", recorded_at="2026-10-28T15:30:00+00:00")])
    assert any("上海记录日不符" in e for e in GOVERNANCE.validate_daily_records(project))


def test_new_schema_at_arbitrary_path_is_still_active(project: Path) -> None:
    record(project, relative="research/achieve/arbitrary.md")
    assert any("落点" in e for e in GOVERNANCE.validate_daily_records(project))


def test_unknown_schema_cannot_hide_record(project: Path) -> None:
    record(project, relative="research/achieve/arbitrary.md", schema_version="daily-record/9.0")
    assert any("不支持" in e for e in GOVERNANCE.validate_daily_records(project))


def test_missing_record_anchor_or_source_reference_is_detected(project: Path) -> None:
    record(project, body="[本条](#entry-one) [不存在](missing.md#entry-x)")
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("引用不存在" in e for e in errors)
    record(project, body="[错误锚点](#entry-not-there)")
    assert any("锚点不存在" in e for e in GOVERNANCE.validate_daily_records(project))


def test_scientific_log_requires_research_source_and_excludes_engineering(project: Path) -> None:
    record(project, "log", [entry("test-check", work_kind="correctness")])
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("研究要点及出处" in e for e in errors)
    assert any("工程/管理事件" in e for e in errors)


def test_record_type_directory_cannot_escape_project(project: Path) -> None:
    registry = json.loads((project / "configs" / "features.yaml").read_text(encoding="utf-8"))
    registry["record_policy"]["types"]["change"]["directory"] = "../outside"
    write_registry(project, registry)
    with pytest.raises(ValueError, match="超出项目"):
        GOVERNANCE.validate_daily_records(project)


def test_governed_file_has_exactly_one_owner_and_current_entry_exists(project: Path) -> None:
    source = project / "src" / "algorithm.py"
    source.parent.mkdir()
    source.write_text("# 实现", encoding="utf-8")
    data = json.loads((project / "configs" / "features.yaml").read_text(encoding="utf-8"))
    data["artifact_policy"] = {
        "governed_paths": ["src"],
        "ownership_rules": [{"pattern": "src/**", "owner": "算法实现"}],
    }
    write_registry(project, data)
    assert GOVERNANCE.validate_artifact_routes(project) == []
    data["artifact_policy"]["ownership_rules"].append(
        {"pattern": "src/*.py", "owner": "另一个责任"}
    )
    write_registry(project, data)
    assert any("仅有一个" in e for e in GOVERNANCE.validate_artifact_routes(project))
    data["artifact_policy"]["ownership_rules"] = []
    data["record_policy"]["current_entries"] = {"report": "research/achieve/not-created.pdf"}
    write_registry(project, data)
    errors = GOVERNANCE.validate_artifact_routes(project)
    assert any("仅有一个" in e for e in errors)
    assert any("当前入口不存在" in e for e in errors)


def test_managed_feature_paths_are_checked_without_recreating_legacy_assets(project: Path) -> None:
    data = json.loads((project / "configs" / "features.yaml").read_text(encoding="utf-8"))
    data["features"] = [
        {
            "feature_id": "F001",
            "feature_code": "RECORD_CHECK",
            "validate_paths": True,
            "implementation_paths": ["missing.py"],
        },
        {
            "feature_id": "F002",
            "feature_code": "LEGACY",
            "implementation_paths": ["old-missing.py"],
        },
    ]
    write_registry(project, data)
    errors = GOVERNANCE.validate_feature_registry(project)
    assert any("missing.py" in e for e in errors)
    assert not any("old-missing.py" in e for e in errors)


@pytest.mark.parametrize("directory", ["var/runs/20261029/hidden", "output/temporary"])
def test_schema_record_cannot_hide_inside_raw_run_directory(project: Path, directory: str) -> None:
    record(project)
    record(project, entries=[entry("hidden")], relative=f"research/project/{directory}/record.md")
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("同日同类型多份" in e for e in errors)
    assert any("落点" in e for e in errors)


def test_missing_date_named_record_is_not_implicit_legacy(project: Path) -> None:
    path = project / "var" / "task-日志.md"
    path.parent.mkdir()
    path.write_text("当天记录不能因未写日期被略过。", encoding="utf-8")
    assert any("缺少记录日" in e for e in GOVERNANCE.validate_daily_records(project))


def test_legacy_directory_or_glob_cannot_exempt_future_records(project: Path) -> None:
    path = record(project)
    configure(project, "legacy_paths", [path.parent.relative_to(project.parent.parent).as_posix()])
    with pytest.raises(ValueError, match="精确文件"):
        GOVERNANCE.validate_daily_records(project)
    configure(project, "legacy_paths", ["research/achieve/**"])
    with pytest.raises(ValueError, match="通配符"):
        GOVERNANCE.validate_daily_records(project)


def test_json_schema_cannot_be_an_unregistered_second_editable_format(project: Path) -> None:
    record(project)
    path = project / "var" / "run" / "secret.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "daily-record/1.0",
                "record_type": "change",
                "record_date": "2026-10-29",
                "project_id": "research",
                "timezone": "Asia/Shanghai",
            }
        ),
        encoding="utf-8",
    )
    assert any("同日同类型多份" in e for e in GOVERNANCE.validate_daily_records(project))


def test_arbitrary_extension_with_explicit_schema_cannot_bypass(project: Path) -> None:
    record(project)
    record(project, entries=[entry("hidden-notes")], relative="research/project/var/hidden.notes")
    assert any("同日同类型多份" in e for e in GOVERNANCE.validate_daily_records(project))


def test_event_and_entry_identity_are_global_across_record_types(project: Path) -> None:
    record(project, entries=[entry("same")])
    record(project, "achievement", entries=[entry("same")])
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("条目ID重复" in e for e in errors)
    assert any("事件和尝试重复" in e for e in errors)


def test_read_only_derived_document_uses_true_mother_not_second_source(project: Path) -> None:
    source = record(project)
    target = record(
        project,
        entries=[entry("one")],
        relative="research/achieve/exports/rendered.notes",
        read_only="true",
        derived_from=source.relative_to(project.parent.parent).as_posix(),
    )
    assert GOVERNANCE.validate_daily_records(project) == []
    target.write_text(
        target.read_text(encoding="utf-8").replace("derived_from:", "unrelated:"), encoding="utf-8"
    )
    assert any("同日同类型多份" in e for e in GOVERNANCE.validate_daily_records(project))


def test_export_with_unreadable_binary_mother_is_a_reported_error(project: Path) -> None:
    source = project / "source.bin"
    source.write_bytes(b"\xff\xfe\x00")
    record(
        project,
        relative="research/achieve/export.notes",
        read_only="true",
        derived_from=source.relative_to(project.parent.parent).as_posix(),
    )
    assert any("母版无法读取" in e for e in GOVERNANCE.validate_daily_records(project))


def group_entry(project: Path, identifier: str = "group-one", **overrides: Any) -> dict[str, Any]:
    source = project.parent / "achieve" / "existing-research.md"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('<a id="guide"></a>\n研究问题与已有原始结果。', encoding="utf-8")
    item = entry(
        identifier, recorded_at="2026-10-30T10:00:00+08:00", occurred_at="2026-10-30T09:00:00+08:00"
    )
    item.update(
        report_contract="group-meeting/1.0",
        work_kind="literature",
        research_point="研究要点",
        research_source="research/achieve/existing-research.md#guide",
        guide_questions=["4.4.Q10"],
        research_question="需要回答哪个研究问题",
        actions="阅读已有研究资料并整理比较",
        result="已有结果与未决问题分开记录",
        interpretation="仅作条件下的解释",
        limitations="尚缺独立性能对照",
        next_step="先分析已有性能结果",
        evidence=["research/achieve/existing-research.md#guide"],
    )
    item.update(overrides)
    return item


def group_record(project: Path, items: list[dict[str, Any]], body: str = "") -> Path:
    configure(project, "log_contract", "group-meeting/1.0")
    configure(project, "log_contract_effective_date", "2026-10-30")
    return record(
        project,
        "log",
        items,
        relative="research/achieve/00-项目管理/logs/20261030-科研进度-日志.md",
        record_date="2026-10-30",
        body=body,
    )


def test_new_research_log_accepts_group_meeting_fields_and_real_sources(project: Path) -> None:
    group_record(project, [group_entry(project)])
    assert GOVERNANCE.validate_daily_records(project) == []


@pytest.mark.parametrize(
    "section,limit", [(1, 14), (2, 16), (3, 17), (4, 14), (5, 14), (6, 15), (7, 14)]
)
def test_guide_question_limits_are_exact(project: Path, section: int, limit: int) -> None:
    group_record(project, [group_entry(project, guide_questions=[f"4.{section}.Q{limit}"])])
    assert GOVERNANCE.validate_daily_records(project) == []
    group_record(project, [group_entry(project, guide_questions=[f"4.{section}.Q{limit + 1}"])])
    assert any("问题编号不存在" in e for e in GOVERNANCE.validate_daily_records(project))


@pytest.mark.parametrize("question", ["3.4.Q10", "4.0.Q1", "4.8.Q1", "4.4.Q0"])
def test_guide_identifier_cannot_be_another_outline(project: Path, question: str) -> None:
    group_record(project, [group_entry(project, guide_questions=[question])])
    assert any("问题编号不存在" in e for e in GOVERNANCE.validate_daily_records(project))


def test_new_entry_cannot_omit_contract_or_borrow_next_entry_fields(project: Path) -> None:
    first = group_entry(project, "missing", report_contract=None, result=None)
    second = group_entry(project, "complete")
    group_record(project, [first, second])
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("必须声明report_contract" in e for e in errors)
    assert any("缺少实际result" in e for e in errors)


def test_old_day_new_record_time_still_requires_contract(project: Path) -> None:
    record(
        project,
        "log",
        [
            entry(
                "backdated",
                recorded_at="2026-10-30T10:00:00+08:00",
                research_point="研究要点",
                research_source="已有出处",
            )
        ],
    )
    assert any("必须声明report_contract" in e for e in GOVERNANCE.validate_daily_records(project))


@pytest.mark.parametrize("kind", ["performance", "analysis"])
def test_performance_and_analysis_need_conditions_and_metrics(project: Path, kind: str) -> None:
    item = group_entry(project, work_kind=kind)
    group_record(project, [item])
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("comparison_conditions" in e for e in errors)
    assert any("metrics" in e for e in errors)
    item.update(comparison_conditions="同一输入与预算", metrics="配对差值为0")
    group_record(project, [item])
    assert GOVERNANCE.validate_daily_records(project) == []


def test_group_log_rejects_engineering_appendix_and_unlocatable_evidence(project: Path) -> None:
    group_record(
        project,
        [
            group_entry(
                project,
                work_kind="engineering",
                evidence=["missing.csv"],
                research_source="research/achieve/existing-research.md#missing",
            )
        ],
        body="\n### 附录\uff1a管理信息\n机械过程信息\n",
    )
    errors = GOVERNANCE.validate_daily_records(project)
    assert any("work_kind" in e for e in errors)
    assert any("research_source" in e for e in errors)
    assert any("证据无法定位" in e for e in errors)
    assert any("工程或管理附录" in e for e in errors)


def test_legacy_entry_remains_compatible_without_new_contract(project: Path) -> None:
    record(
        project,
        "log",
        [entry("legacy-entry", research_point="旧研究要点", research_source="旧原文出处")],
        body="\n### 附录\uff1a管理信息\n原有信息\n",
    )
    assert GOVERNANCE.validate_daily_records(project) == []


def test_historical_view_is_precisely_registered_and_not_an_active_daily_file(
    project: Path,
) -> None:
    path = project.parent / "achieve/00-项目管理/logs/20261029-科研进度-日志.md"
    path.parent.mkdir(parents=True)
    text = "---\nschema_version: research-history/1.0\nproject_id: research\nrecord_state: historical_readonly\nevent_date: 2026-10-29\ncompiled_at: 2026-10-30T12:00:00+08:00\n---\n\n按核实日期整理的科研进展。\n"
    path.write_text(text, encoding="utf-8")
    assert any("未登记精确路径" in e for e in GOVERNANCE.validate_daily_records(project))
    configure(project, "historical_views", [path.relative_to(project.parent.parent).as_posix()])
    assert GOVERNANCE.validate_daily_records(project) == []
    path.write_text(text.replace("compiled_at:", "recorded_at:"), encoding="utf-8")
    assert any("compiled_at" in e for e in GOVERNANCE.validate_daily_records(project))
    assert any("不能伪造旧recorded_at" in e for e in GOVERNANCE.validate_daily_records(project))


def enable_minimal_records(project: Path) -> None:
    configure(project, "enabled_daily_types", ["requirement", "log"])
    configure(project, "process_record_profile", "minimal")
    configure(project, "minimal_records_effective_date", "2026-10-30")


@pytest.mark.parametrize(
    "kind,label,body", [("change", "变更记录", "项目变更"), ("achievement", "成果卡", "科研结果")]
)
def test_minimal_profile_blocks_new_process_daily_files(
    project: Path, kind: str, label: str, body: str
) -> None:
    enable_minimal_records(project)
    spec = json.loads((project / "configs/features.yaml").read_text(encoding="utf-8"))[
        "record_policy"
    ]["types"][kind]
    record(
        project,
        kind,
        [entry("new-process", recorded_at="2026-10-30T10:00:00+08:00")],
        relative=f"{spec['directory']}/20261030-{body}-{label}.md",
        record_date="2026-10-30",
    )
    assert any("最小记录模式不再生成" in e for e in GOVERNANCE.validate_daily_records(project))


def test_minimal_profile_keeps_old_process_daily_compatible_but_blocks_new_append(
    project: Path,
) -> None:
    enable_minimal_records(project)
    record(project)
    assert GOVERNANCE.validate_daily_records(project) == []
    record(project, entries=[entry("old"), entry("new", recorded_at="2026-10-30T10:00:00+08:00")])
    assert any("最小记录模式不再生成" in e for e in GOVERNANCE.validate_daily_records(project))


def test_minimal_profile_allows_new_research_progress(project: Path) -> None:
    enable_minimal_records(project)
    group_record(project, [group_entry(project)])
    assert GOVERNANCE.validate_daily_records(project) == []


def add_requirement_type(project: Path) -> None:
    data = json.loads((project / "configs/features.yaml").read_text(encoding="utf-8"))
    data["record_policy"]["types"]["requirement"] = {
        "aliases": ["需求记录"],
        "directory": "research/achieve/00-项目管理/requirements",
        "filename_body": "用户要求",
        "label": "需求记录",
    }
    write_registry(project, data)


def test_minimal_profile_allows_new_requirement_daily(project: Path) -> None:
    add_requirement_type(project)
    enable_minimal_records(project)
    record(
        project,
        "requirement",
        [entry("scope", recorded_at="2026-10-30T10:00:00+08:00")],
        relative="research/achieve/00-项目管理/requirements/20261030-用户要求-需求记录.md",
        record_date="2026-10-30",
    )
    assert GOVERNANCE.validate_daily_records(project) == []


def test_requirement_history_requires_exact_registration_real_time_and_source(
    project: Path,
) -> None:
    add_requirement_type(project)
    path = project.parent / "achieve/00-项目管理/requirements/20261029-用户要求-需求记录.md"
    path.parent.mkdir(parents=True)
    source = path.parent / "original.md"
    source.write_text("原始用户要求。", encoding="utf-8")
    text = "---\nschema_version: research-requirement-history/1.0\nproject_id: research\nrecord_state: historical_readonly\nevent_date: 2026-10-29\ncompiled_at: 2026-10-30T12:00:00+08:00\n---\n\n[用户原话](original.md)\n"
    path.write_text(text, encoding="utf-8")
    assert any("未登记精确路径" in e for e in GOVERNANCE.validate_daily_records(project))
    configure(
        project,
        "historical_requirement_views",
        [path.relative_to(project.parent.parent).as_posix()],
    )
    assert GOVERNANCE.validate_daily_records(project) == []
    path.write_text(text.replace("original.md)", "missing.md)"), encoding="utf-8")
    assert any("引用不存在" in e for e in GOVERNANCE.validate_daily_records(project))
    path.write_text(text.replace("compiled_at:", "recorded_at:"), encoding="utf-8")
    assert any("compiled_at" in e for e in GOVERNANCE.validate_daily_records(project))
    assert any("不能伪造旧recorded_at" in e for e in GOVERNANCE.validate_daily_records(project))


def test_history_requirement_registry_cannot_exempt_directory(project: Path) -> None:
    directory = project.parent / "achieve/requirements"
    directory.mkdir(parents=True)
    configure(
        project,
        "historical_requirement_views",
        [directory.relative_to(project.parent.parent).as_posix()],
    )
    with pytest.raises(ValueError, match="现有精确文件"):
        GOVERNANCE.validate_daily_records(project)


def test_minimal_requires_explicit_daily_whitelist(project: Path) -> None:
    configure(project, "process_record_profile", "minimal")
    data = json.loads((project / "configs/features.yaml").read_text(encoding="utf-8"))
    data["record_policy"].pop("enabled_daily_types", None)
    write_registry(project, data)
    with pytest.raises(ValueError):
        GOVERNANCE.validate_daily_records(project)
