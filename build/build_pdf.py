# -*- coding: utf-8 -*-
"""Build a single RTL Persian PDF-ready HTML from the nextjs-react review course."""
import re, pathlib, markdown
from pygments.formatters import HtmlFormatter

BASE = pathlib.Path(__file__).resolve().parent.parent
BUILD = BASE / "build"

CHAPTERS = [
    ("README.md", "شروع مرور"),
    ("01-react-ui.md", "فصل ۱ — توصیف UI"),
    ("02-react-state.md", "فصل ۲ — مدیریت State"),
    ("03-react-escape-hatches.md", "فصل ۳ — Refs و Effects"),
    ("04-react-modern.md", "فصل ۴ — React 19 مدرن"),
    ("05-nextjs-structure.md", "فصل ۵ — ساختار و Routing"),
    ("06-server-client.md", "فصل ۶ — Server vs Client ⭐"),
    ("07-data-fetching.md", "فصل ۷ — Fetching و رندر"),
    ("08-server-actions.md", "فصل ۸ — Server Actions"),
    ("09-streaming-errors.md", "فصل ۹ — Streaming و ارورها"),
    ("10-optimization.md", "فصل ۱۰ — Image/Font/Metadata"),
    ("11-route-handlers.md", "فصل ۱۱ — API، Middleware، Deploy"),
    ("12-cheatsheets.md", "فصل ۱۲ — چیت‌شیت و مصاحبه"),
    ("13-faq-deep-dive.md", "فصل ۱۳ — عمق‌سنجی ۹ سوال کلیدی"),
]

ANCHOR = {fn: f"ch{i:02d}" for i, (fn, _) in enumerate(CHAPTERS)}
LINK_RE = re.compile(r"\]\((\.?/?)([\w\-]+\.md)([#\w\-]*)\)")

MD_EXT = ["tables", "fenced_code", "codehilite", "md_in_html", "attr_list", "sane_lists"]
MD_CFG = {"codehilite": {"guess_lang": False}}


def preprocess(text: str) -> str:
    def repl(m):
        target, frag = m.group(2), m.group(3) or ""
        if target in ANCHOR:
            return f"](#{ANCHOR[target]}{frag})"
        return m.group(0)
    text = LINK_RE.sub(repl, text)
    text = re.sub(r"```mermaid\n(.*?)```", lambda m: f'<div class="mermaid">\n{m.group(1)}</div>', text, flags=re.S)
    text = text.replace("<details>", '<details markdown="1" open>')
    text = text.replace("<summary>", '<summary markdown="span">')
    return text


def render_chapter(fn: str, idx: int) -> str:
    raw = (BASE / fn).read_text(encoding="utf-8")
    body = markdown.markdown(preprocess(raw), extensions=MD_EXT, extension_configs=MD_CFG)
    return f'<section class="chapter" id="ch{idx:02d}">{body}</section>'


CSS = """
@font-face { font-family:'Vazirmatn'; src:url('fonts/Vazirmatn-Regular.ttf') format('truetype'); font-weight:400; }
@font-face { font-family:'Vazirmatn'; src:url('fonts/Vazirmatn-Medium.ttf') format('truetype'); font-weight:500; }
@font-face { font-family:'Vazirmatn'; src:url('fonts/Vazirmatn-Bold.ttf') format('truetype'); font-weight:700; }
@font-face { font-family:'JetBrains Mono'; src:url('fonts/JetBrainsMono-Regular.ttf') format('truetype'); font-weight:400; }
@font-face { font-family:'JetBrains Mono'; src:url('fonts/JetBrainsMono-Bold.ttf') format('truetype'); font-weight:700; }

@page { size: A4; margin: 16mm 13mm 18mm 13mm; }

:root {
  --ink:#18181b; --muted:#6b7280; --line:#e5e7eb;
  --primary:#0e7490; --primary-soft:#ecfeff;
  --accent:#4338ca; --accent-soft:#eef2ff;
  --green:#059669; --green-soft:#ecfdf5;
  --amber:#b45309; --amber-soft:#fffbeb;
  --rose:#be123c; --rose-soft:#fff1f2;
  --code-bg:#09090b; --code-ink:#e4e4e7;
}
* { box-sizing:border-box; }
html { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body {
  direction:rtl; text-align:right;
  font-family:'Vazirmatn', Tahoma, sans-serif;
  color:var(--ink); font-size:11.2pt; line-height:2;
  margin:0; padding:0;
}

/* cover — Next.js مینیمال مشکی */
.cover {
  page-break-after:always; height:250mm;
  display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center; color:#fff; border-radius:14px; padding:20mm;
  background:linear-gradient(135deg,#09090b 0%,#1e293b 55%,#0e7490 130%);
}
.cover .badge { background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.35);
  padding:4px 18px; border-radius:999px; font-size:10pt; letter-spacing:.3px; }
.cover h1 { font-size:30pt; line-height:1.6; margin:14px 0 6px; border:none; color:#fff; background:none; }
.cover h2 { font-size:14pt; font-weight:500; color:#a5f3fc; border:none; margin:0; }
.cover .stack { display:flex; gap:10px; margin-top:26px; flex-wrap:wrap; justify-content:center; }
.cover .stack span { background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.3);
  border-radius:10px; padding:6px 16px; font-size:10.5pt; }
.cover .foot { margin-top:40px; font-size:9.5pt; opacity:.85; }

/* toc */
.toc { page-break-after:always; }
.toc h1 { border:none; }
.toc ol { list-style:none; padding:0; counter-reset:toc; }
.toc li { counter-increment:toc; border-bottom:1px dashed var(--line);
  padding:9px 2px; display:flex; justify-content:space-between; align-items:baseline; }
.toc a { text-decoration:none; color:var(--ink); font-weight:500; }
.toc li::before { content:counter(toc); background:var(--code-bg); color:#67e8f9;
  font-weight:700; border-radius:8px; width:30px; height:30px; display:inline-flex;
  align-items:center; justify-content:center; margin-left:14px; flex:none; }
.toc li .desc { color:var(--muted); font-size:9.5pt; }

/* chapters / headings */
.chapter { page-break-before:always; }
h1 {
  font-size:19pt; color:#fff; background:linear-gradient(90deg,#18181b,#334155);
  padding:14px 22px; border-radius:12px; line-height:1.7;
  margin:0 0 18px; page-break-after:avoid;
}
h2 {
  color:var(--primary); font-size:14.5pt; margin:26px 0 10px;
  padding-right:12px; border-right:4px solid var(--primary); line-height:1.8;
  page-break-after:avoid;
}
h3 { color:var(--accent); font-size:12.5pt; margin:20px 0 8px; page-break-after:avoid; }
p { margin:8px 0; }
strong { color:#111827; }
a { color:var(--primary); text-decoration:none; }

/* lists */
ul, ol { padding-right:1.6em; padding-left:0; margin:8px 0; }
li { margin:3px 0; }
li::marker { color:var(--primary); font-weight:700; }
input[type="checkbox"] { accent-color:var(--primary); }

/* tables */
table { border-collapse:collapse; width:100%; margin:12px 0; font-size:10pt;
  border-radius:10px; overflow:hidden; page-break-inside:avoid; }
th { background:linear-gradient(90deg,#18181b,#334155); color:#fff; font-weight:700; }
th, td { border:1px solid #dbe1ea; padding:6px 10px; text-align:right; vertical-align:top; }
tbody tr:nth-child(even) { background:#f8fafc; }

/* code */
pre, code, kbd { font-family:'JetBrains Mono','Vazirmatn',Consolas,monospace; direction:ltr; }
code { background:#ecfeff; color:#0e7490; padding:1px 6px; border-radius:5px;
  font-size:8.8pt; unicode-bidi:embed; }
pre { background:var(--code-bg); color:var(--code-ink); direction:ltr; text-align:left;
  padding:13px 16px; border-radius:12px; overflow-x:hidden; font-size:8.6pt;
  line-height:1.65; margin:10px 0; border:1px solid #27272a; page-break-inside:avoid; }
pre code { background:none; color:inherit; padding:0; font-size:inherit; }
.codehilite { background:var(--code-bg); border-radius:12px; margin:10px 0; page-break-inside:avoid; }
.codehilite pre { margin:0; border:none; }
.codehilite .k,.codehilite .kd,.codehilite .kn,.codehilite .ow { color:#67e8f9; }
.codehilite .s,.codehilite .s1,.codehilite .s2,.codehilite .sd { color:#86efac; }
.codehilite .n,.codehilite .na,.codehilite .nx { color:#e4e4e7; }
.codehilite .nf { color:#fbbf24; }
.codehilite .mi,.codehilite .mf { color:#fda4af; }
.codehilite .o,.codehilite .p { color:#a1a1aa; }
.codehilite .nb,.codehilite .nv { color:#7dd3fc; }
.codehilite .err { color:#e4e4e7; background:none; border:none; }
.codehilite .c,.codehilite .c1,.codehilite .cm,.codehilite .cp { color:#71717a !important; font-style:italic; }
.codehilite .nt { color:#f0abfc; }
.codehilite .nd { color:#fbbf24; }

/* blockquotes */
blockquote {
  margin:12px 0; padding:10px 16px; border-radius:12px;
  border-right:5px solid var(--primary); background:var(--primary-soft);
  page-break-inside:avoid;
}
blockquote p { margin:4px 0; }
blockquote p:first-child { font-weight:500; }
blockquote:has(> p:first-child strong:contains("⚠")) { background:var(--amber-soft); border-right-color:var(--amber); }
blockquote:has(> p:first-child strong:contains("🚨")) { background:var(--rose-soft); border-right-color:var(--rose); }
blockquote:has(> p:first-child strong:contains("💡")) { background:var(--green-soft); border-right-color:var(--green); }
blockquote:has(> p:first-child strong:contains("🔑")) { background:var(--green-soft); border-right-color:var(--green); }
blockquote:has(> p:first-child strong:contains("🎯")) { background:var(--primary-soft); border-right-color:var(--primary); }
blockquote:has(> p:first-child strong:contains("⭐")) { background:var(--accent-soft); border-right-color:var(--accent); }
blockquote:has(> p:first-child strong:contains("📖")) { background:#f4f4f5; border-right-color:#52525b; }

/* hr, details */
hr { border:none; border-top:2px dashed var(--line); margin:22px 0; }
details { background:#f8fafc; border:1px solid var(--line); border-radius:10px;
  padding:8px 14px; margin:10px 0; page-break-inside:avoid; }
summary { cursor:pointer; font-weight:700; color:var(--green); }

/* mermaid */
.mermaid {
  background:#fff; border:1px solid var(--line); border-radius:12px;
  padding:10px; margin:12px 0; text-align:center; page-break-inside:avoid;
  display:flex; justify-content:center;
}
.mermaid svg { max-width:100%; height:auto; }

del { color:var(--muted); }
em { color:#27272a; }
"""

PYGMENTS_CSS = HtmlFormatter(style="default").get_style_defs(".codehilite")

COVER = """
<section class="cover">
  <div class="badge">مرور جامع بر اساس داکیومنت رسمی — سپتامبر ۲۰۲۶</div>
  <h1>React 19 + Next.js 16<br/>مرور صفر تا مصاحبه</h1>
  <h2>فصل‌بندی مطابق react.dev و nextjs.org/docs — با مثال، تمرین و جواب</h2>
  <div class="stack">
    <span>Server Components</span><span>Server Actions</span><span>ISR &amp; Caching</span>
    <span>Streaming &amp; Suspense</span><span>React 19 Hooks</span><span>Deployment</span>
  </div>
  <div class="foot">۱۳ فصل در دو بخش · چیت‌شیت دوتایی · ۲۰ سوال مصاحبه با جواب</div>
</section>
"""

DESCS = {
    "README.md": "نقشه مرور و روش استفاده",
    "01-react-ui.md": "کامپوننت خالص، props، key، تله &&",
    "02-react-state.md": "snapshot، immutable، reducer، Context",
    "03-react-escape-hatches.md": "useRef، useEffect، custom hooks",
    "04-react-modern.md": "use، useActionState، useOptimistic",
    "05-nextjs-structure.md": "قرارداد فایل‌ها، layout، Link",
    "06-server-client.md": "مرز RSC، serialization، ترکیب",
    "07-data-fetching.md": "SSG/ISR/SSR، caching، Promise.all",
    "08-server-actions.md": "فرم‌ها، zod، revalidate",
    "09-streaming-errors.md": "Suspense، loading/error/not-found",
    "10-optimization.md": "Image، Font، Metadata، sitemap",
    "11-route-handlers.md": "route.ts، middleware، env، deploy",
    "12-cheatsheets.md": "چیت‌شیت دوتایی + ۲۰ سوال مصاحبه",
    "13-faq-deep-dive.md": "use، useActionState، forwardRef، Edge، RSC Payload، Hydration، RPC",
}


def build_toc() -> str:
    items = []
    for i, (fn, title) in enumerate(CHAPTERS):
        items.append(f'<li><a href="#ch{i:02d}">{title}</a><span class="desc">{DESCS.get(fn, "")}</span></li>')
    return f'<section class="toc"><h1>فهرست مطالب</h1><ol>{"".join(items)}</ol></section>'


def main():
    parts = [COVER, build_toc()]
    for i, (fn, _) in enumerate(CHAPTERS):
        parts.append(render_chapter(fn, i))
    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8"/>
<title>مرور React + Next.js</title>
<style>{CSS}
{PYGMENTS_CSS}
</style></head>
<body>{''.join(parts)}
<script src="mermaid.min.js"></script>
<script>mermaid.initialize({{ startOnLoad:true, theme:'base',
  themeVariables: {{ fontFamily:'Vazirmatn, Tahoma', fontSize:'13px',
    primaryColor:'#ecfeff', primaryBorderColor:'#0e7490', primaryTextColor:'#18181b',
    lineColor:'#64748b', secondaryColor:'#eef2ff', tertiaryColor:'#f8fafc' }},
  flowchart: {{ htmlLabels:true, curve:'basis' }} }});</script>
</body></html>"""
    out = BUILD / "course.html"
    out.write_text(html, encoding="utf-8")
    print(f"OK -> {out}  ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
