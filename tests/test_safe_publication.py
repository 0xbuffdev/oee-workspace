#!/usr/bin/env python3
"""WS-I04: publication integrity and resource-guide fail-closed tests."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_script(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


publisher = load_script("publish-workspace.py", "oee_safe_publish")
guides = load_script("render-resource-guides.py", "oee_safe_guides")


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "learner"
        self.root.mkdir()
        self.stage = self.root / ".oee-stage-test"
        self.stage.mkdir()
        self.course_paths = [
            Path(part) / "SEF" / "SEF1" for part in ("labs", "exercises", "notes")
        ]
        for rel in self.course_paths:
            path = self.stage / rel
            path.mkdir(parents=True)
            (path / "README.md").write_text(str(rel), encoding="utf-8")

    def test_three_course_directories_publish_without_copy(self):
        installed = publisher.publish(self.root, self.stage, self.course_paths)
        self.assertEqual(installed, [self.root / rel for rel in self.course_paths])
        for rel in self.course_paths:
            self.assertEqual((self.root / rel / "README.md").read_text(), str(rel))
            self.assertFalse((self.stage / rel).exists())

    def test_existing_learner_file_is_preserved_and_no_other_path_is_published(self):
        target = self.root / self.course_paths[0]
        target.mkdir(parents=True)
        (target / "README.md").write_text("My work", encoding="utf-8")
        with self.assertRaisesRegex(publisher.PublishError, "already exists"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertEqual((target / "README.md").read_text(), "My work")
        self.assertFalse((self.root / self.course_paths[1]).exists())
        self.assertFalse((self.root / self.course_paths[2]).exists())

    def test_reject_symlinked_parent_even_when_it_targets_safe_directory(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / "labs").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(publisher.PublishError, "real directory"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertEqual(list(outside.iterdir()), [])

    def test_reject_symlink_at_destination_and_preserve_target(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "evidence.txt").write_text("mine", encoding="utf-8")
        directory = self.root / "labs" / "SEF"
        directory.mkdir(parents=True)
        (directory / "SEF1").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(publisher.PublishError, "already exists"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertEqual((outside / "evidence.txt").read_text(), "mine")

    def test_missing_stage_aborts_before_any_publish(self):
        (self.stage / self.course_paths[2] / "README.md").unlink()
        (self.stage / self.course_paths[2]).rmdir()
        with self.assertRaisesRegex(publisher.PublishError, "staged output"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertFalse((self.root / self.course_paths[0]).exists())

    def test_failed_first_rename_preserves_stage(self):
        with patch.object(publisher.os, "rename", side_effect=OSError("injected")):
            with self.assertRaisesRegex(publisher.PublishError, "publishing stopped"):
                publisher.publish(self.root, self.stage, self.course_paths)
        self.assertFalse((self.root / self.course_paths[0]).exists())
        self.assertTrue((self.stage / self.course_paths[0] / "README.md").exists())

    def test_partial_publish_does_not_delete_learner_files(self):
        real_rename = os.rename
        calls = []

        def fail_second(src, target):
            calls.append((src, target))
            if len(calls) == 2:
                raise OSError("injected second rename failure")
            real_rename(src, target)

        with patch.object(publisher.os, "rename", side_effect=fail_second):
            with self.assertRaisesRegex(publisher.PublishError, "after 1 directories"):
                publisher.publish(self.root, self.stage, self.course_paths)
        self.assertTrue((self.root / self.course_paths[0] / "README.md").exists())
        self.assertFalse((self.root / self.course_paths[1]).exists())

    def test_reject_outside_stage_and_invalid_project(self):
        other = Path(self.temp.name) / ".oee-stage-elsewhere"
        other.mkdir()
        with self.assertRaisesRegex(publisher.PublishError, "directly inside"):
            publisher.publish(self.root, other, self.course_paths)
        self.assertEqual(publisher.main([
            "--workspace", str(self.root), "--stage", str(self.stage),
            "--project", "ledgerlab",
        ]), 1)

    def test_project_install(self):
        rel = Path("projects") / "SEF10"
        (self.stage / rel).mkdir(parents=True)
        (self.stage / rel / "BRIEF.md").write_text("pinned", encoding="utf-8")
        publisher.publish(self.root, self.stage, [rel])
        self.assertEqual((self.root / rel / "BRIEF.md").read_text(), "pinned")


class GuidePublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog_root = self.root / "resources" / "catalog"
        self.map_root = self.root / "resources" / "mappings"
        self.guide_root = self.root / "resources" / "guides"
        (self.catalog_root / "online").mkdir(parents=True)
        (self.map_root / "SEF").mkdir(parents=True)
        self.catalog = {
            "id": "R1", "kind": "course-material", "title": "A free resource",
            "access": {"mode": "free", "url": "https://example.org/"},
            "verification": {"status": "verified", "basis": "Test fixture",
                             "checkedOn": "2026-11-20"}
        }
        (self.catalog_root / "online" / "R1.json").write_text(
            json.dumps(self.catalog), encoding="utf-8")
        self.mapping = {
            "schemaVersion": 2, "status": "reviewed",
            "curriculum": {
                "repository": "0xbuffdev/open-engineering-education",
                "revision": "a" * 40, "specification": "v0.2.0",
                "course": "SEF1", "path": "curriculum/SEF/SEF1.md"
            },
            "modules": [{
                "number": 1, "title": "Bits",
                "coverage": "partial", "gap": "Other work still required",
                "resources": [{
                    "resource": "R1", "role": "optional",
                    "part": {"type": "topics", "titles": ["Binary"]},
                    "purpose": "Read for additional practice",
                    "verification": "verified"
                }]
            }]
        }
        self.write_mapping()

    def write_mapping(self):
        (self.map_root / "SEF" / "SEF1.json").write_text(
            json.dumps(self.mapping), encoding="utf-8")

    def scoped(self):
        return (
            patch.object(guides, "ROOT", self.root),
            patch.object(guides, "CATALOG", self.catalog_root),
            patch.object(guides, "MAPPINGS", self.map_root),
            patch.object(guides, "GUIDES", self.guide_root),
        )

    def render_under(self, *, source_status=0):
        with self.scoped()[0], self.scoped()[1], self.scoped()[2], self.scoped()[3]:
            with patch.object(guides.subprocess, "run",
                              return_value=subprocess.CompletedProcess(
                                  [], source_status, "", "unsupported source")):
                return list(guides.outputs("SEF1", self.root / "oee"))

    def test_reject_draft_even_if_toolkit_structural_check_would_pass(self):
        self.mapping["status"] = "draft"
        self.write_mapping()
        with self.assertRaisesRegex(ValueError, "unreviewed_map"):
            self.render_under()

    def test_reject_wrong_source_before_rendering(self):
        with self.assertRaisesRegex(ValueError, "pinned-source validation"):
            self.render_under(source_status=3)

    def test_immutable_render_bytes_for_same_reviewed_input(self):
        one = self.render_under()
        two = self.render_under()
        self.assertEqual(one, two)
        self.assertIn("**Map status:** Reviewed", one[0][1])
        self.assertIn("No book purchase is required", one[0][1])

    def test_repository_owned_guide_atomically_replaced(self):
        target = self.guide_root / "SEF" / "SEF1.md"
        with patch.object(guides, "GUIDES", self.guide_root):
            guides.atomic_write_guide(target, "first\n")
            guides.atomic_write_guide(target, "second\n")
        self.assertEqual(target.read_text(), "second\n")
        self.assertEqual(list(target.parent.glob("*.tmp")), [])

    def test_atomic_write_failure_preserves_original(self):
        target = self.guide_root / "SEF" / "SEF1.md"
        with patch.object(guides, "GUIDES", self.guide_root):
            guides.atomic_write_guide(target, "learner-preserved\n")
            with patch.object(guides.os, "replace", side_effect=OSError("injected")):
                with self.assertRaises(OSError):
                    guides.atomic_write_guide(target, "new\n")
        self.assertEqual(target.read_text(), "learner-preserved\n")
        self.assertFalse(list(target.parent.glob("*.tmp")))

    def test_refuse_symlinked_guide_destination(self):
        outside = self.root / "external.md"
        outside.write_text("do not alter", encoding="utf-8")
        target = self.guide_root / "SEF" / "SEF1.md"
        target.parent.mkdir(parents=True)
        target.symlink_to(outside)
        with patch.object(guides, "GUIDES", self.guide_root):
            with self.assertRaisesRegex(ValueError, "symlink"):
                guides.atomic_write_guide(target, "danger\n")
        self.assertEqual(outside.read_text(), "do not alter")


if __name__ == "__main__":
    unittest.main()
