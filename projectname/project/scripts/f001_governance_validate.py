"""F001 项目治理校验：只读检查文件职责、日记录唯一性、条目与引用；不判断科研性能。"""

# CLI 输出保留中文标点; 该例外仅作用于本工具的人类可读消息。
# ruff: noqa: RUF001, RUF002, T201, PERF401

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

FEATURES_FILE = Path("configs/features.yaml")
SUPERVISION_MARKER = "```project-supervision"
DATE_DOCUMENT_PATTERN = re.compile(r"^\d{8}-.+-.+\.[A-Za-z0-9]+$")


def load_structured_file(path: Path) -> dict[str, Any]:
    """读取 JSON 兼容的 YAML 注册表，避免引入额外运行依赖。"""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取结构化配置 {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"配置根节点必须是对象：{path}")
    return value


def validate_feature_registry(project_root: Path) -> list[str]:
    """检查功能编号、代码唯一性及必填字段。"""
    path = project_root / FEATURES_FILE
    errors: list[str] = []
    data = load_structured_file(path)
    features = data.get("features", [])
    if not isinstance(features, list):
        return ["features 必须是数组"]
    id_pattern = re.compile(str(data.get("feature_id_pattern", r"F\d{3}")))
    code_pattern = re.compile(str(data.get("feature_code_pattern", r"[A-Z][A-Z0-9_]+")))
    required = data.get("required_fields", [])
    seen_ids: set[str] = set()
    seen_codes: set[str] = set()
    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            errors.append(f"features[{index}] 必须是对象")
            continue
        missing = [name for name in required if not feature.get(name)]
        if missing:
            errors.append(f"features[{index}] 缺少字段：{', '.join(missing)}")
        feature_id = str(feature.get("feature_id", ""))
        feature_code = str(feature.get("feature_code", ""))
        if feature_id and not id_pattern.fullmatch(feature_id):
            errors.append(f"features[{index}] feature_id 不符合格式：{feature_id}")
        if feature_code and not code_pattern.fullmatch(feature_code):
            errors.append(f"features[{index}] feature_code 不符合格式：{feature_code}")
        if feature_id in seen_ids:
            errors.append(f"重复 feature_id：{feature_id}")
        if feature_code in seen_codes:
            errors.append(f"重复 feature_code：{feature_code}")
        seen_ids.add(feature_id)
        seen_codes.add(feature_code)
        if feature.get("validate_paths"):
            for field in ("implementation_paths", "test_paths", "evidence"):
                for relative in feature.get(field, []):
                    target = (project_root / str(relative)).resolve()
                    if not target.is_relative_to(project_root.parent.parent.resolve()):
                        errors.append(f"{feature_id} {field} 超出本项目边界：{relative}")
                    elif not target.exists():
                        errors.append(f"{feature_id} {field} 引用不存在：{relative}")
    return errors


def validate_project_layout(project_root: Path) -> list[str]:
    """检查治理入口、配置文件和脚本是否位于项目约定位置。"""
    errors: list[str] = []
    root_agents = project_root.parent.parent / "AGENTS.md"
    if not root_agents.exists():
        errors.append(f"缺少根级治理入口：{root_agents}")
    for relative in (
        FEATURES_FILE,
        Path("configs/skill-promotion.yaml"),
        Path("scripts/f001_governance_validate.py"),
    ):
        if not (project_root / relative).exists():
            errors.append(f"缺少治理资产：{relative.as_posix()}")
    for directory in project_root.iterdir():
        if directory.is_dir() and not any(directory.iterdir()):
            errors.append(f"发现未登记空目录：{directory.relative_to(project_root).as_posix()}")
    return errors


def validate_date_named_documents(project_root: Path) -> list[str]:
    """提示新增的根目录文档应采用日期化名称，固定技术入口不在此检查。"""
    warnings: list[str] = []
    fixed = {
        "AGENTS.md",
        "README.md",
        "SKILL.md",
        "PROGRAMMING_STANDARDS.md",
        "pyproject.toml",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "LICENSE",
        "CITATION.cff",
        "Dockerfile",
        ".gitignore",
        "uv.lock",
    }
    registry_path = project_root / FEATURES_FILE
    technical_enabled = registry_path.is_file() and load_structured_file(registry_path).get(
        "technical_documents", {}
    ).get("enabled")
    for path in project_root.rglob("*"):
        if technical_enabled and path.is_relative_to(project_root / "docs"):
            continue
        if (
            not path.is_file()
            or path.name in fixed
            or path.suffix not in {".md", ".html", ".json", ".yaml"}
        ):
            continue
        if ".git" in path.parts or "__pycache__" in path.parts or ".venv" in path.parts:
            continue
        if path.name.startswith(".") or path.name in {
            "base.yaml",
            "features.yaml",
            "skill-promotion.yaml",
        }:
            continue
        if not DATE_DOCUMENT_PATTERN.fullmatch(path.name) and path.parent.name not in {
            "docs",
            "examples",
        }:
            warnings.append(
                f"文档/配置未采用日期化名称（请确认固定名例外）：{path.relative_to(project_root).as_posix()}"
            )
    return warnings


SHANGHAI = timezone(timedelta(hours=8))
DAILY_SCHEMA = "daily-record/1.0"
ENTRY_PATTERN = re.compile(r"<!--\s*daily-entry\s+(\{.*?\})\s*-->", re.DOTALL)
ANCHOR_PATTERN = re.compile(r"\bid\s*=\s*[\"']([^\"']+)[\"']")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKIP_COMPONENTS = {".git", ".venv", "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache"}


def _repo_root(project_root: Path) -> Path:
    """治理配置中的记录目录相对于项目外层根，不是工程根。"""
    return project_root.parent.parent.resolve()


def _relative(path: Path, root: Path) -> str:
    return os.path.relpath(path, root).replace("\\", "/")


def _frontmatter(text: str) -> dict[str, str]:
    """只读文件开头的平面元数据，不把代码块中的模板当作记录。"""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip():
            result[key.strip()] = value.strip().strip("\"'")
    return result


def _policy(project_root: Path) -> dict[str, Any] | None:
    data = load_structured_file(project_root / FEATURES_FILE)
    policy = data.get("record_policy", {})
    if not isinstance(policy, dict):
        raise ValueError("record_policy 必须是对象")
    if not policy.get("enabled"):
        return None
    if policy.get("timezone") != "Asia/Shanghai" or not policy.get("project_id"):
        raise ValueError("record_policy 必须声明项目标识与Asia/Shanghai时区")
    date.fromisoformat(str(policy["effective_date"]))
    if policy.get("log_contract", "group-meeting/1.0") != "group-meeting/1.0":
        raise ValueError("不支持的科研日志契约")
    date.fromisoformat(str(policy.get("log_contract_effective_date", "2026-10-30")))
    if "enabled_daily_types" in policy or policy.get("process_record_profile") == "minimal":
        enabled = policy.get("enabled_daily_types")
        if not isinstance(enabled, list) or set(enabled) != {"requirement", "log"}:
            raise ValueError("最小日记录类型必须为requirement与log")
        if policy.get("process_record_profile") != "minimal":
            raise ValueError("启用最小日记录类型时必须使用minimal配置")
        date.fromisoformat(str(policy.get("minimal_records_effective_date", "2026-10-30")))
    types = policy.get("types")
    if not isinstance(types, dict) or not types:
        raise ValueError("record_policy.types 必须是非空对象")
    aliases: dict[str, str] = {}
    targets: set[str] = set()
    for canonical, spec in types.items():
        if not isinstance(spec, dict) or not all(
            spec.get(k) for k in ("directory", "filename_body", "label")
        ):
            raise ValueError(f"记录类型缺少目录/固定主体/标签：{canonical}")
        directory = Path(str(spec["directory"]))
        target = (_repo_root(project_root) / directory).resolve()
        if directory.is_absolute() or not target.is_relative_to(_repo_root(project_root)):
            raise ValueError(f"记录目录超出项目边界：{canonical}")
        identity = f"{directory.as_posix()}/{spec['filename_body']}-{spec['label']}"
        if identity in targets:
            raise ValueError("两个规范类型声明同一文件目标")
        targets.add(identity)
        for alias in [canonical, spec["label"], *spec.get("aliases", [])]:
            alias = str(alias)
            if alias in aliases and aliases[alias] != canonical:
                raise ValueError(f"记录类型别名冲突：{alias}")
            aliases[alias] = canonical
    legacy_paths = policy.get("legacy_paths", [])
    if not isinstance(legacy_paths, list):
        raise ValueError("legacy_paths必须是精确文件路径列表")
    for relative in legacy_paths:
        if not isinstance(relative, str) or any(char in relative for char in "*?["):
            raise ValueError("legacy_paths不允许通配符或目录前缀")
        path = (_repo_root(project_root) / relative).resolve()
        if (
            Path(relative).is_absolute()
            or not path.is_relative_to(_repo_root(project_root))
            or not path.is_file()
        ):
            raise ValueError(f"历史例外必须是本项目现有精确文件：{relative}")
    for relative in [
        *policy.get("historical_views", []),
        *policy.get("historical_requirement_views", []),
    ]:
        if not isinstance(relative, str) or any(char in relative for char in "*?["):
            raise ValueError("historical_views只允许精确文件路径")
        target = (_repo_root(project_root) / relative).resolve()
        if (
            Path(relative).is_absolute()
            or not target.is_relative_to(_repo_root(project_root))
            or not target.is_file()
        ):
            raise ValueError(f"历史科研视图不是本项目现有精确文件：{relative}")
    policy["_aliases"] = aliases
    return policy


def _record_date(value: str) -> date:
    normalized = f"{value[:4]}-{value[4:6]}-{value[6:]}" if len(value) == 8 else value
    return date.fromisoformat(normalized)


def _type_from_name(name: str, policy: dict[str, Any]) -> str | None:
    stem = Path(name).stem
    for alias in sorted(policy["_aliases"], key=len, reverse=True):
        if stem.endswith("-" + alias):
            return str(policy["_aliases"][alias])
    return None


def _anchors(text: str) -> set[str]:
    anchors = set(ANCHOR_PATTERN.findall(text))
    counts: dict[str, int] = {}
    for match in re.finditer(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", match.group(1).lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def _local_reference_errors(path: Path, text: str, repo: Path) -> list[str]:
    errors: list[str] = []
    for raw in LINK_PATTERN.findall(text):
        url = raw.strip().removeprefix("<").removesuffix(">")
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        if not target.is_relative_to(repo):
            errors.append(f"当前记录引用超出项目边界：{url}")
        elif not target.exists():
            errors.append(f"当前记录引用不存在：{url}")
        elif parsed.fragment and target.suffix.lower() in {".md", ".html"}:
            try:
                content = text if target == path else target.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError):
                errors.append(f"引用无法读取：{url}")
                continue
            if unquote(parsed.fragment) not in _anchors(content):
                errors.append(f"当前记录锚点不存在：{url}")
    return errors


GROUP_MEETING_CONTRACT = "group-meeting/1.0"
RESEARCH_WORK_KINDS = {
    "literature",
    "method",
    "performance",
    "analysis",
    "writing",
    "research_blocker",
}
GUIDE_LIMITS = {1: 14, 2: 16, 3: 17, 4: 14, 5: 14, 6: 15, 7: 14}


def _locatable_source(value: str, path: Path, repo: Path) -> bool:
    """验证来源能定位到文件/显式锚点，不评价来源能否支持科学结论。"""
    markdown = LINK_PATTERN.fullmatch(value.strip())
    reference = markdown.group(1) if markdown else value.strip()
    parsed = urlsplit(reference.strip("<>"))
    if parsed.scheme or parsed.netloc or not parsed.path:
        return False
    source = (repo / unquote(parsed.path)).resolve()
    if not source.exists():
        source = (path.parent / unquote(parsed.path)).resolve()
    if not source.is_relative_to(repo) or not source.is_file():
        return False
    if parsed.fragment and source.suffix.lower() in {".md", ".html"}:
        try:
            return unquote(parsed.fragment) in _anchors(source.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError):
            return False
    return True


def _group_meeting_errors(
    entry: dict[str, Any], body: str, path: Path, policy: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if entry.get("report_contract") != GROUP_MEETING_CONTRACT:
        errors.append("新科研日志必须声明report_contract=group-meeting/1.0")
    if not isinstance(entry.get("work_kind"), str) or entry["work_kind"] not in RESEARCH_WORK_KINDS:
        errors.append("科研日志work_kind不在允许的研究工作范围")
    required = (
        "research_point",
        "research_source",
        "research_question",
        "actions",
        "result",
        "interpretation",
        "limitations",
        "next_step",
        "evidence",
        "guide_questions",
    )
    for key in required:
        value = entry.get(key)
        expected = list if key in {"evidence", "guide_questions"} else str
        if (
            not isinstance(value, expected)
            or not value
            or (isinstance(value, str) and not value.strip())
        ):
            errors.append(f"组会日志缺少实际{key}")
    questions = entry.get("guide_questions")
    if not isinstance(questions, list) or not questions:
        errors.append("guide_questions必须是非空问题编号列表")
    else:
        for question in questions:
            match = re.fullmatch(r"4\.([1-7])\.Q([1-9][0-9]*)", str(question))
            if not match or int(match.group(2)) > GUIDE_LIMITS[int(match.group(1))]:
                errors.append(f"研究问题编号不存在：{question}")
    repo = _repo_root(path) if not policy.get("_repo") else Path(policy["_repo"])
    source = entry.get("research_source")
    if not isinstance(source, str) or not _locatable_source(source, path, repo):
        errors.append("research_source必须定位到本项目来源文件或锚点")
    evidence = entry.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence必须是非空来源路径列表")
    else:
        for reference in evidence:
            if not isinstance(reference, str) or not _locatable_source(reference, path, repo):
                errors.append(f"科研证据无法定位：{reference}")
    if str(entry.get("work_kind")) in {"performance", "analysis"}:
        for key in ("comparison_conditions", "metrics"):
            value = entry.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"性能/分析日志缺少{key}")
    if re.search(
        r"^#{1,6}\s*(?:附录[：:]\s*)?(?:管理信息|工程附录|代码正确性验证)", body, re.MULTILINE
    ):
        errors.append("科研日志不得包含工程或管理附录")
    return errors


def _entry_errors(
    path: Path,
    text: str,
    canonical: str,
    day: date,
    seen_ids: set[str],
    seen_events: set[tuple[str, str]],
    policy: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    matches = list(ENTRY_PATTERN.finditer(text))
    if not matches:
        return ["日文件没有真实独立条目"]
    for index, match in enumerate(matches):
        encoded = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]
        try:
            entry = json.loads(encoded)
        except json.JSONDecodeError:
            errors.append("daily-entry元数据不是有效JSON")
            continue
        if not isinstance(entry, dict):
            errors.append("daily-entry元数据必须是对象")
            continue
        identifier = str(entry.get("entry_id", ""))
        if not identifier or re.search(r"[\s\"'<>#]", identifier):
            errors.append("条目ID缺失或包含不安全字符")
        elif identifier in seen_ids:
            errors.append(f"条目ID重复：{identifier}")
        else:
            seen_ids.add(identifier)
        anchor = "entry-" + identifier
        if len(re.findall(r"\bid\s*=\s*[\"']" + re.escape(anchor) + r"[\"']", text)) != 1:
            errors.append(f"条目锚点缺失或重复：{anchor}")
        for key in ("event_key", "attempt_id", "status"):
            if not entry.get(key):
                errors.append(f"条目缺少{key}：{identifier}")
        event = (str(entry.get("event_key", "")), str(entry.get("attempt_id", "")))
        if event in seen_events:
            errors.append(f"事件和尝试重复：{identifier}")
        seen_events.add(event)
        for key in ("recorded_at", "occurred_at"):
            try:
                stamp = datetime.fromisoformat(str(entry[key]).replace("Z", "+00:00"))
                if stamp.tzinfo is None:
                    raise ValueError("缺少时区")
                if key == "recorded_at" and stamp.astimezone(SHANGHAI).date() != day:
                    errors.append(f"记录时间与上海记录日不符：{identifier}")
            except (KeyError, TypeError, ValueError):
                errors.append(f"条目{key}缺失或不是带时区时间：{identifier}")
        if canonical == "log":
            contract_policy = policy or {}
            effective = str(contract_policy.get("log_contract_effective_date", "2026-10-30"))
            try:
                stamp = datetime.fromisoformat(
                    str(entry.get("recorded_at", "")).replace("Z", "+00:00")
                )
                recorded_day = (
                    stamp.astimezone(SHANGHAI).date().isoformat()
                    if stamp.tzinfo
                    else day.isoformat()
                )
            except ValueError:
                recorded_day = day.isoformat()
            if (
                entry.get("report_contract")
                or recorded_day >= effective
                or day.isoformat() >= effective
            ):
                errors.extend(_group_meeting_errors(entry, body, path, contract_policy))
            if not entry.get("research_point") or not entry.get("research_source"):
                errors.append(f"科研日志缺少研究要点及出处：{identifier}")
            if str(entry.get("work_kind")) in {"correctness", "engineering", "management"}:
                errors.append(f"工程/管理事件不能进入科研日志：{identifier}")
    return [f"{path.name}：{error}" for error in errors]


def _historical_view_errors(
    path: Path, metadata: dict[str, str], policy: dict[str, Any], repo: Path
) -> list[str]:
    """历史科学提炼视图是获准的只读对象，不冒充当时产生的日记录。"""
    errors: list[str] = []
    relative = _relative(path, repo)
    requirement_view = metadata.get("schema_version") == "research-requirement-history/1.0"
    registry = "historical_requirement_views" if requirement_view else "historical_views"
    if relative not in policy.get(registry, []):
        return [f"历史科研视图未登记精确路径：{relative}"]
    if metadata.get("record_state") != "historical_readonly":
        errors.append(f"历史科研视图必须只读：{relative}")
    if metadata.get("project_id") != str(policy["project_id"]):
        errors.append(f"历史科研视图项目不符：{relative}")
    try:
        event_day = date.fromisoformat(metadata["event_date"])
        compiled = datetime.fromisoformat(metadata["compiled_at"].replace("Z", "+00:00"))
        if compiled.tzinfo is None or compiled.astimezone(SHANGHAI).date() < event_day:
            raise ValueError("实际整理时间无效")
        spec = policy["types"]["requirement" if requirement_view else "log"]
        expected = (
            repo
            / str(spec["directory"])
            / f"{event_day:%Y%m%d}-{spec['filename_body']}-{spec['label']}.md"
        )
        if expected.resolve() != path.resolve():
            errors.append(f"历史科研视图事件日与落点不符：{relative}")
    except (KeyError, ValueError):
        errors.append(f"历史科研视图缺少真实event_date/compiled_at：{relative}")
    if "recorded_at" in metadata:
        errors.append(f"历史科研视图不能伪造旧recorded_at：{relative}")
    return errors


def validate_daily_records(project_root: Path) -> list[str]:
    """只校验启用后的当前记录；旧原件与显式历史路径不自动迁移。"""
    errors: list[str] = []
    policy = _policy(project_root)
    if policy is None:
        return errors
    repo = _repo_root(project_root)
    policy["_repo"] = str(repo)
    effective = date.fromisoformat(str(policy["effective_date"]))
    seen: dict[tuple[str, date, str], Path] = {}
    seen_ids: set[str] = set()
    seen_events: set[tuple[str, str]] = set()
    export_map = {str(item["path"]): str(item["source"]) for item in policy.get("exports", [])}
    for path in sorted(repo.rglob("*")):
        if any(part in SKIP_COMPONENTS or part == "node_modules" for part in path.parts):
            continue
        if not path.is_file():
            continue
        relative = _relative(path, repo)
        if not path.resolve().is_relative_to(repo):
            errors.append(f"记录路径超出本项目：{relative}")
            continue
        if relative in policy.get("legacy_paths", []):
            continue
        named_type = _type_from_name(path.name, policy)
        name_match = re.match(r"^(\d{8})-", path.name)
        try:
            with path.open("rb") as handle:
                prefix = handle.read(65536)
            try:
                text = prefix.decode("utf-8-sig").replace("\r\n", "\n")
            except UnicodeError:
                if not named_type:
                    continue
                text = ""
            metadata = _frontmatter(text)
            json_schema = re.search(r'"schema_version"\s*:\s*"daily-record', text)
            if json_schema and text.lstrip().startswith("{"):
                candidate = json.loads(path.read_text(encoding="utf-8-sig"))
                if isinstance(candidate, dict):
                    metadata = {
                        key: str(value)
                        for key, value in candidate.items()
                        if not isinstance(value, (dict, list))
                    }
            daily_schema = metadata.get("schema_version", "").startswith("daily-record")
            if (named_type or daily_schema) and text:
                text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError, json.JSONDecodeError):
            errors.append(f"记录候选无法读取：{relative}")
            continue
        if metadata.get("schema_version") in {
            "research-history/1.0",
            "research-requirement-history/1.0",
        }:
            errors.extend(_historical_view_errors(path, metadata, policy, repo))
            errors.extend(_local_reference_errors(path, text, repo))
            if ENTRY_PATTERN.search(text):
                errors.append(f"历史科研视图不能伪造活动日条目：{relative}")
            continue
        if not named_type and not daily_schema:
            continue
        try:
            filename_day = _record_date(name_match.group(1)) if name_match else None
            declared_day = (
                _record_date(metadata["record_date"]) if metadata.get("record_date") else None
            )
        except ValueError:
            errors.append(f"记录日期无效：{relative}")
            continue
        if (
            not daily_schema
            and filename_day
            and filename_day < effective
            and (not declared_day or declared_day < effective)
        ):
            continue
        declared_export = metadata.get("derived_from") and (
            metadata.get("read_only") == "true" or metadata.get("record_state") == "exported"
        )
        if relative in export_map or declared_export:
            declared_source = export_map.get(relative) or metadata["derived_from"]
            source_part = unquote(urlsplit(str(declared_source)).path)
            source = (repo / source_part).resolve()
            if not source.exists() and declared_export:
                source = (path.parent / source_part).resolve()
            if not source.is_relative_to(repo) or not source.is_file() or source == path:
                errors.append(f"只读导出母版无效：{relative}")
                continue
            try:
                mother = _frontmatter(source.read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError):
                errors.append(f"只读导出母版无法读取：{relative}")
                continue
            if mother.get("schema_version") != DAILY_SCHEMA or mother.get("derived_from"):
                errors.append(f"只读导出必须引用真实日记录母版：{relative}")
            if metadata.get("record_type") and policy["_aliases"].get(
                metadata["record_type"]
            ) != policy["_aliases"].get(mother.get("record_type", "")):
                errors.append(f"导出与母版记录类型不符：{relative}")
            if metadata.get("record_date") and metadata["record_date"] != mother.get("record_date"):
                errors.append(f"导出与母版记录日不符：{relative}")
            continue
        declared = metadata.get("record_type", "")
        canonical = policy["_aliases"].get(declared) if declared else named_type
        if canonical not in policy["types"]:
            errors.append(f"未知规范记录类型：{relative}")
            continue
        if named_type and canonical != named_type:
            errors.append(f"记录类型与文件名矛盾：{relative}")
        day = declared_day or filename_day
        if day is None:
            errors.append(f"日文件缺少记录日：{relative}")
            continue
        minimal_cutoff = date.fromisoformat(
            str(policy.get("minimal_records_effective_date", "2026-10-30"))
        )
        is_new = day >= minimal_cutoff
        for encoded in ENTRY_PATTERN.findall(text):
            try:
                stamp = datetime.fromisoformat(
                    str(json.loads(encoded).get("recorded_at", "")).replace("Z", "+00:00")
                )
                is_new = is_new or (
                    stamp.tzinfo is not None and stamp.astimezone(SHANGHAI).date() >= minimal_cutoff
                )
            except (ValueError, TypeError, AttributeError):
                pass  # 条目本身的JSON/时间错误由后续独立检查报告。
        enabled_types = policy.get("enabled_daily_types")
        if (
            policy.get("process_record_profile") == "minimal"
            and isinstance(enabled_types, list)
            and is_new
            and canonical not in enabled_types
        ):
            errors.append(f"最小记录模式不再生成该类型日文件：{canonical}；{relative}")
        key = (str(policy["project_id"]), day, str(canonical))
        if key in seen:
            errors.append(f"同日同类型多份记录：{_relative(seen[key], repo)} 与 {relative}")
        seen[key] = path
        spec = policy["types"][canonical]
        expected = (
            repo
            / str(spec["directory"])
            / f"{day:%Y%m%d}-{spec['filename_body']}-{spec['label']}.md"
        )
        if path.resolve() != expected.resolve():
            errors.append(f"记录落点或固定文件名不符：{relative}；应为{_relative(expected, repo)}")
        if metadata.get("schema_version") != DAILY_SCHEMA:
            errors.append(f"当前日文件缺少或不支持{DAILY_SCHEMA}元数据：{relative}")
        if metadata.get("record_profile") and metadata["record_profile"] != str(
            policy.get("profile", "research")
        ):
            errors.append(f"日文件用途不符：{relative}")
        if (
            metadata.get("project_id") != str(policy["project_id"])
            or metadata.get("timezone") != "Asia/Shanghai"
        ):
            errors.append(f"日文件项目/时区不符：{relative}")
        if filename_day != day:
            errors.append(f"文件日期与记录日不符：{relative}")
        errors.extend(_entry_errors(path, text, str(canonical), day, seen_ids, seen_events, policy))
        errors.extend(_local_reference_errors(path, text, repo))
    return errors


def validate_artifact_routes(project_root: Path) -> list[str]:
    """在明确配置的作用域检查单一责任与真实当前入口，不推断未声明领域。"""
    errors: list[str] = []
    data = load_structured_file(project_root / FEATURES_FILE)
    artifact = data.get("artifact_policy", {})
    repo = _repo_root(project_root)
    checked: set[Path] = set()
    for relative in artifact.get("governed_paths", []):
        scope = (project_root / str(relative)).resolve()
        if not scope.is_relative_to(repo):
            errors.append(f"归属检查范围超出项目：{relative}")
            continue
        for path in scope.rglob("*"):
            if not path.is_file() or any(part in SKIP_COMPONENTS for part in path.parts):
                continue
            if path.resolve() in checked:
                continue
            checked.add(path.resolve())
            name = _relative(path, project_root)
            owners = [
                rule
                for rule in artifact.get("ownership_rules", [])
                if fnmatch.fnmatchcase(name, str(rule["pattern"]))
            ]
            if len(owners) != 1 or not owners[0].get("owner"):
                errors.append(f"文件应有且仅有一个责任规则：{name}")
    policy = _policy(project_root)
    if policy:
        for label, relative in policy.get("current_entries", {}).items():
            path = (repo / str(relative)).resolve()
            if not path.is_relative_to(repo) or not path.is_file():
                errors.append(f"当前入口不存在或超出项目：{label}={relative}")
    return errors


def validate_technical_documents(engineering_root: Path) -> list[str]:
    """检查当前技术对象归属及精确来源绑定，不评价科学结论。"""
    import hashlib

    registry = next(
        (
            engineering_root / name
            for name in ("configs/features.yaml", "config/feature-registry.yaml")
            if (engineering_root / name).is_file()
        ),
        None,
    )
    if registry is None:
        return []
    policy = json.loads(registry.read_text(encoding="utf-8-sig")).get("technical_documents", {})
    if not policy.get("enabled"):
        return []
    root = engineering_root.resolve()
    home = (root / policy.get("root", "docs")).resolve()
    if not home.is_relative_to(root):
        return ["技术文档目录越界"]
    errors = []
    reader = policy.get("profile") == "reader"
    reader_entries = {"README.md", "项目技术说明.md", "使用指南.md", "结果说明与适用范围.md"}
    if reader:
        if set(policy.get("root_entries", [])) != reader_entries:
            errors.append("读者文档入口必须是规定的四份文档")
        state = policy.get("delivery_state", "ready")
        if state not in {"ready", "not_started"}:
            errors.append("读者文档交付状态无效")
        required = reader_entries if state == "ready" else {"README.md"}
        for filename in sorted(required):
            if not (home / filename).is_file():
                errors.append("缺少读者文档：" + filename)
        if state == "not_started" and (home / "README.md").is_file():
            navigation = (home / "README.md").read_text(encoding="utf-8-sig")
            if not any(word in navigation for word in ("尚未建立", "尚无", "未建立")):
                errors.append("未开始文档须在README明确尚未建立")
    pins = policy.get("pinned_paths", {})
    baseline = set(policy.get("baseline_paths", []))
    identities = set()
    for relative, expected in pins.items():
        source = (root / relative).resolve()
        if (
            not source.is_relative_to(home)
            or not source.is_file()
            or hashlib.sha256(source.read_bytes().replace(b"\r\n", b"\n") if policy.get("pin_hash_mode") == "text-lf" else source.read_bytes()).hexdigest() != expected
        ):
            errors.append("技术原件来源绑定改变或缺失：" + relative)
    for path in home.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(home):
            errors.append("技术文档链接越界：" + relative)
            continue
        if relative in pins or relative in baseline or path.name == ".gitkeep":
            continue
        local = path.relative_to(home)
        if (path.parent == home and path.name not in policy.get("root_entries", [])) or (
            len(local.parts) > 1 and local.parts[0] not in policy.get("stable_directories", [])
        ):
            errors.append("技术文档缺少明确对象归属：" + relative)
        if path.suffix in {".diff", ".txt"} or any(
            path.name.endswith("-" + kind + ".md")
            for kind in (
                "工作契约",
                "工程交付记录",
                "检查记录",
                "修订记录",
                "技术诊断",
                "工程复验记录",
                "源码记录",
            )
        ):
            errors.append("过程材料、补丁或源码快照不得进入当前docs：" + relative)
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8-sig")
            if reader:
                # 读者文档不使用机器元数据头。旧精确绑定原件已在前面排除。
                if re.match(r"\A---\s*\n.*?\n---\s*\n", text, re.DOTALL):
                    errors.append("读者正文不得包含frontmatter机器元数据：" + relative)
                body = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)
                machine_fields = re.search(
                    r"(?mi)^\s*(?:[-*]\s*)?(?:sha256|source_sha256|schema_version|run_id|entry_id|object_id|implementation_paths)\s*[:=|]",
                    body,
                )
                machine_block = re.search(r"(?mi)^```(?:json|yaml|toml|python|jsonl)\s*$", body)
                process_output = re.search(r"\b[0-9]+\s+passed\b|\b[0-9a-fA-F]{64}\b", body)
                if machine_fields or machine_block or process_output:
                    errors.append("机器字段、代码清单或检查成绩不得进入读者正文：" + relative)
            if "daily-record/1.0" in text[:512]:
                errors.append("日记录不得进入docs：" + relative)
            for line in text[:1500].splitlines():
                if line.startswith("object_id:"):
                    identity = line.partition(":")[2].strip()
                    if identity in identities:
                        errors.append("技术对象存在多个当前正文：" + identity)
                    identities.add(identity)
    return errors


def validate_achievement_layout(engineering_root: Path) -> list[str]:
    """可选的新增成果归属检查。旧精确基线不迁移，不要求所有分类目录存在。"""
    registry = next(
        (
            engineering_root / name
            for name in ("configs/features.yaml", "config/feature-registry.yaml")
            if (engineering_root / name).is_file()
        ),
        None,
    )
    if registry is None:
        return []
    policy = json.loads(registry.read_text(encoding="utf-8-sig")).get("achievement_layout", {})
    if not policy.get("enabled"):
        return []
    repo = engineering_root.parent.parent.resolve()
    errors = []
    covered = set()
    process_suffixes = {
        ".diff",
        ".patch",
        ".log",
        ".aux",
        ".bcf",
        ".blg",
        ".toc",
        ".fls",
        ".fdb_latexmk",
    }
    for spec in policy.get("roots", []):
        home = (engineering_root / spec["path"]).resolve()
        if Path(spec["path"]).is_absolute() or not home.is_relative_to(repo):
            errors.append("成果归属根目录越界：" + str(spec["path"]))
            continue
        baseline = set(spec.get("baseline_paths", []))
        legacy_dirs = set()
        for relative in baseline:
            value = Path(relative)
            if (
                value.is_absolute()
                or not (home / value).resolve().is_relative_to(home)
                or any(c in relative for c in "*?[")
            ):
                errors.append("成果旧基线必须是精确相对文件：" + relative)
                continue
            legacy_dirs.update(parent.as_posix() for parent in value.parents if parent != Path("."))
        folders = spec.get("folders", {})
        if not isinstance(folders, dict) or not all(
            isinstance(v, dict) and v.get("purpose") for v in folders.values()
        ):
            errors.append("成果分类必须声明唯一用途")
            continue
        if not home.exists():
            continue
        if not home.is_dir():
            errors.append("成果归属根不是文件夹：" + str(spec["path"]))
            continue
        for path in home.rglob("*"):
            relative = path.relative_to(home).as_posix()
            if path.is_symlink() or not path.resolve().is_relative_to(home):
                errors.append("成果链接越界或未经登记：" + relative)
                continue
            if path.is_file() and relative in baseline:
                continue
            parts = path.relative_to(home).parts
            if path.is_file():
                identity = path.resolve()
                if identity in covered:
                    errors.append("成果文件匹配多个受管根：" + relative)
                covered.add(identity)
            if len(parts) == 1:
                if path.is_file() and path.name not in spec.get("entry_filenames", ["README.md"]):
                    errors.append("成果根目录不允许新文件散放：" + relative)
                elif path.is_dir() and parts[0] not in folders and relative not in legacy_dirs:
                    errors.append("未知成果文件夹：" + relative)
                continue
            category = folders.get(parts[0])
            if category is None:
                if not path.is_dir() or relative not in legacy_dirs:
                    errors.append("文件没有成果分类归属：" + relative)
                continue
            if len(parts) == 2:
                if path.is_file() and path.name not in category.get(
                    "object_entry_filenames", ["README.md"]
                ):
                    errors.append("成果必须进入稳定对象文件夹：" + relative)
                elif (
                    path.is_dir()
                    and re.match(
                        r"(?i)^(?:(?:PI|MB|EX|CR)-[EPX][0-9]+|agent[0-9_-]*|task[-_].*|[0-9]{8}(?:[-_].*)?)$",
                        parts[1],
                    )
                    and relative not in legacy_dirs
                ):
                    errors.append("成果对象不能按日期任务或Agent分散：" + relative)
                continue
            if re.match(
                r"(?i)^(?:(?:PI|MB|EX|CR)-[EPX][0-9]+|agent[0-9_-]*|task[-_].*|[0-9]{8}(?:[-_].*)?)$",
                parts[1],
            ):
                errors.append("成果对象不能按日期任务或Agent分散：" + relative)
            if len(parts) >= 4 or (len(parts) == 3 and path.is_dir()):
                object_spec = category.get("objects", {}).get(parts[1], {})
                child_folders = object_spec.get(
                    "child_folders",
                    object_spec.get(
                        "object_child_folders", category.get("object_child_folders", {})
                    ),
                )
                if parts[2] not in child_folders:
                    errors.append("未知深层成果文件夹归属：" + relative)
            if path.is_file() and (
                path.suffix.lower() in process_suffixes
                or any(
                    path.stem == kind or path.stem.endswith("-" + kind)
                    for kind in policy.get("rejected_types", [])
                )
            ):
                errors.append("过程稿或编译证据不应新增到成果区：" + relative)
    return errors


def run(project_root: Path) -> int:
    try:
        errors = (
            validate_feature_registry(project_root)
            + validate_project_layout(project_root)
            + validate_daily_records(project_root)
            + validate_artifact_routes(project_root)
            + validate_technical_documents(project_root)
            + validate_achievement_layout(project_root)
        )
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"ERROR: 治理配置或记录无法检查：{exc}")
        return 1
    warnings = validate_date_named_documents(project_root)
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    print(f"治理校验完成：ERROR={len(errors)} WARNING={len(warnings)}")
    return 1 if errors else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="F001 项目治理只读校验器")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--check", action="store_true", help="执行检查；默认同样执行，保留参数用于统一入口"
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    sys.exit(run(arguments.project_root.resolve()))
