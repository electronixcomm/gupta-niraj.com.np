"""Sanity checks for the published site. Exit code 1 if anything is wrong.

Run from the repo root:   python _tools/check_site.py
Also runs on every push via .github/workflows/site-check.yml.

Checks every published HTML page for:
  * internal links and assets that point to files that don't exist,
  * a <title>, one description and one canonical link (except the 404 page),
  * JSON-LD blocks that are valid JSON,
and checks that sitemap.xml lists only existing pages and every indexable page.
"""
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://gupta-niraj.com.np'
NOT_IN_SITEMAP = {'404.html'}


def published_files():
    out = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    return sorted(f for f in out if not f.startswith(('_', '.')) and (ROOT / f).is_file())


def resolve(page, ref):
    """Map an href/src on `page` to a repo path, or None for external/anchor links."""
    if not ref or ref.startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:', 'blob:')):
        return None
    parts = urlsplit(ref)
    if parts.scheme or parts.netloc:
        if parts.netloc != 'gupta-niraj.com.np':
            return None
        path = parts.path
    else:
        path = parts.path
    if not path:
        return None
    path = unquote(path)
    if path.startswith('/'):
        target = path.lstrip('/')
    else:
        target = str((pathlib.PurePosixPath(page).parent / path))
    if target == '' or target.endswith('/'):
        target += 'index.html'
    return str(pathlib.PurePosixPath(target))


def main():
    files = published_files()
    present = set(files)
    errors = []
    pages = [f for f in files if f.endswith('.html')]

    for page in pages:
        s = (ROOT / page).read_text(encoding='utf-8')
        head = s[:s.find('</head>')] if '</head>' in s else s
        # links and assets (attribute values only; iframe srcdoc content is entity-encoded and skipped)
        for ref in re.findall(r'\s(?:href|src)="([^"]+)"', s):
            target = resolve(page, ref)
            if target and target not in present:
                target_norm = str(pathlib.PurePosixPath(target))
                if target_norm not in present:
                    errors.append(f'{page}: broken link -> {ref}')
        if '<title>' not in s:
            errors.append(f'{page}: missing <title>')
        if page not in NOT_IN_SITEMAP:
            for tag, label in (('name="description"', 'description'), ('rel="canonical"', 'canonical')):
                n = head.count(tag)
                if n != 1:
                    errors.append(f'{page}: {n} {label} tags in <head> (expected 1)')
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(block)
            except ValueError as e:
                errors.append(f'{page}: invalid JSON-LD ({e})')

    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    listed = set()
    for loc in re.findall(r'<loc>([^<]+)</loc>', sitemap):
        target = resolve('index.html', loc)
        listed.add(target)
        if target not in present:
            errors.append(f'sitemap.xml: lists a missing page {loc}')
    for page in pages:
        if page not in NOT_IN_SITEMAP and page not in listed and 'noindex' not in (ROOT / page).read_text(encoding='utf-8')[:6000]:
            errors.append(f'sitemap.xml: page not listed {page}')
    if 'Sitemap:' not in (ROOT / 'robots.txt').read_text(encoding='utf-8'):
        errors.append('robots.txt: no Sitemap line')

    if errors:
        print(f'{len(errors)} problem(s):')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    print(f'OK: {len(pages)} pages, {len(listed)} sitemap URLs, all internal links resolve')


if __name__ == '__main__':
    main()
