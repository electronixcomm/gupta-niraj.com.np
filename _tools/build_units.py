"""Keep the teaching unit pages consistent.

Run from the repo root:  python _tools/build_units.py

For every unit page listed in CATALOG this script (idempotently):
  * inserts the shared top bar (subject, unit, prev / all units / next) and
    bottom bar (previous / next lesson) between <!--nkg:...--> markers,
  * sets a consistent <title>,
  * adds lang="en" and a mobile viewport tag where missing,
  * adds layout-only fixes (tables scroll inside their box on phones, plus
    per-page tweaks in PAGE_CSS).
The lesson content itself is never touched.

It also regenerates the unit list on each subject page between
<!-- units:start --> and <!-- units:end -->.

Folders starting with "_" are not published by GitHub Pages.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

CATALOG = {
    'digital-logic': {
        'name': 'Digital Logic',
        'code': 'BT102CO',
        'units': [
            (1, 'Number Systems', 'Binary, octal, decimal and hexadecimal; conversions, complements and binary codes.', [
                ('unit-1-number-systems.html', 'Unit 1', 'Number Systems', 'notes', 'Interactive notes with an MCQ practice test'),
            ], []),
            (2, 'Boolean Algebra & Logic Gates', 'Boolean theorems and functions, logic gates, canonical forms and logic families.', [
                ('unit-2-boolean-algebra-and-logic-gates.html', 'Unit 2', 'Boolean Algebra & Logic Gates', 'notes', 'Interactive notes, lab connection and quiz'),
            ], []),
            (3, 'Simplification of Boolean Functions', 'Minterms and maxterms, two- to four-variable K-maps, prime implicants, SOP and POS.', [
                ('unit-3-simplification-of-boolean-functions.html', 'Unit 3', 'Simplification of Boolean Functions', 'notes', 'Step-by-step ladder with K-map practice'),
            ], []),
            (4, 'Combinational Logic', 'Adders and subtractors, code conversion, multilevel NAND/NOR circuits, XOR and parity.', [
                ('unit-4-combinational-logic.html', 'Unit 4', 'Combinational Logic', 'notes', 'Interactive notes with a problem bank'),
            ], []),
            (5, 'Combinational Logic with MSI & LSI', 'Parallel and BCD adders, comparators, decoders, encoders, multiplexers, ROM and PLA.', [
                ('unit-5-combinational-logic-msi-lsi.html', 'Unit 5', 'Combinational Logic with MSI & LSI', 'notes', 'Interactive notes with a problem bank'),
            ], []),
            (6, 'Sequential Logic', 'Flip-flops (RS, D, JK, T, master-slave), state equations and state reduction.', [
                ('unit-6-sequential-logic.html', 'Unit 6', 'Sequential Logic', 'notes', 'Interactive notes with a problem bank'),
            ], []),
            (7, 'Registers & Counters', 'Shift registers, SISO/SIPO/PISO/PIPO, synchronous and asynchronous counters, ring and decade counters.', [
                ('unit-7-registers-and-counters.html', 'Unit 7', 'Registers & Counters', 'notes', 'Interactive notes with a problem bank'),
            ], []),
        ],
    },
    'switching-routing': {
        'name': 'Switching & Routing',
        'code': 'NCS 485',
        'units': [
            (1, 'Introduction to Switching & Routing', 'Where switches and routers sit in a network, IP addressing review, and first steps on the Cisco CLI.', [
                ('unit-1-1-routers-and-switches.html', 'Unit 1.1', 'Role of Routers & Switches', 'slides', 'Slide deck reviewing computer network basics'),
                ('unit-1-2-ip-addressing-review.html', 'Unit 1.2', 'IP Addressing Review', 'notes', 'Classful vs classless addressing and network design'),
                ('unit-1-2-switching-vs-routing.html', 'Unit 1.2', 'Switching vs Routing', 'notes', 'Frames, packets and forwarding, with an ARP/CAM walkthrough'),
                ('unit-1-3-cisco-ios-cli-basics.html', 'Unit 1.3', 'Cisco IOS & CLI Basics', 'notes', 'CLI modes, memory and the switch boot process'),
            ], [('lab-1-simple-lan.pkt', 'Lab 1 · Building a simple LAN')]),
            (2, 'Switch Fundamentals & Configuration', 'How a switch forwards frames, and how to configure, secure and verify it.', [
                ('unit-2-2-switching-methods.html', 'Unit 2.2', 'Switching Methods', 'notes', 'Store-and-forward, cut-through and fragment-free'),
                ('unit-2-3-mac-address-table.html', 'Unit 2.3', 'MAC Address Table & Frame Forwarding', 'notes', 'How a switch learns, floods and forwards'),
                ('unit-2-3-basic-switch-setup.html', 'Unit 2.3', 'Basic Switch Configuration', 'notes', 'Hostname, management IP, console, VTY and SSH'),
                ('unit-2-4-managing-switch-configuration.html', 'Unit 2.4', 'Managing & Verifying Switch Configuration', 'notes', 'Show commands, saving and backing up configurations'),
            ], [('switch-config-cheat-sheet.pdf', 'Switch configuration cheat sheet')]),
            (3, 'VLANs', 'Breaking one switch into many broadcast domains, trunks and inter-VLAN routing.', [
                ('unit-3-1-vlan-concepts.html', 'Unit 3.1', 'VLAN Concepts & Configuration', 'notes', 'Purpose, membership and configuration of VLANs'),
            ], [('lab-3-router-on-a-stick.pkt', 'Lab 3 · Router-on-a-stick'),
                ('lab-3b-intervlan-layer3-switch.pkt', 'Lab 3b · Inter-VLAN with Layer 3 switch')]),
            (4, 'Static Routing', 'How a router decides where a packet goes, and how to tell it by hand.', [
                ('unit-4-static-routing.html', 'Unit 4', 'Static Routing', 'notes', 'Static and default routes in multi-router topologies'),
            ], [('lab-4-static-default-routes.pkt', 'Lab 4 · Static and default routes')]),
            (5, 'Distance Vector Routing', 'Routers sharing what they know with their neighbours: RIP and its limits.', [
                ('unit-5-distance-vector-rip.html', 'Unit 5', 'Distance Vector Routing (RIP)', 'notes', 'RIP versions, updates, timers and loop prevention'),
            ], [('lab-5-ripv2.pkt', 'Lab 5 · RIP v2')]),
            (6, 'Link-State & Hybrid Routing', 'OSPF and EIGRP in theory and in the lab.', [
                ('unit-6-link-state-and-hybrid-routing.html', 'Unit 6', 'Link-State & Hybrid Routing Protocols', 'notes', 'OSPF concepts, areas and the SPF algorithm'),
                ('unit-6-3-eigrp.html', 'Unit 6.3', 'EIGRP & Comparing RIP, OSPF, EIGRP', 'notes', 'EIGRP fundamentals with a design comparison matrix'),
                ('unit-6-lab-ospf.html', 'Unit 6 Lab', 'OSPF Implementation', 'lab', 'Single-area OSPF in a multi-router topology'),
                ('unit-6-lab-eigrp.html', 'Unit 6 Lab', 'EIGRP Implementation', 'lab', 'Basic EIGRP setup and verification'),
            ], [('lab-6-ospf-single-area.pkt', 'Lab 6 · OSPF single area')]),
            (7, 'Advanced Switching', 'Redundant switched networks: STP, Rapid PVST+, port security and EtherChannel.', [
                ('unit-7-advanced-switching.html', 'Unit 7', 'Advanced Switching', 'notes', 'STP, Rapid PVST+, port security and EtherChannel'),
                ('unit-7-lab-series.html', 'Unit 7 Lab', 'Switching Lab Series', 'lab', 'VLANs, STP, port security, EtherChannel and trouble tickets'),
            ], [('lab-7-stp-port-security-etherchannel.pkt', 'Lab 7 · STP, port security, EtherChannel')]),
            (8, 'WAN, ACL & NAT', 'Connecting sites over WAN links, filtering traffic and sharing public addresses.', [
                ('unit-8-wan-acl-nat.html', 'Unit 8', 'WAN, ACL & NAT', 'notes', 'PPP/HDLC, access control lists and network address translation'),
                ('unit-8-lab-series.html', 'Unit 8 Lab', 'WAN, ACL & NAT Lab Series', 'lab', 'PPP/HDLC, ACL filtering and NAT for internet access'),
            ], [('lab-8-ppp-hdlc-acl-nat.pkz', 'Lab 8 · PPP/HDLC, ACL and NAT')]),
        ],
    },
}

# Layout-only tweaks for pages whose own layout needs them. Never content.
PAGE_CSS = {
    'unit-1-1-routers-and-switches.html': (
        'body{flex-direction:column!important;justify-content:flex-start!important;align-items:stretch!important}'
        '.deck-container{height:calc(100vh - 50px)!important;max-height:none!important;margin:0 auto}'
        '@media (max-width:700px){.slide{padding:24px 18px!important}}'
    ),
    'unit-1-2-switching-vs-routing.html': (
        'body{padding-top:50px!important}.rail{top:50px!important}'
        '@media (max-width:860px){body{padding-top:106px!important}}'
    ),
    'unit-3-simplification-of-boolean-functions.html': '@media (max-width:760px){html,body{overflow-x:clip}}',
    'unit-4-static-routing.html': '@media (max-width:760px){html,body{overflow-x:clip}}',
    'unit-5-distance-vector-rip.html': '@media (max-width:760px){html,body{overflow-x:clip}}',
}
# Unit 6 pages: the single-column phone grid must not grow past the screen.
for _f in ('unit-6-link-state-and-hybrid-routing.html', 'unit-6-3-eigrp.html',
           'unit-6-lab-ospf.html', 'unit-6-lab-eigrp.html'):
    PAGE_CSS[_f] = '@media (max-width:900px){.shell{grid-template-columns:minmax(0,1fr)!important}}'
# Pages that arrived without a document wrapper were designed for a zero body margin.
for _f in ('unit-7-lab-series.html', 'unit-8-lab-series.html', 'unit-8-wan-acl-nat.html'):
    PAGE_CSS[_f] = 'body{margin:0}'
FIXED_BAR = {'unit-1-2-switching-vs-routing.html'}

BAR_CSS = """
#nkg-unitbar,#nkg-unitfoot{all:initial;display:block;box-sizing:border-box;position:relative;z-index:2147483000;align-self:stretch;justify-self:stretch;
  background:#0b1d3a;color:#fbf9f3;font:500 14px/1.2 Inter,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased}
#nkg-unitbar{height:50px;border-bottom:2px solid #c9a14a}
#nkg-unitbar[data-mode=fixed]{position:fixed;top:0;left:0;right:0}
#nkg-unitfoot{border-top:2px solid #c9a14a;margin-top:48px}
#nkg-unitbar *,#nkg-unitfoot *{box-sizing:border-box}
#nkg-unitbar .nkg-in,#nkg-unitfoot .nkg-in{display:flex;align-items:center;gap:12px;height:100%;max-width:1280px;margin:0 auto;padding:0 16px}
#nkg-unitfoot .nkg-in{padding:18px 16px;gap:12px;flex-wrap:wrap}
#nkg-unitbar a,#nkg-unitfoot a{color:#fbf9f3!important;text-decoration:none!important;background:none;border:0;font:inherit;cursor:pointer}
#nkg-unitbar .nkg-mark{flex:none;display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;
  background:linear-gradient(135deg,#11295a,#1c3a78);color:#d9b769;font:700 11px/1 Georgia,serif;letter-spacing:.02em;box-shadow:0 0 0 1px rgba(201,161,74,.5)}
#nkg-unitbar .nkg-subj{flex:none;font-weight:600;white-space:nowrap}
#nkg-unitbar .nkg-subj:hover{color:#d9b769!important}
#nkg-unitbar .nkg-sep{flex:none;color:#c9a14a}
#nkg-unitbar .nkg-unit{flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#cdd5e3}
#nkg-unitbar .nkg-unit b{color:#d9b769;font-weight:600;margin-right:6px}
#nkg-unitbar .nkg-nav{flex:none;display:flex;gap:6px}
#nkg-unitbar .nkg-btn{display:inline-flex;align-items:center;gap:6px;height:32px;padding:0 12px;border-radius:6px;border:1px solid rgba(251,249,243,.22)!important;white-space:nowrap}
#nkg-unitbar .nkg-btn:hover{border-color:#c9a14a!important;color:#d9b769!important}
#nkg-unitbar .nkg-btn[aria-disabled=true]{opacity:.35;pointer-events:none}
#nkg-unitfoot .nkg-card{flex:1 1 260px;display:flex;flex-direction:column;gap:4px;padding:12px 16px;border-radius:8px;border:1px solid rgba(251,249,243,.18)!important}
#nkg-unitfoot .nkg-card:hover{border-color:#c9a14a!important}
#nkg-unitfoot .nkg-card.next{text-align:right}
#nkg-unitfoot .nkg-k{font:600 11px/1 Inter,-apple-system,"Segoe UI",sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#c9a14a}
#nkg-unitfoot .nkg-t{font-size:15px;font-weight:600}
#nkg-unitfoot .nkg-copy{flex-basis:100%;font-size:12px;color:#8c93ab;text-align:center;padding-top:6px}
@media (max-width:640px){
  #nkg-unitbar .nkg-subj,#nkg-unitbar .nkg-sep{display:none}
  #nkg-unitbar .nkg-btn span{display:none}
  #nkg-unitbar .nkg-btn{padding:0 10px}
}
@media (max-width:760px){table{display:block;max-width:100%;overflow-x:auto}}
"""

BAR_JS = """(function(){try{var b=document.getElementById('nkg-unitbar'),f=document.getElementById('nkg-unitfoot'),cs=getComputedStyle(document.body),n=function(p){return parseFloat(cs[p])||0};
var l=n('paddingLeft')+n('marginLeft'),r=n('paddingRight')+n('marginRight');
if(b&&b.getAttribute('data-mode')!=='fixed'){var t=n('paddingTop')+n('marginTop');b.style.marginTop=-t+'px';b.style.marginLeft=-l+'px';b.style.marginRight=-r+'px';b.style.marginBottom=n('paddingTop')+'px';}
if(f){f.style.marginLeft=(parseFloat(f.style.marginLeft)||0)-l+'px';f.style.marginRight=-r+'px';f.style.marginBottom=-(n('paddingBottom')+n('marginBottom'))+'px';}}catch(e){}})();"""

FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600&amp;display=swap">'


def esc(s):
    return html.escape(s, quote=True)


def pages_in_order(key):
    out = []
    for num, utitle, usum, lessons, files in CATALOG[key]['units']:
        for f, label, topic, kind, meta in lessons:
            out.append(dict(file=f, label=label, topic=topic, kind=kind, meta=meta, unit=num))
    return out


def strip_old(s):
    s = re.sub(r'<!--nkg:bar-->.*?<!--/nkg:bar-->\n?', '', s, flags=re.S)
    s = re.sub(r'\n?<!--nkg:foot-->.*?<!--/nkg:foot-->\n?', '', s, flags=re.S)
    # first-generation back link
    s = re.sub(r'<div style="font:14px/1\.4 Inter[^>]*><a href="/teaching/[^"]+" style="[^"]*">&larr;[^<]*</a></div>\n?', '', s)
    return s


def build_page(key, i, seq):
    sub = CATALOG[key]
    p = seq[i]
    path = ROOT / 'teaching' / key / p['file']
    s = path.read_text(encoding='utf-8')
    s = strip_old(s)
    hub = f'/teaching/{key}.html'
    prev = seq[i - 1] if i > 0 else None
    nxt = seq[i + 1] if i + 1 < len(seq) else None

    def href(q):
        return f'/teaching/{key}/{q["file"]}'

    css = BAR_CSS + PAGE_CSS.get(p['file'], '')
    mode = 'fixed' if p['file'] in FIXED_BAR else 'flow'
    prev_btn = (f'<a class="nkg-btn" href="{href(prev)}" title="Previous: {esc(prev["label"] + " · " + prev["topic"])}">&#8249;<span> Prev</span></a>'
                if prev else '<a class="nkg-btn" aria-disabled="true">&#8249;<span> Prev</span></a>')
    next_btn = (f'<a class="nkg-btn" href="{href(nxt)}" title="Next: {esc(nxt["label"] + " · " + nxt["topic"])}"><span>Next </span>&#8250;</a>'
                if nxt else '<a class="nkg-btn" aria-disabled="true"><span>Next </span>&#8250;</a>')
    bar = (f'<!--nkg:bar-->{FONT_LINK}<style>{css}</style>'
           f'<nkg-unitbar id="nkg-unitbar" data-mode="{mode}" role="navigation" aria-label="Course navigation"><span class="nkg-in">'
           f'<a class="nkg-mark" href="/teaching/" title="Teaching Hub">NKG</a>'
           f'<a class="nkg-subj" href="{hub}">{esc(sub["name"])}</a><span class="nkg-sep">/</span>'
           f'<span class="nkg-unit"><b>{esc(p["label"])}</b>{esc(p["topic"])}</span>'
           f'<span class="nkg-nav">{prev_btn}<a class="nkg-btn" href="{hub}" title="All units">&#9776;<span> All units</span></a>{next_btn}</span>'
           f'</span></nkg-unitbar><!--/nkg:bar-->')
    cards = []
    if prev:
        cards.append(f'<a class="nkg-card prev" href="{href(prev)}"><span class="nkg-k">&#8249; Previous</span><span class="nkg-t">{esc(prev["label"] + " · " + prev["topic"])}</span></a>')
    cards.append(f'<a class="nkg-card" href="{hub}"><span class="nkg-k">{esc(sub["code"])}</span><span class="nkg-t">All {esc(sub["name"])} units</span></a>')
    if nxt:
        cards.append(f'<a class="nkg-card next" href="{href(nxt)}"><span class="nkg-k">Next &#8250;</span><span class="nkg-t">{esc(nxt["label"] + " · " + nxt["topic"])}</span></a>')
    foot = (f'<!--nkg:foot--><nkg-unitfoot id="nkg-unitfoot" role="navigation" aria-label="Lesson navigation"><span class="nkg-in">'
            + ''.join(cards) +
            f'<span class="nkg-copy">Niraj Kumar Gupta · Teaching Hub · {esc(sub["name"])} ({esc(sub["code"])})</span>'
            f'</span></nkg-unitfoot><script>{BAR_JS}</script><!--/nkg:foot-->')

    m = re.search(r'<body[^>]*>', s)
    s = s[:m.end()] + bar + s[m.end():]
    k = s.rfind('</body>')
    s = (s[:k] + foot + '\n' + s[k:]) if k != -1 else (s.rstrip() + '\n' + foot + '\n')

    title = f'{p["label"]} · {p["topic"]} — {sub["name"]}'
    s = re.sub(r'<title>.*?</title>', lambda _: f'<title>{esc(title)}</title>', s, count=1, flags=re.S)
    s = re.sub(r'<html(?![^>]*\blang=)', '<html lang="en"', s, count=1)
    if not re.search(r'<meta[^>]+name=["\']?viewport', s[:s.find('<body')]):
        s = re.sub(r'<head[^>]*>', lambda mm: mm.group(0) + '\n<meta name="viewport" content="width=device-width, initial-scale=1.0">', s, count=1)
    path.write_text(s, encoding='utf-8', newline='')


KIND_LABEL = {'notes': 'Lesson', 'slides': 'Slides', 'lab': 'Lab'}


def build_subject(key):
    sub = CATALOG[key]
    path = ROOT / 'teaching' / f'{key}.html'
    s = path.read_text(encoding='utf-8')
    units = sub['units']
    n_lessons = sum(1 for u in units for l in u[3] if l[3] != 'lab')
    n_labs = sum(1 for u in units for l in u[3] if l[3] == 'lab')
    n_files = sum(len(u[4]) for u in units)
    stats = [f'<span><strong>{len(units)}</strong> units</span>', f'<span><strong>{n_lessons}</strong> lessons</span>']
    if n_labs:
        stats.append(f'<span><strong>{n_labs}</strong> lab guides</span>')
    if n_files:
        stats.append(f'<span><strong>{n_files}</strong> downloads</span>')
    jump = ''.join(f'<a href="#unit-{u[0]}">{u[0]}</a>' for u in units)
    blocks = []
    for num, utitle, usum, lessons, files in units:
        items = ''.join(
            f'''
              <li class="lesson"><a href="/teaching/{key}/{f}">
                <span class="lesson-kind {kind}">{KIND_LABEL[kind]}</span>
                <span class="lesson-text"><span class="lesson-title">{esc(label.replace('Unit ', '') + ' · ' + topic if '.' in label else topic)}</span><span class="lesson-meta">{esc(meta)}</span></span>
                <span class="lesson-go" aria-hidden="true">&rarr;</span>
              </a></li>''' for f, label, topic, kind, meta in lessons)
        dl = ''
        if files:
            dl = '\n            <div class="unit-files"><span class="unit-files-label">Downloads</span>' + ''.join(
                f'<a class="file-chip" href="/teaching/{key}/downloads/{f}" download><span class="file-ext">{f.rsplit(".", 1)[1]}</span>{esc(t)}</a>'
                for f, t in files) + '</div>'
        blocks.append(f'''
        <article class="unit" id="unit-{num}">
          <div class="unit-num"><span>Unit</span>{num}</div>
          <div class="unit-body">
            <h2>{esc(utitle)}</h2>
            <p class="unit-summary">{esc(usum)}</p>
            <ul class="lessons">{items}
            </ul>{dl}
          </div>
        </article>''')
    section = f'''<!-- units:start -->
    <section class="section unit-section">
      <div class="container">
        <div class="course-bar">
          <div class="course-stats">{''.join(stats)}</div>
          <nav class="unit-jump" aria-label="Jump to unit"><span>Jump to unit</span>{jump}</nav>
        </div>
        <div class="unit-list">{''.join(blocks)}
        </div>
      </div>
    </section>
    <!-- units:end -->'''
    if '<!-- units:start -->' in s:
        s = re.sub(r'<!-- units:start -->.*?<!-- units:end -->', lambda _: section, s, flags=re.S)
    else:
        a = s.index('    <section class="section">')
        b = s.index('  </main>')
        s = s[:a] + '    ' + section + '\n' + s[b:]
    path.write_text(s, encoding='utf-8', newline='')


if __name__ == '__main__':
    for key in CATALOG:
        seq = pages_in_order(key)
        for i in range(len(seq)):
            build_page(key, i, seq)
        build_subject(key)
        print(f'{key}: {len(seq)} pages + subject page')
