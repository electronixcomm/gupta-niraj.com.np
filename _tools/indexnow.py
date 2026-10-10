"""Tell search engines (Bing, Yandex, Seznam, Naver via IndexNow) that pages changed.

Run from the repo root AFTER the change is pushed and live:
    python _tools/indexnow.py            # every URL in sitemap.xml
    python _tools/indexnow.py URL [URL]  # only the given URLs

The key file <key>.txt in the site root proves ownership; don't delete it.
"""
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOST = 'gupta-niraj.com.np'
KEY_FILE = next(p for p in ROOT.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', p.name))
KEY = KEY_FILE.stem


def main():
    urls = sys.argv[1:] or re.findall(r'<loc>([^<]+)</loc>', (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY_FILE.name}', 'urlList': urls}).encode()
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f'IndexNow: HTTP {r.status} for {len(urls)} URLs')


if __name__ == '__main__':
    main()
