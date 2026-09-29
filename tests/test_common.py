import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
import prbar_common as c  # noqa: E402


def node(**kw):
    base = {
        "number": 7, "title": "Add thing", "url": "https://github.com/o/r/pull/7",
        "isDraft": False, "body": "", "headRefName": "feat", "updatedAt": "2026-01-01T00:00:00Z",
        "additions": 10, "deletions": 2, "changedFiles": 3, "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN", "reviewDecision": None, "author": {"login": "me"},
        "repository": {"nameWithOwner": "o/r"},
        "commits": {"nodes": [{"commit": {"committedDate": "2026-01-02T00:00:00Z",
                                          "statusCheckRollup": {"state": "SUCCESS"}}}]},
        "comments": {"nodes": []},
    }
    base.update(kw)
    return base


class Links(unittest.TestCase):
    def test_extracts_issues_and_previews(self):
        text = ("Fixes https://linear.app/acme/issue/ENG-225/pr-bar and "
                "https://github.com/o/r/issues/12.\n"
                "Preview: [x](https://pr-bar-git-feat-acme.vercel.app/path).")
        issues, previews = c.extract_links(text)
        self.assertEqual([i["label"] for i in issues], ["ENG-225", "o/r#12"])
        self.assertEqual(issues[0]["url"], "https://linear.app/acme/issue/ENG-225")
        self.assertEqual(previews[0]["url"], "https://pr-bar-git-feat-acme.vercel.app/path")


class Classify(unittest.TestCase):
    def test_buckets(self):
        self.assertEqual(c.normalise(node())["bucket"], "ready")
        self.assertEqual(c.normalise(node(isDraft=True))["bucket"], "draft")
        self.assertEqual(c.normalise(node(reviewDecision="CHANGES_REQUESTED"))["bucket"], "fixes")
        self.assertEqual(c.normalise(node(mergeable="CONFLICTING"))["bucket"], "fixes")
        failing = node()
        failing["commits"]["nodes"][0]["commit"]["statusCheckRollup"]["state"] = "FAILURE"
        self.assertEqual(c.normalise(failing)["bucket"], "fixes")

    def test_review_requested_group(self):
        prs = [c.normalise(node()), c.normalise(node(number=8), True)]
        g = c.group(prs)
        self.assertEqual(len(g["review"]), 1)
        self.assertEqual(len(g["ready"]), 1)


class Format(unittest.TestCase):
    def setUp(self):
        self.prs = [c.normalise(node()), c.normalise(node(number=8, title="Other"), True)]

    def test_formats(self):
        self.assertIn("[#7 Add thing](https://github.com/o/r/pull/7)", c.format_summary(self.prs, "md"))
        self.assertIn("<https://github.com/o/r/pull/7|#7 Add thing>", c.format_summary(self.prs, "slack"))
        self.assertIn("- #7 Add thing", c.format_summary(self.prs, "text"))

    def test_review_scope(self):
        out = c.format_summary(self.prs, "text", "review")
        self.assertIn("#8", out)
        self.assertNotIn("#7", out)

    def test_age(self):
        self.assertEqual(c.fmt_age(90000), "1d")
        self.assertEqual(c.fmt_age(30), "<1m")


if __name__ == "__main__":
    unittest.main()
