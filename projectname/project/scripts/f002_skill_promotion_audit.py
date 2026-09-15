"""F002 Skill 晋升审查：只读检查项目 Skill 晋升证据，不执行全局安装。"""

# CLI 输出保留中文标点; 该例外仅作用于本工具的人类可读消息。
# ruff: noqa: RUF001, RUF002, T201

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REGISTRY = Path("configs/skill-promotion.yaml")


def load_registry(project_root: Path) -> dict[str, Any]:
    try:
        value = json.loads((project_root / REGISTRY).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 Skill 晋升登记：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("Skill 晋升登记根节点必须是对象")
    return value


def run(project_root: Path) -> int:
    data = load_registry(project_root)
    required = data.get("required_evidence", [])
    errors: list[str] = []
    promotions = data.get("promotions", [])
    if not isinstance(promotions, list):
        errors.append("promotions 必须是数组")
        promotions = []
    for index, item in enumerate(promotions):
        if not isinstance(item, dict):
            errors.append(f"promotions[{index}] 必须是对象")
            continue
        missing = [key for key in required if not item.get(key)]
        if missing:
            errors.append(f"promotions[{index}] 缺少证据：{', '.join(missing)}")
    if not promotions:
        print("INFO: 当前没有待晋升 Skill；保持项目级试点，不执行全局安装。")
    for message in errors:
        print(f"ERROR: {message}")
    print(f"Skill 晋升审查完成：ERROR={len(errors)}，全局安装=未执行")
    return 1 if errors else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="F002 Skill 晋升只读审查器")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(run(parse_args().project_root.resolve()))
