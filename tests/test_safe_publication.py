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


from oee_workspace import local as publisher
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
        with self.assertRaisesRegex(publisher.PublicationError, "already exists"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertEqual((target / "README.md").read_text(), "My work")
        self.assertFalse((self.root / self.course_paths[1]).exists())
        self.assertFalse((self.root / self.course_paths[2]).exists())

    def test_reject_symlinked_parent_even_when_it_targets_safe_directory(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / "labs").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(publisher.PublicationError, "real directory"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertEqual(list(outside.iterdir()), [])

    def test_reject_symlink_at_destination_and_preserve_target(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (outside / "evidence.txt").write_text("mine", encoding="utf-8")
        directory = self.root / "labs" / "SEF"
        directory.mkdir(parents=True)
        (directory / "SEF1").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(publisher.PublicationError, "already exists"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertEqual((outside / "evidence.txt").read_text(), "mine")

    def test_missing_stage_aborts_before_any_publish(self):
        (self.stage / self.course_paths[2] / "README.md").unlink()
        (self.stage / self.course_paths[2]).rmdir()
        with self.assertRaisesRegex(publisher.PublicationError, "staged output"):
            publisher.publish(self.root, self.stage, self.course_paths)
        self.assertFalse((self.root / self.course_paths[0]).exists())

    def test_failed_first_rename_preserves_stage(self):
        with patch.object(publisher.os, "rename", side_effect=OSError("injected")):
            with self.assertRaisesRegex(publisher.PublicationError, "new files rolled back"):
                publisher.publish(self.root, self.stage, self.course_paths)
        self.assertFalse((self.root / self.course_paths[0]).exists())
        self.assertTrue((self.stage / self.course_paths[0] / "README.md").exists())

    def test_partial_publish_rolls_back_only_newly_owned_files(self):
        real_rename = os.rename
        calls = []

        def fail_second(src, target):
            calls.append((src, target))
            if len(calls) == 2:
                raise OSError("injected second rename failure")
            real_rename(src, target)

        with patch.object(publisher.os, "rename", side_effect=fail_second):
            with self.assertRaisesRegex(publisher.PublicationError, "new files rolled back"):
                publisher.publish(self.root, self.stage, self.course_paths)
        self.assertFalse((self.root / self.course_paths[0]).exists())
        self.assertFalse((self.root / self.course_paths[1]).exists())
        self.assertTrue((self.stage / self.course_paths[1] / "README.md").exists())

    def test_reject_outside_stage_and_invalid_project(self):
        other = Path(self.temp.name) / ".oee-stage-elsewhere"
        other.mkdir()
        with self.assertRaisesRegex(publisher.PublicationError, "directly inside"):
            publisher.publish(self.root, other, self.course_paths)
        # Invalid project aliases are rejected by the current-only CLI.
        # The publisher itself accepts only validated relative destinations.
        with self.assertRaisesRegex(publisher.PublicationError,
                                    "invalid relative destination"):
            publisher.publish(self.root, self.stage, [Path("../ledgerlab")])

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
        self.guide_root = self.root / "guides"
        self.guide_root.mkdir()
        self.program = self.guide_root / "SEF"
        self.program.mkdir()
        self.output = self.program / "SEF1.md"

    def test_release_keyed_guide_render_is_deterministic(self):
        from test_toolkit_consumer import PIN, valid_map, COURSE_SHA
        mapping = valid_map()
        mapping["status"] = "reviewed"
        catalog = {"R1": ({"title": "Resource", "access": {"mode": "free", "url": "https://example.com"}},
                          "resources/catalog/online/R1.json")}
        source = {"originCommit": "c" * 40, "releaseId": PIN["releaseId"],
                  "manifestSha256": PIN["manifestSha256"],
                  "courseSha256": COURSE_SHA}
        a = guides.render(mapping, catalog, source)
        b = guides.render(mapping, catalog, source)
        self.assertEqual(a, b)
        self.assertIn(PIN["releaseId"], a)
        self.assertIn(PIN["manifestSha256"], a)
        self.assertIn("blob/" + "c" * 40, a)

    def test_atomic_guide_writer_refuses_symlink_output(self):
        with patch.object(guides, "GUIDES", self.guide_root):
            self.output.symlink_to(self.root / "target.md")
            with self.assertRaises(ValueError):
                guides.atomic_write_guide(self.output, "new guide")
            self.assertFalse((self.root / "target.md").exists())

    def test_no_active_map_does_not_create_unapproved_guide(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(guides, "MAPPINGS", Path(tmp) / "mappings"):
                self.assertEqual(list(guides.outputs(None, None, None)), [])


if __name__ == "__main__":
    unittest.main()
