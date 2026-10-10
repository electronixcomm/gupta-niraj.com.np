"""Search-engine (SEO) and answer-engine (AEO) metadata for the site.

Run from the repo root AFTER build_units.py:   python _tools/seo.py

It (idempotently):
  * adds a <!--nkg:seo--> block inside <head> of every page: description,
    canonical, robots, Open Graph / Twitter tags and schema.org JSON-LD
    (Person/WebSite on the homepage, Course on subject pages,
    LearningResource on lessons, BreadcrumbList everywhere),
  * regenerates sitemap.xml with <lastmod> dates,
  * writes robots.txt and llms.txt.
Page content is never touched.
"""
import datetime
import html
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / '_tools'))
from build_units import CATALOG, pages_in_order  # noqa: E402

SITE = 'https://gupta-niraj.com.np'
IMAGE = SITE + '/assets/og-image.jpg'
AUTHOR = 'Niraj Kumar Gupta'
PERSON_ID = SITE + '/#person'
TODAY = datetime.date.today().isoformat()

PERSON = {
    '@type': 'Person', '@id': PERSON_ID, 'name': AUTHOR, 'url': SITE + '/',
    'jobTitle': 'Senior Engineer',
    'worksFor': {'@type': 'Organization', 'name': 'NDCL'},
    'alumniOf': [{'@type': 'CollegeOrUniversity', 'name': 'Institute of Engineering, Tribhuvan University'}],
    'knowsAbout': ['Switching and Routing', 'Computer Networks', 'Digital Logic', 'Cloud Computing',
                   'Microsoft Azure', 'Machine Learning', 'Generative Adversarial Networks',
                   'C Programming', 'Python', 'Data Mining'],
    'sameAs': ['https://www.researchgate.net/publication/370580661'],
    'image': IMAGE,
    'email': 'mailto:contact@gupta-niraj.com.np',
    'subjectOf': {'@type': 'DigitalDocument', 'name': 'Curriculum Vitae', 'encodingFormat': 'application/pdf',
                  'url': SITE + '/assets/Niraj_Kumar_Gupta_CV.pdf'},
}
RIGHTS = {'copyrightHolder': {'@type': 'Person', '@id': PERSON_ID, 'name': AUTHOR}, 'copyrightYear': 2026,
          'usageInfo': SITE + '/privacy.html'}
PERSON_REF = {'@type': 'Person', '@id': PERSON_ID, 'name': AUTHOR, 'url': SITE + '/'}

# Subject pages: path -> course facts. Lesson-based subjects come from CATALOG.
SUBJECTS = {
    'digital-logic': dict(code='BT102CO', provider='Gateway Professional College (Purvanchal University)', level='Undergraduate, Year I'),
    'switching-routing': dict(code='NCS 485', provider='UniGlobe College (Pokhara University)', level='Undergraduate'),
    'c-programming': dict(name='C Programming', code='CSC115', provider='SOCH College of IT (Tribhuvan University)', level='Undergraduate, Year I'),
    'cloud-computing': dict(name='Cloud Computing', code='Unit 28', provider='ISMT College (University of Sunderland)', level='Undergraduate'),
    'electrical-engineering': dict(name='Basic Electrical Engineering', code=None, provider=None, level='Undergraduate'),
    'ai-ml': dict(name='AI / ML / Deep Learning', code=None, provider=None, level='Graduate'),
    'python-data-science': dict(name='Python & Data Science', code=None, provider=None, level='Undergraduate'),
    'weka': dict(name='WEKA — Data Mining', code=None, provider=None, level='Undergraduate'),
}
HUB_DESC = ('Free teaching material by Niraj Kumar Gupta: interactive lessons, labs and practice for '
            'Switching & Routing, Digital Logic, Cloud Computing, C Programming, Electrical Engineering, '
            'AI/ML, Python & Data Science and WEKA.')

AI_AGENTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User',
             'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended', 'CCBot',
             'Bingbot', 'Googlebot', 'DuckDuckBot', 'YandexBot']



def write_text(path, s):
    """Write with a short retry: Windows sometimes holds a brief lock on files just written."""
    import time
    for attempt in range(6):
        try:
            path.write_text(s, encoding='utf-8', newline='')
            return
        except OSError:
            if attempt == 5:
                raise
            time.sleep(0.5)

def esc(s):
    return html.escape(s, quote=True)


def unesc(s):
    return html.unescape(s)


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'


def crumbs(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}


def git_date(rel):
    """Last change date: today if the file has uncommitted changes, else its last commit date."""
    dirty = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        return TODAY
    out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or TODAY


def head_meta(title, desc, url, og_type='website', with_desc=True, with_canon=True):
    tags = []
    if with_desc:
        tags.append(f'<meta name="description" content="{esc(desc)}">')
    if with_canon:
        tags.append(f'<link rel="canonical" href="{url}">')
    tags += [
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">',
        f'<meta name="author" content="{AUTHOR}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{AUTHOR} · Teaching Hub">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{IMAGE}">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{AUTHOR} — Teaching Hub">',
        '<meta property="og:locale" content="en_US">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{IMAGE}">',
    ]
    return tags


def inject(path, block):
    s = path.read_text(encoding='utf-8')
    # drop the previous block together with the blank lines around it, so reruns don't add whitespace
    s = re.sub(r'\s*<!--nkg:seo-->.*?<!--/nkg:seo-->\s*', '\n', s, flags=re.S)
    block = '<!--nkg:seo-->' + block + '<!--/nkg:seo-->'
    k = s.find('</head>')
    if k == -1:  # page whose head is only implied: put metadata right after the first <head>-less marker
        m = re.search(r'<body[^>]*>', s)
        k = m.start()
    s = s[:k] + block + '\n' + s[k:]
    write_text(path, s)
    return s


def page_title(s):
    m = re.search(r'<title>(.*?)</title>', s, re.S)
    return unesc(m.group(1).strip()) if m else ''


def page_desc(s):
    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    return unesc(m.group(1)) if m else ''


def drop_old_social(s):
    """Remove hand-written OG/Twitter tags so the generated block is the only source."""
    s = re.sub(r'\s*<!-- Open Graph -->', '', s)
    s = re.sub(r'\s*<!-- Twitter -->', '', s)
    s = re.sub(r'\s*<meta (property="og:[^"]+"|name="twitter:[^"]+"|name="author") content="[^"]*"\s*/?>', '', s)
    s = re.sub(r'\s*<!-- Structured data -->\s*<script type="application/ld\+json">.*?</script>', '', s, flags=re.S)
    return s


def build_lessons(sitemap):
    for key, sub in CATALOG.items():
        facts = SUBJECTS[key]
        course_url = f'{SITE}/teaching/{key}.html'
        for p in pages_in_order(key):
            rel = f'teaching/{key}/{p["file"]}'
            path = ROOT / rel
            url = f'{SITE}/{rel}'
            topic, label = p['topic'], p['label']
            kind = {'lab': 'Lab guide', 'slides': 'Presentation', 'notes': 'Lesson'}[p['kind']]
            desc = (f'{label} · {topic}: {p["meta"]}. Free interactive {kind.lower()} for {sub["name"]} '
                    f'({sub["code"]}, {facts["provider"].split("(")[-1].rstrip(")")}) by {AUTHOR}.')
            title = f'{label} · {topic} — {sub["name"]}'
            date = git_date(rel)
            graph = [
                {'@type': 'LearningResource', '@id': url + '#lesson', 'name': f'{label} · {topic}', 'headline': title,
                 'description': desc, 'url': url, 'inLanguage': 'en', 'learningResourceType': kind,
                 'educationalLevel': facts['level'], 'isAccessibleForFree': True, 'teaches': topic,
                 'keywords': f'{topic}, {sub["name"]}, {sub["code"]}', 'dateModified': date, 'image': IMAGE,
                 'author': PERSON_REF, 'publisher': PERSON_REF, **RIGHTS,
                 'isPartOf': {'@type': 'Course', '@id': course_url + '#course', 'name': sub['name'], 'courseCode': sub['code'], 'url': course_url}},
                crumbs([('Home', SITE + '/'), ('Teaching Hub', SITE + '/teaching/'), (sub['name'], course_url), (f'{label} · {topic}', url)]),
            ]
            block = ''.join(head_meta(title, desc, url, og_type='article')) + \
                f'<meta property="article:author" content="{SITE}/"><meta property="article:modified_time" content="{date}">' + \
                ld({'@context': 'https://schema.org', '@graph': graph})
            inject(path, block)
            sitemap.append((url, date, 'monthly', '0.7'))


def build_subjects(sitemap):
    for key, facts in SUBJECTS.items():
        rel = f'teaching/{key}.html'
        path = ROOT / rel
        url = f'{SITE}/{rel}'
        s = drop_old_social(path.read_text(encoding='utf-8'))
        write_text(path, s)
        title, desc = page_title(s), page_desc(s)
        name = CATALOG[key]['name'] if key in CATALOG else facts['name']
        course = {'@type': 'Course', '@id': url + '#course', 'name': name, 'description': desc, 'url': url,
                  'inLanguage': 'en', 'isAccessibleForFree': True, 'educationalLevel': facts['level'],
                  'image': IMAGE, 'author': PERSON_REF, 'instructor': PERSON_REF, **RIGHTS,
                  'provider': ({'@type': 'CollegeOrUniversity', 'name': facts['provider']} if facts['provider']
                               else {'@type': 'Person', '@id': PERSON_ID, 'name': AUTHOR}),
                  'offers': {'@type': 'Offer', 'category': 'Free', 'price': 0, 'priceCurrency': 'USD'},
                  'hasCourseInstance': {'@type': 'CourseInstance', 'courseMode': 'Online', 'courseWorkload': 'Self-paced',
                                        'instructor': PERSON_REF}}
        if facts['code']:
            course['courseCode'] = facts['code']
        if key in CATALOG:
            course['hasPart'] = [{'@type': 'LearningResource', 'name': f'{p["label"]} · {p["topic"]}',
                                  'url': f'{SITE}/teaching/{key}/{p["file"]}'} for p in pages_in_order(key)]
        graph = [course, crumbs([('Home', SITE + '/'), ('Teaching Hub', SITE + '/teaching/'), (name, url)])]
        inject(path, ''.join(head_meta(title, desc, url, with_desc=False, with_canon=False)) +
               ld({'@context': 'https://schema.org', '@graph': graph}))
        sitemap.append((url, git_date(rel), 'weekly', '0.8'))


def build_hub(sitemap):
    rel = 'teaching/index.html'
    path = ROOT / rel
    url = SITE + '/teaching/'
    s = drop_old_social(path.read_text(encoding='utf-8'))
    s = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{esc(HUB_DESC)}"', s, count=1)
    write_text(path, s)
    items = [{'@type': 'ListItem', 'position': i + 1, 'url': f'{SITE}/teaching/{k}.html',
              'name': (CATALOG[k]['name'] if k in CATALOG else f['name'])} for i, (k, f) in enumerate(SUBJECTS.items())]
    graph = [{'@type': 'CollectionPage', '@id': url + '#page', 'name': 'Teaching Hub', 'url': url, 'description': HUB_DESC,
              'inLanguage': 'en', 'author': PERSON_REF, 'mainEntity': {'@type': 'ItemList', 'itemListElement': items}},
             crumbs([('Home', SITE + '/'), ('Teaching Hub', url)])]
    inject(path, ''.join(head_meta(page_title(s), HUB_DESC, url, with_desc=False, with_canon=False)) +
           ld({'@context': 'https://schema.org', '@graph': graph}))
    sitemap.append((url, git_date(rel), 'weekly', '0.9'))


def build_home(sitemap):
    path = ROOT / 'index.html'
    s = drop_old_social(path.read_text(encoding='utf-8'))
    write_text(path, s)
    title, desc = page_title(s), page_desc(s)
    graph = [PERSON,
             {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': f'{AUTHOR} · Teaching Hub',
              'inLanguage': 'en', 'publisher': {'@id': PERSON_ID}, 'author': {'@id': PERSON_ID}},
             {'@type': 'ProfilePage', '@id': SITE + '/#profile', 'url': SITE + '/', 'name': title,
              'mainEntity': {'@id': PERSON_ID}, 'isPartOf': {'@id': SITE + '/#website'}}]
    inject(path, ''.join(head_meta(title, desc, SITE + '/', og_type='profile', with_desc=False, with_canon=False)) +
           ld({'@context': 'https://schema.org', '@graph': graph}))
    sitemap.append((SITE + '/', git_date('index.html'), 'monthly', '1.0'))


def build_privacy(sitemap):
    rel = 'privacy.html'
    path = ROOT / rel
    url = f'{SITE}/{rel}'
    s = path.read_text(encoding='utf-8')
    s = re.sub(r'\s*<meta name="robots" content="[^"]*" />', '', s)
    write_text(path, s)
    title, desc = page_title(s), page_desc(s)
    graph = [{'@type': 'WebPage', '@id': url + '#page', 'name': title, 'url': url, 'description': desc, 'inLanguage': 'en',
              'author': PERSON_REF, 'isPartOf': {'@id': SITE + '/#website'}},
             crumbs([('Home', SITE + '/'), ('Privacy & terms', url)])]
    inject(path, ''.join(head_meta(title, desc, url, with_desc=False, with_canon=False)) +
           ld({'@context': 'https://schema.org', '@graph': graph}))
    sitemap.append((url, git_date(rel), 'yearly', '0.3'))


def write_sitemap(entries):
    rows = ''.join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{p}</priority>\n  </url>\n'
                   for u, d, c, p in entries)
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + '</urlset>\n',
                                      encoding='utf-8', newline='')


def write_robots():
    agents = ''.join(f'User-agent: {a}\n' for a in AI_AGENTS)
    (ROOT / 'robots.txt').write_text(
        '# gupta-niraj.com.np — all content is public teaching material.\n'
        '# Search engines and AI answer engines are welcome to crawl, index and cite it.\n\n'
        'User-agent: *\nAllow: /\n\n'
        '# Named explicitly so the policy is unambiguous for search and AI crawlers.\n'
        + agents + 'Allow: /\n\n'
        f'Sitemap: {SITE}/sitemap.xml\n'
        f'# Plain-text site guide for AI assistants: {SITE}/llms.txt\n',
        encoding='utf-8', newline='')


def write_llms():
    lines = [f'# {AUTHOR} · Teaching Hub', '',
             f'> Free, openly accessible university teaching material written by {AUTHOR}, Senior Engineer at NDCL '
             '(Nepal) and lecturer. Each lesson is a self-contained interactive HTML page with explanations, '
             'worked examples, diagrams and practice questions.', '',
             f'Content may be quoted and cited with a link to the lesson page. Terms: {SITE}/privacy.html', '',
             '## Site', '',
             f'- [Home]({SITE}/): profile, experience, education and research of {AUTHOR}',
             f'- [CV (PDF)]({SITE}/assets/Niraj_Kumar_Gupta_CV.pdf)',
             f'- [Teaching Hub]({SITE}/teaching/): all subjects', '']
    for key, sub in CATALOG.items():
        facts = SUBJECTS[key]
        lines += [f'## {sub["name"]} ({sub["code"]})', '',
                  f'Course page: {SITE}/teaching/{key}.html — taught at {facts["provider"]}.', '']
        for num, utitle, usum, lessons, files in sub['units']:
            for f, label, topic, kind, meta in lessons:
                lines.append(f'- [{label} · {topic}]({SITE}/teaching/{key}/{f}): {meta}')
        lines.append('')
    lines += ['## Other subjects', '']
    for key, facts in SUBJECTS.items():
        if key in CATALOG:
            continue
        s = (ROOT / 'teaching' / f'{key}.html').read_text(encoding='utf-8')
        lines.append(f'- [{facts["name"]}]({SITE}/teaching/{key}.html): {page_desc(s)}')
    lines.append('')
    write_text(ROOT / 'llms.txt', '\n'.join(lines))


if __name__ == '__main__':
    entries = []
    build_home(entries)
    build_hub(entries)
    build_subjects(entries)
    build_lessons(entries)
    build_privacy(entries)
    write_sitemap(entries)
    write_robots()
    write_llms()
    print(f'SEO metadata on {len(entries)} pages; sitemap, robots.txt and llms.txt written')
