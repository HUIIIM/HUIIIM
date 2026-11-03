import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from ivv_gate import verdict_state

SHA = "b6b16f8137e51e19764dadf12cfeef536dfd79e3"


def verdict(sha7: str, ruling: str) -> str:
    return f"### 独立评估 · SOTA v1.0 · {sha7}\n判定：{ruling}\n\n| 条款 | 结论 |\n"


class Gate(unittest.TestCase):
    def test_other_branches_pass(self):
        self.assertEqual(verdict_state("docs/x", SHA, [])[0], "success")

    def test_no_verdict_is_pending(self):
        self.assertEqual(verdict_state("claude/x", SHA, ["LGTM"])[0], "pending")

    def test_pass_for_head(self):
        self.assertEqual(verdict_state("claude/x", SHA, [verdict("b6b16f8", "PASS")])[0], "success")

    def test_na_counts_as_pass(self):
        body = verdict("b6b16f8", "N/A（本 PR 不涉及任何条款）")
        self.assertEqual(verdict_state("claude/x", SHA, [body])[0], "success")

    def test_fail_for_head(self):
        self.assertEqual(verdict_state("claude/x", SHA, [verdict("b6b16f8", "FAIL（MUST 未过 2 条）")])[0], "failure")

    def test_verdict_for_old_head_does_not_count(self):
        self.assertEqual(verdict_state("claude/x", SHA, [verdict("865fce8", "PASS")])[0], "pending")

    def test_latest_verdict_wins(self):
        bodies = [verdict("b6b16f8", "FAIL（1）"), verdict("b6b16f8", "PASS")]
        self.assertEqual(verdict_state("claude/x", SHA, bodies)[0], "success")

    def test_ascii_colon_accepted(self):
        self.assertEqual(verdict_state("claude/x", SHA, [verdict("b6b16f8", "PASS").replace("：", ":")])[0], "success")

    def test_quoted_heading_mid_text_is_ignored_unless_own_line(self):
        self.assertEqual(verdict_state("claude/x", SHA, ["see ### 独立评估 · SOTA v1.0 · b6b16f8 判定：PASS"])[0],
                         "pending")


if __name__ == "__main__":
    unittest.main()
