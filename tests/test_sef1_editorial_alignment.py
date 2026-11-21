"""Editorial SEF1 traceability tests; not a curriculum parser or release approval.

These checks intentionally inspect only local editorial Markdown and catalogue
metadata. The academic assertions against the *current* OEE source were
independently compared during authoring and must be repeated at release lock.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "resources" / "editorial" / "SEF1-LESSON-MAP.md"
COUNTS = (6, 5, 4, 6, 4, 6, 6, 4)
LESSON = re.compile(
    r"^\| ([1-8])\.([1-9][0-9]*) ([^|]+) \| ([^|]+) \| "
    r"(topical|partial|source-only) \| ([^|]+) \|$"
)
ID = re.compile(r"\b(?:B|R)[1-9][0-9]*\b")


class SEF1EditorialResourceAlignmentTests(unittest.TestCase):
    def test_41_oeesef1_lessons_have_individual_review_rows(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")
        rows = [LESSON.fullmatch(line) for line in text.splitlines()]
        rows = [match for match in rows if match is not None]
        self.assertEqual(len(rows), sum(COUNTS))
        keys = [(int(row[1]), int(row[2])) for row in rows]
        self.assertEqual(keys, [
            (module, lesson)
            for module, count in enumerate(COUNTS, start=1)
            for lesson in range(1, count + 1)
        ])
        self.assertEqual(len(keys), len(set(keys)))
        for row in rows:
            self.assertTrue(row[3].strip(), "empty OEE source lesson title")
            self.assertTrue(row[4].strip(), "empty optional resource/gap source")
            self.assertTrue(row[6].strip(), "undeclared OEE-specific gap")
        self.assertIn("**not** a published or approved resource map", text)
        self.assertIn("216553f10d20ed5fcb40dda46a147c68d7895555", text)

    def test_all_41_lesson_resource_ids_have_catalogue_records(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")
        rows = [LESSON.fullmatch(line) for line in text.splitlines()]
        used = {item for row in rows if row is not None
                for item in ID.findall(row[4])}
        self.assertTrue(used)
        catalog = ROOT / "resources" / "catalog"
        available = {
            path.stem
            for path in catalog.rglob("*.json")
            if path.parent.name in ("books", "online")
        }
        self.assertFalse(used - available,
                         f"uncatalogued SEF1 lesson source: {used - available}")
        self.assertEqual(len(used), len(set(used)))

    def test_new_free_entries_are_verified_and_not_paid(self) -> None:
        paths = [
            ROOT / "resources" / "catalog" / "books" / "B4.json",
            *(ROOT / "resources" / "catalog" / "online" / f"R{x}.json"
              for x in range(92, 97)),
        ]
        for path in paths:
            with self.subTest(path=path.name):
                item = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(item["id"], path.stem)
                self.assertEqual(item["access"]["mode"], "free")
                self.assertTrue(item["access"]["url"].startswith("https://"))
                self.assertEqual(item["verification"]["status"], "verified")
                self.assertEqual(item["verification"]["checkedOn"], "2026-11-21")
                self.assertTrue(item["verification"]["basis"])

    def test_b1_and_b46_remain_prose_review_needed(self) -> None:
        for id_ in ("B1", "B46"):
            data = json.loads((
                ROOT / "resources" / "catalog" / "books" / f"{id_}.json"
            ).read_text(encoding="utf-8"))
            self.assertEqual(data["verification"]["status"], "review-needed")

    def test_no_unapproved_sef1_runtime_map_was_activated(self) -> None:
        self.assertFalse((
            ROOT / "resources" / "mappings" / "SEF" / "SEF1.json"
        ).exists())
        self.assertFalse((
            ROOT / "resources" / "guides" / "SEF" / "SEF1.md"
        ).exists())


if __name__ == "__main__":
    unittest.main()
