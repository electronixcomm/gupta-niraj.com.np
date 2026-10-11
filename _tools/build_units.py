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
                ('unit-1-1-routers-and-switches.html', 'Unit 1.1', 'Role of Routers & Switches', 'notes', 'Computer network basics review: OSI, TCP/IP, Layer 2 vs Layer 3'),
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
            # Non-numeric "unit": course-wide lab material, shown as "Labs 1–8".
            ('Labs', 'Lab Companion', 'Commands, a practice checklist and self-test questions for every lab, stage by stage.', [
                ('lab-command-cheat-sheet.html', 'Lab Companion', 'Command Cheat Sheet', 'lab', 'Every command for Labs 1–8, with verification and troubleshooting'),
                ('lab-practice-checklist.html', 'Lab Companion', 'Practice Checklist', 'lab', 'Tick off each stage from a clean start to backup and recovery'),
                ('lab-question-bank.html', 'Lab Companion', 'Command Question Bank', 'lab', 'Questions by lab to test yourself on commands and output'),
            ], []),
        ],
    },
}

# Layout-only tweaks for pages whose own layout needs them. Never content.
PAGE_CSS = {
    # Slide deck shown as one scrolling page: every slide visible in order, slide Prev/Next removed.
    'unit-1-1-routers-and-switches.html': (
        'body{display:block!important;overflow:visible!important;overflow-x:clip!important;min-height:0!important}'
        '.deck-container{display:block!important;width:auto!important;height:auto!important;max-width:1180px!important;'
        'max-height:none!important;margin:0 auto!important;padding:28px 20px 4px!important;background:transparent!important;box-shadow:none!important}'
        '.slide{display:flex!important;opacity:1!important;height:auto!important;position:relative!important;'
        'background:#161b22;border:1px solid #30363d;border-radius:14px;box-shadow:0 14px 40px rgba(0,0,0,.45);'
        'padding:40px 48px 70px!important;margin:0 0 28px!important;scroll-margin-top:16px}'
        '.slide.title-slide{min-height:420px;background:radial-gradient(circle at center,#1f242d 0%,#0d1117 100%)}'
        '.content-area{overflow:visible!important}'
        '.slide-footer{left:48px!important;right:48px!important}'
        '.nav-controls{display:none!important}'
        '@media (max-width:760px){.content-area{flex-direction:column!important}'
        '.slide{padding:26px 18px 64px!important}.slide-footer{left:18px!important;right:18px!important}'
        '.title-slide h1{font-size:2.2rem!important}.slide-header{flex-wrap:wrap;gap:6px}.slide-header h2{font-size:1.5rem!important}}'
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

# Pages without their own side contents: they get the shared left panel on wide screens.
# Every page gets the shared "Contents" drawer on narrow screens.
WIDE_TOC = {
    'unit-1-1-routers-and-switches.html', 'unit-1-2-ip-addressing-review.html', 'unit-1-3-cisco-ios-cli-basics.html',
    'unit-2-2-switching-methods.html', 'unit-2-3-mac-address-table.html', 'unit-2-3-basic-switch-setup.html',
    'unit-2-4-managing-switch-configuration.html', 'unit-3-1-vlan-concepts.html',
    'unit-4-static-routing.html', 'unit-5-distance-vector-rip.html',
}
# Pages whose own sticky contents list must scroll on its own instead of running off screen.
_SCROLL_OWN_TOC = '@media (min-width:901px){nav.toc{max-height:calc(100vh - 48px);overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin}}'
for _f in ('unit-1-number-systems.html', 'unit-4-combinational-logic.html', 'unit-5-combinational-logic-msi-lsi.html',
           'unit-6-sequential-logic.html', 'unit-7-registers-and-counters.html',
           'unit-6-link-state-and-hybrid-routing.html', 'unit-6-3-eigrp.html', 'unit-6-lab-ospf.html', 'unit-6-lab-eigrp.html'):
    PAGE_CSS[_f] = PAGE_CSS.get(_f, '') + _SCROLL_OWN_TOC

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
#nkg-unitfoot .nkg-copy a.nkg-priv{color:#c9a14a!important;font:inherit}
@media (max-width:640px){
  #nkg-unitbar .nkg-subj,#nkg-unitbar .nkg-sep{display:none}
  #nkg-unitbar .nkg-btn span{display:none}
  #nkg-unitbar .nkg-btn{padding:0 10px}
}
@media (max-width:760px){table{display:block;max-width:100%;overflow-x:auto}}
#nkg-unitbar .nkg-tocbtn{display:none}
html.nkg-toc-narrow #nkg-unitbar .nkg-tocbtn{display:inline-flex}
#nkg-toc{all:initial;position:fixed;z-index:2147482990;left:12px;top:62px;width:260px;display:none;flex-direction:column;box-sizing:border-box;
  background:#0b1d3a;color:#cdd5e3;border:1px solid rgba(201,161,74,.35);border-radius:12px;box-shadow:0 10px 30px rgba(6,18,42,.28);
  font:500 13.5px/1.35 Inter,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;-webkit-font-smoothing:antialiased;overflow:hidden}
#nkg-toc *{box-sizing:border-box}
html.nkg-toc-wide #nkg-toc[data-wide="1"]{display:flex}
#nkg-toc .nkg-toc-h{flex:none;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:14px 14px 12px 16px;
  font:600 11px/1 Inter,-apple-system,"Segoe UI",sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#c9a14a;border-bottom:1px solid rgba(251,249,243,.1)}
#nkg-toc .nkg-toc-x{display:none;place-items:center;width:30px;height:30px;border-radius:6px;border:1px solid rgba(251,249,243,.22);color:#fbf9f3;font:400 18px/1 Inter,sans-serif;cursor:pointer;background:none}
#nkg-toc .nkg-toc-list{display:block;flex:1 1 auto;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:8px 8px 14px;scrollbar-width:thin;scrollbar-color:#1c3a78 transparent}
#nkg-toc a{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden;color:#cdd5e3!important;text-decoration:none!important;
  padding:7px 10px 7px 12px;margin:1px 0;border-left:2px solid transparent;border-radius:0 6px 6px 0;cursor:pointer}
#nkg-toc a.l3{padding-left:24px;font-size:12.5px;color:#9fb0c8!important}
#nkg-toc a:hover{background:rgba(251,249,243,.06);color:#fbf9f3!important}
#nkg-toc a.on{border-left-color:#c9a14a;background:rgba(201,161,74,.13);color:#fbf9f3!important}
html.nkg-toc-narrow #nkg-toc{z-index:2147483002;display:flex;left:0;top:0!important;bottom:0;height:auto!important;width:min(300px,86vw);border-radius:0 12px 12px 0;border-left:0;
  transform:translateX(-105%);visibility:hidden;transition:transform .25s ease,visibility .25s}
html.nkg-toc-narrow.nkg-toc-open #nkg-toc{transform:none;visibility:visible}
html.nkg-toc-narrow #nkg-toc .nkg-toc-x{display:inline-grid}
#nkg-toc-scrim{all:initial;display:none;position:fixed;inset:0;z-index:2147482989;background:rgba(6,18,42,.45)}
html.nkg-toc-open #nkg-toc-scrim{display:block;z-index:2147483001}
@media (prefers-reduced-motion:reduce){html.nkg-toc-narrow #nkg-toc{transition:none}}
"""

BAR_JS = r"""(function(){
var d=document,h=d.documentElement,B=d.body,bar=d.getElementById('nkg-unitbar'),ft=d.getElementById('nkg-unitfoot'),toc=d.getElementById('nkg-toc'),
list=toc&&toc.querySelector('.nkg-toc-list'),hs=[],links=[],basePL=null,wideOK=toc&&toc.getAttribute('data-wide')==='1';
function px(v){return parseFloat(v)||0}
if(toc){try{
  var all=[].slice.call(d.querySelectorAll('h2,h3')).filter(function(x){return !x.closest('#nkg-unitbar,#nkg-unitfoot,#nkg-toc')&&x.getClientRects().length&&x.textContent.trim()});
  if(all.filter(function(x){return x.tagName==='H2'}).length>8)all=all.filter(function(x){return x.tagName==='H2'});
  all.forEach(function(x,i){if(!x.id)x.id='nkg-s-'+(i+1);var a=d.createElement('a');a.href='#'+x.id;a.textContent=[].map.call(x.childNodes,function(c){return c.textContent}).join(' ').replace(/\s+/g,' ').trim();
    a.className=x.tagName==='H3'?'l3':'l2';a.addEventListener('click',function(){h.classList.remove('nkg-toc-open')});list.appendChild(a);hs.push(x);links.push(a)});
  if(!hs.length){toc.remove();toc=null;}
}catch(e){toc=null}}
function place(){if(!toc)return;
  if(h.classList.contains('nkg-toc-wide')){var top=Math.max(12,(bar?bar.getBoundingClientRect().bottom:0)+12),bot=innerHeight-12;
    if(ft){var fb=ft.getBoundingClientRect().top-12;if(fb<bot)bot=fb}toc.style.top=top+'px';toc.style.height=Math.max(140,bot-top)+'px'}
  else{toc.style.top='';toc.style.height=''}
  var cur=0;for(var i=0;i<hs.length;i++){if(hs[i].getBoundingClientRect().top<90)cur=i;else break}
  for(var j=0;j<links.length;j++)links[j].classList.toggle('on',j===cur);
  var a=links[cur];if(a&&list.clientHeight){if(a.offsetTop<list.scrollTop||a.offsetTop>list.scrollTop+list.clientHeight-40)list.scrollTop=a.offsetTop-list.clientHeight/3}}
function layout(){try{
  if(toc){if(basePL===null){B.style.removeProperty('padding-left');basePL=px(getComputedStyle(B).paddingLeft)}
    var wide=wideOK&&innerWidth>=1200;h.classList.toggle('nkg-toc-wide',wide);h.classList.toggle('nkg-toc-narrow',innerWidth<1200);
    if(wide){h.classList.remove('nkg-toc-open');B.style.setProperty('padding-left',(basePL+284)+'px','important')}else B.style.removeProperty('padding-left')}
  var cs=getComputedStyle(B),l=px(cs.paddingLeft)+px(cs.marginLeft),r=px(cs.paddingRight)+px(cs.marginRight);
  if(bar&&bar.getAttribute('data-mode')!=='fixed'){var t=px(cs.paddingTop)+px(cs.marginTop);bar.style.marginTop=-t+'px';bar.style.marginLeft=-l+'px';bar.style.marginRight=-r+'px';bar.style.marginBottom=px(cs.paddingTop)+'px'}
  if(ft){ft.style.marginLeft=-l+'px';ft.style.marginRight=-r+'px';ft.style.marginBottom=-(px(cs.paddingBottom)+px(cs.marginBottom))+'px'}
  place()}catch(e){}}
var tick=false;function onScroll(){if(!tick){tick=true;requestAnimationFrame(function(){tick=false;place()})}}
layout();addEventListener('resize',layout);addEventListener('scroll',onScroll,{passive:true});addEventListener('load',layout);
if(toc){var btn=d.querySelector('#nkg-unitbar .nkg-tocbtn'),sc=d.getElementById('nkg-toc-scrim'),x=toc.querySelector('.nkg-toc-x');
  function close(){h.classList.remove('nkg-toc-open')}
  if(btn)btn.addEventListener('click',function(e){e.preventDefault();h.classList.toggle('nkg-toc-open');place()});
  if(sc)sc.addEventListener('click',close);if(x)x.addEventListener('click',close);
  d.addEventListener('keydown',function(e){if(e.key==='Escape')close()});}
else{var b2=d.querySelector('#nkg-unitbar .nkg-tocbtn');if(b2)b2.remove()}
})();"""

FONT_LINK = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600&amp;display=swap">'



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
           f'<span class="nkg-nav"><a class="nkg-btn nkg-tocbtn" href="#" role="button" title="Contents">&#9776;<span> Contents</span></a>'
           f'{prev_btn}<a class="nkg-btn" href="{hub}" title="All units">&#9638;<span> All units</span></a>{next_btn}</span>'
           f'</span></nkg-unitbar>'
           f'<nkg-toc id="nkg-toc" data-wide="{1 if p["file"] in WIDE_TOC else 0}" role="navigation" aria-label="Page contents">'
           f'<span class="nkg-toc-h">Contents<button class="nkg-toc-x" type="button" aria-label="Close contents">&times;</button></span>'
           f'<span class="nkg-toc-list"></span></nkg-toc><nkg-scrim id="nkg-toc-scrim"></nkg-scrim><!--/nkg:bar-->')
    cards = []
    if prev:
        cards.append(f'<a class="nkg-card prev" href="{href(prev)}"><span class="nkg-k">&#8249; Previous</span><span class="nkg-t">{esc(prev["label"] + " · " + prev["topic"])}</span></a>')
    cards.append(f'<a class="nkg-card" href="{hub}"><span class="nkg-k">{esc(sub["code"])}</span><span class="nkg-t">All {esc(sub["name"])} units</span></a>')
    if nxt:
        cards.append(f'<a class="nkg-card next" href="{href(nxt)}"><span class="nkg-k">Next &#8250;</span><span class="nkg-t">{esc(nxt["label"] + " · " + nxt["topic"])}</span></a>')
    foot = (f'<!--nkg:foot--><nkg-unitfoot id="nkg-unitfoot" role="navigation" aria-label="Lesson navigation"><span class="nkg-in">'
            + ''.join(cards) +
            f'<span class="nkg-copy">&copy; Niraj Kumar Gupta · Teaching Hub · {esc(sub["name"])} ({esc(sub["code"])}) · <a class="nkg-priv" href="/privacy.html">Privacy &amp; terms</a></span>'
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
    write_text(path, s)


KIND_LABEL = {'notes': 'Lesson', 'slides': 'Slides', 'lab': 'Lab'}


def build_subject(key):
    sub = CATALOG[key]
    path = ROOT / 'teaching' / f'{key}.html'
    s = path.read_text(encoding='utf-8')
    units = sub['units']
    n_lessons = sum(1 for u in units for l in u[3] if l[3] != 'lab')
    n_labs = sum(1 for u in units for l in u[3] if l[3] == 'lab')
    n_files = sum(len(u[4]) for u in units)
    stats = [f'<span><strong>{sum(isinstance(u[0], int) for u in units)}</strong> units</span>', f'<span><strong>{n_lessons}</strong> lessons</span>']
    if n_labs:
        stats.append(f'<span><strong>{n_labs}</strong> lab guides</span>')
    if n_files:
        stats.append(f'<span><strong>{n_files}</strong> downloads</span>')
    jump = ''.join(f'<a href="#unit-{str(u[0]).lower()}">{u[0]}</a>' for u in units)
    blocks = []
    for num, utitle, usum, lessons, files in units:
        badge = f'<span>Unit</span>{num}' if isinstance(num, int) else f'<span>{esc(num)}</span>1–{units[-2][0]}'
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
        <article class="unit" id="unit-{str(num).lower()}">
          <div class="unit-num">{badge}</div>
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
    write_text(path, s)


if __name__ == '__main__':
    for key in CATALOG:
        seq = pages_in_order(key)
        for i in range(len(seq)):
            build_page(key, i, seq)
        build_subject(key)
        print(f'{key}: {len(seq)} pages + subject page')
