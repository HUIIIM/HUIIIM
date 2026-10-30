import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_readme as c  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class Markers(unittest.TestCase):
    def test_markdown_on_comment_line_is_flagged(self):
        # The shape the daily sync wrote until 2026-10-30: renders as literal ** and ](...).
        bad = "<!-- grading:start -->**Graded daily.** [card](https://x.test)<!-- grading:end -->\n"
        self.assertEqual(len(c.static_findings(bad)), 1)

    def test_markers_on_their_own_lines_pass(self):
        good = "<!-- grading:start -->\n\n**Graded daily.** [card](https://x.test)\n\n<!-- grading:end -->\n"
        self.assertEqual(c.static_findings(good), [])

    def test_comment_only_line_passes(self):
        self.assertEqual(c.static_findings("<!-- a --> <!-- b -->\n"), [])


class Images(unittest.TestCase):
    def test_missing_alt_and_file(self):
        f = c.static_findings('<img src="assets/nope.png">\n')
        self.assertTrue(any("alt" in x for x in f))
        self.assertTrue(any("not found" in x for x in f))


class Rendering(unittest.TestCase):
    def test_visible_text_detects_literal_markdown(self):
        rendered = "<p>**Graded daily.** [the card](https://x.test)</p><p><code>**ok**</code></p>"
        shown = c.visible_text(rendered)
        self.assertIn("**", shown)
        self.assertIn("](", shown)
        self.assertNotIn("**ok**", shown)


class RepositoryReadme(unittest.TestCase):
    def test_current_readme_is_clean(self):
        self.assertEqual(c.static_findings((ROOT / "README.md").read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
