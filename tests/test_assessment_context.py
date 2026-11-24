"""Context digest, document and applicability rejection tests."""
import copy
from pathlib import Path
import runpy
import unittest

from test_toolkit_consumer import valid_export

ROOT = Path(__file__).resolve().parents[1]
validator = runpy.run_path(str(ROOT / "scripts/verify-assessment-context.py"))
check = validator["check_context"]
digest = validator["digest"]
canonical = validator["canonical"]


def seal(data):
    data.pop("contextSha256", None)
    data["contextSha256"] = digest(canonical(data))


def fixture():
    export = valid_export()
    path = export["source"]["coursePath"]
    markdown = "Original required assessment.\nOptional practice.\n"
    sha = digest(markdown.encode())
    export["source"]["courseSha256"] = sha
    context = {
        "contextVersion": 1, "source": export["source"].copy(),
        "toolkit": export["toolkit"].copy(),
        "courseExportSha256": digest(canonical(export)),
        "documents": [{"path": path, "sha256": sha, "startLine": 1,
                       "endLine": 2, "markdown": markdown}],
        "assessments": [{"assessmentId": "SEF1-AS1", "sourcePaths": [path]}],
        "reviewedRanges": [], "applicability": "manual-resolution-required",
        "manualReviewRequired": True,
    }
    seal(context)
    return context, export, {path: sha}


class AssessmentContextTests(unittest.TestCase):
    def test_unindexed_course_retains_original_text(self):
        context, export, hashes = fixture()
        self.assertEqual(check(context, export, hashes), context)

    def test_resealed_tampered_context_is_rejected(self):
        for mutate in (
            lambda c: c.update(contextVersion=True),
            lambda c: c.update(courseExportSha256="a" * 64),
            lambda c: c["source"].update(originCommit="d" * 40),
            lambda c: c["toolkit"].update(toolVersion="9.9.9"),
            lambda c: c["documents"][0].update(markdown="Altered\n"),
            lambda c: c["documents"][0].update(endLine=3),
            lambda c: c["assessments"][0].update(assessmentId="SEF1-AS99"),
            lambda c: c.update(applicability="source-indexed"),
            lambda c: c.update(reviewedRanges=[{}]),
        ):
            context, export, hashes = fixture()
            mutate(context)
            seal(context)
            with self.subTest(context=context), self.assertRaises(ValueError):
                check(context, export, hashes)

    def test_context_digest_is_required(self):
        context, export, hashes = fixture()
        changed = copy.deepcopy(context)
        changed["contextSha256"] = "0" * 64
        with self.assertRaises(ValueError):
            check(changed, export, hashes)
