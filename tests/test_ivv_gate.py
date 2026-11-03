import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from ivv_gate import Comment, parse_assessors, to_comment, verdict_state

SHA = "b6b16f8137e51e19764dadf12cfeef536dfd79e3"
ASSESSORS = parse_assessors(None)  # default: github-actions[bot]
BOT = "github-actions[bot]"


def verdict(sha7: str, ruling: str, author: str = BOT, **kw: object) -> Comment:
    body = f"### 独立评估 · SOTA v1.0 · {sha7}\n判定：{ruling}\n\n| 条款 | 结论 |\n"
    return Comment(body=body, author=author, **kw)  # type: ignore[arg-type]


def state(comments: list[Comment], ref: str = "claude/x", assessors: frozenset[str] = ASSESSORS) -> str:
    return verdict_state(ref, SHA, comments, assessors)[0]


class Gate(unittest.TestCase):
    def test_other_branches_pass(self):
        self.assertEqual(state([], ref="docs/x"), "success")

    def test_no_verdict_is_pending(self):
        self.assertEqual(state([Comment("LGTM", BOT)]), "pending")

    def test_pass_for_head(self):
        self.assertEqual(state([verdict("b6b16f8", "PASS")]), "success")

    def test_na_counts_as_pass(self):
        self.assertEqual(state([verdict("b6b16f8", "N/A（本 PR 不涉及任何条款）")]), "success")

    def test_fail_for_head(self):
        self.assertEqual(state([verdict("b6b16f8", "FAIL（MUST 未过 2 条）")]), "failure")

    def test_verdict_for_old_head_does_not_count(self):
        self.assertEqual(state([verdict("865fce8", "PASS")]), "pending")

    def test_latest_verdict_wins(self):
        self.assertEqual(state([verdict("b6b16f8", "FAIL（1）"), verdict("b6b16f8", "PASS")]), "success")

    def test_ascii_colon_accepted(self):
        c = verdict("b6b16f8", "PASS")
        self.assertEqual(state([Comment(c.body.replace("：", ":"), BOT)]), "success")

    def test_heading_mid_text_is_ignored(self):
        self.assertEqual(state([Comment("see ### 独立评估 · SOTA v1.0 · b6b16f8 判定：PASS", BOT)]), "pending")


class Independence(unittest.TestCase):
    """IVV.md rule 1: the author never grades itself (#28 review)."""

    def test_author_pass_stays_pending(self):
        # Every authoring session here comments as the repository owner.
        self.assertEqual(state([verdict("b6b16f8", "PASS", author="HUIIIM")]), "pending")

    def test_author_pass_cannot_override_assessor_fail(self):
        comments = [verdict("b6b16f8", "FAIL（1）"), verdict("b6b16f8", "PASS", author="HUIIIM")]
        self.assertEqual(state(comments), "failure")

    def test_assessor_app_slug_counts(self):
        self.assertEqual(state([verdict("b6b16f8", "PASS", author="someone", app="ivv-assessor")],
                               assessors=parse_assessors("ivv-assessor")), "success")

    def test_edited_verdict_does_not_count(self):
        self.assertEqual(state([verdict("b6b16f8", "PASS", edited=True)]), "pending")

    def test_parse_assessors(self):
        self.assertEqual(parse_assessors(" a , b ,,"), frozenset({"a", "b"}))
        self.assertEqual(parse_assessors(""), frozenset({BOT}))

    def test_to_comment_reads_identity_and_edit(self):
        raw = {"body": "x", "user": {"login": "HUIIIM"}, "performed_via_github_app": None,
               "created_at": "2026-11-03T00:00:00Z", "updated_at": "2026-11-03T00:05:00Z"}
        c = to_comment(raw)
        self.assertEqual((c.author, c.app, c.edited), ("HUIIIM", "", True))


if __name__ == "__main__":
    unittest.main()
