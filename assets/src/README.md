# Profile images

`../*.png` are rendered from the HTML that `render.py` writes next to it, in light and dark pairs.
Edit the copy in `render.py` (`CARDS`, `hero`), never the PNGs or the generated HTML by hand.
Keep the card text and the matching line in the profile `README.md` (alt text and the status line) in sync.

```bash
python3 -m pip install -r assets/src/requirements.txt
python3 -m playwright install chromium   # or set CHROMIUM_PATH to an existing Chromium
VERTCITI_LOGO_LIGHT=/path/to/logo.svg VERTCITI_LOGO_DARK=/path/to/logo-reverse.svg \
  python3 assets/src/render.py
```

- **Logos:** `logo.svg` and `logo-reverse.svg` live in the vertciti website repository. Point the two variables at local copies, or drop the files next to `render.py`.
- **Fonts:** the cards use Nunito Sans and JetBrains Mono. Install both before rendering: Chromium silently substitutes a fallback font, which changes the layout.
- **Check:** after rendering, run `python3 scripts/check_readme.py` from the repository root.
