"""F001 项目治理校验：只读检查功能注册表、目录边界和基础命名约束。"""

# CLI 输出保留中文标点; 该例外仅作用于本工具的人类可读消息。
# ruff: noqa: RUF001, RUF002, T201, PERF401

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

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


def run(project_root: Path) -> int:
    errors = validate_feature_registry(project_root) + validate_project_layout(project_root)
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
