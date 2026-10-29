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
    for path in project_root.rglob("*"):
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


def _entry_errors(
    path: Path,
    text: str,
    canonical: str,
    day: date,
    seen_ids: set[str],
    seen_events: set[tuple[str, str]],
) -> list[str]:
    errors: list[str] = []
    matches = ENTRY_PATTERN.findall(text)
    if not matches:
        return ["日文件没有真实独立条目"]
    for encoded in matches:
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
            if not entry.get("research_point") or not entry.get("research_source"):
                errors.append(f"科研日志缺少研究要点及出处：{identifier}")
            if entry.get("work_kind") in {"correctness", "engineering", "management"}:
                errors.append(f"工程/管理事件不能进入科研日志：{identifier}")
    return [f"{path.name}：{error}" for error in errors]


def validate_daily_records(project_root: Path) -> list[str]:
    """只校验启用后的当前记录；旧原件与显式历史路径不自动迁移。"""
    errors: list[str] = []
    policy = _policy(project_root)
    if policy is None:
        return errors
    repo = _repo_root(project_root)
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
        errors.extend(_entry_errors(path, text, str(canonical), day, seen_ids, seen_events))
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


def run(project_root: Path) -> int:
    try:
        errors = (
            validate_feature_registry(project_root)
            + validate_project_layout(project_root)
            + validate_daily_records(project_root)
            + validate_artifact_routes(project_root)
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
