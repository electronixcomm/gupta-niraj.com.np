# gupta-niraj.com.np

Personal site and teaching hub of **Niraj Kumar Gupta**, Senior Engineer at NDCL and lecturer.
Static HTML/CSS/JS served by GitHub Pages at <https://gupta-niraj.com.np>.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Homepage: profile, experience, education, research |
| `teaching/index.html` | Teaching Hub: all subjects |
| `teaching/<subject>.html` | Subject page (unit list is generated for lesson-based subjects) |
| `teaching/digital-logic/`, `teaching/switching-routing/` | Lesson pages, one self-contained HTML file each |
| `teaching/switching-routing/downloads/` | Packet Tracer labs and cheat sheet |
| `assets/` | Shared stylesheet, script, favicon, social share image |
| `privacy.html`, `404.html` | Privacy & terms, not-found page |
| `sitemap.xml`, `robots.txt`, `llms.txt` | Generated for search and AI answer engines |
| `_tools/` | Build scripts (folders starting with `_` are not published) |

## Adding or changing a lesson

1. Put the lesson HTML in `teaching/<subject>/` with a URL-safe file name. Never edit lesson content in the scripts.
2. Add it to `CATALOG` in `_tools/build_units.py` (unit, label, title, kind, one-line summary).
3. Run, from the repo root:

   ```
   python _tools/build_units.py   # top/bottom bars, contents panel, titles, subject-page unit cards
   python _tools/seo.py           # meta tags, JSON-LD, sitemap.xml, robots.txt, llms.txt
   python _tools/check_site.py    # links, metadata, sitemap
   ```
4. Commit and push; GitHub Pages deploys in under a minute. Then notify Bing and other IndexNow engines:

   ```
   python _tools/indexnow.py      # submits every sitemap URL
   ```

Raw course material in `teaching/Uniglobe college/` is a local working folder and is ignored by git.

## Content

© Niraj Kumar Gupta. All rights reserved. Lessons are free to read; short quotations with a link are welcome.
See <https://gupta-niraj.com.np/privacy.html>.
