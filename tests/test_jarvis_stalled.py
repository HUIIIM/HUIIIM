import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import jarvis_stalled
from jarvis_stalled import stalled_reason

NOW = dt.datetime(2026, 11, 3, 12, tzinfo=dt.UTC)


def issue(*labels, title="task", created_h=0, updated_h=0, pr=False):
    d = {
        "title": title,
        "labels": [{"name": n} for n in labels],
        "created_at": (NOW - dt.timedelta(hours=created_h)).isoformat(),
        "updated_at": (NOW - dt.timedelta(hours=updated_h)).isoformat(),
    }
    if pr:
        d["pull_request"] = {}
    return d


class Stalled(unittest.TestCase):
    def test_fresh_queued_is_fine(self):
        self.assertIsNone(stalled_reason(issue("jarvis-task", created_h=1), NOW))

    def test_old_unpicked_is_stalled(self):
        self.assertIn("queued", stalled_reason(issue("jarvis-task", "jarvis-task:queued", created_h=7), NOW))

    def test_working_recent_is_fine(self):
        self.assertIsNone(stalled_reason(issue("jarvis-task", "jarvis-task:working", created_h=30, updated_h=1), NOW))

    def test_working_stale_is_stalled(self):
        self.assertIn("working", stalled_reason(issue("jarvis-task", "jarvis-task:working", updated_h=3), NOW))

    def test_review_and_blocked_are_not_stalled(self):
        for state in ("jarvis-task:review", "jarvis-task:blocked", "jarvis-task:done"):
            self.assertIsNone(stalled_reason(issue("jarvis-task", state, created_h=100), NOW))

    def test_decision_requests_and_prs_skipped(self):
        self.assertIsNone(stalled_reason(issue("jarvis-task", title="[jarvis-task] 待中枢裁 · x", created_h=100), NOW))
        self.assertIsNone(stalled_reason(issue("jarvis-task", created_h=100, pr=True), NOW))


class ApiFailure(unittest.TestCase):
    def test_api_error_exits_2_not_1(self):
        import os
        import urllib.error
        from unittest import mock

        env = {"GITHUB_TOKEN": "t", "GITHUB_REPOSITORY": "o/r"}
        boom = mock.Mock(side_effect=urllib.error.URLError("503"))
        with mock.patch.dict(os.environ, env), mock.patch.object(jarvis_stalled, "_api", boom):
            self.assertEqual(jarvis_stalled.main(), 2)


if __name__ == "__main__":
    unittest.main()
