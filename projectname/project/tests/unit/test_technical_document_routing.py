"""当前技术对象、过程材料和旧来源绑定的放置约束。"""

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ENGINEERING_ROOT = next(
    p
    for p in Path(__file__).resolve().parents
    if (p / "scripts/f001_governance_validate.py").is_file()
)
SPEC = importlib.util.spec_from_file_location(
    "technical_routing", ENGINEERING_ROOT / "scripts/f001_governance_validate.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TechnicalDocumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "configs").mkdir()
        (self.root / "docs/interfaces").mkdir(parents=True)
        self.policy = {
            "enabled": True,
            "root": "docs",
            "root_entries": ["README.md", "api.md", "architecture.md"],
            "stable_directories": ["interfaces", "commands", "algorithms", "adr"],
            "pinned_paths": {},
        }

    def check(self):
        (self.root / "configs/features.yaml").write_text(
            json.dumps({"technical_documents": self.policy}), encoding="utf-8"
        )
        return MODULE.validate_technical_documents(self.root)

    def test_stable_object_is_allowed(self):
        (self.root / "docs/interfaces/receipt.md").write_text(
            "回执接口与错误约定。", encoding="utf-8"
        )
        self.assertEqual(self.check(), [])

    def test_root_timeline_and_patch_are_rejected(self):
        (self.root / "docs/20261030-任务-API说明.md").write_text("旧式散放。", encoding="utf-8")
        (self.root / "docs/interfaces/change.diff").write_text("补丁", encoding="utf-8")
        self.assertEqual(len(self.check()), 2)

    def test_frozen_source_cannot_be_silently_changed(self):
        p = self.root / "docs/20261025-旧来源-API说明.md"
        p.write_bytes(b"original")
        self.policy["pinned_paths"] = {
            p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        }
        self.assertEqual(self.check(), [])
        p.write_bytes(b"changed")
        self.assertTrue(any("来源绑定" in e for e in self.check()))

    def test_duplicate_current_object_is_rejected(self):
        for name in ["a", "b"]:
            (self.root / ("docs/interfaces/" + name + ".md")).write_text(
                "---\nobject_id: receipt\n---\n", encoding="utf-8"
            )
        self.assertTrue(any("多个当前正文" in e for e in self.check()))

    def test_declared_text_pin_is_portable_but_content_changes_fail(self):
        p = self.root / "docs/legacy.md"
        p.write_bytes(b"# Source\r\nOriginal text\r\n")
        self.policy["pin_hash_mode"] = "text-lf"
        self.policy["pinned_paths"] = {"docs/legacy.md": hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()}
        self.assertEqual(self.check(), [])
        p.write_bytes(b"# Source\nOriginal text\n")
        self.assertEqual(self.check(), [])
        p.write_bytes(b"# Source\nChanged text\n")
        self.assertTrue(any("来源绑定" in e for e in self.check()))
