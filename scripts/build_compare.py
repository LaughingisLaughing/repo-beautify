#!/usr/bin/env python3
"""Build a single-file HTML page that renders multiple README variants
side-by-side with GitHub CSS, so the user can pick a style in the browser.

Usage:
  python3 build_compare.py --repo OWNER/REPO --out compare.html v1.md v2.md ...
  python3 build_compare.py --repo OWNER/REPO --manifest variants.json --out compare.html

Manifest format (optional, enriches the tab header cards):
  [{"file": "v1.md", "name": "V1 Classic", "tool": "othneildrew/Best-README-Template",
    "url": "https://github.com/...", "stars": "16k", "status": "active",
    "effort": "...", "pros": "...", "cons": "...", "fit": "..."}]

Without a manifest, tabs are labeled by filename.
"""
import argparse
import html
import json
from pathlib import Path

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<link id="gh-css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown-light.min.css">
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  :root { --bg:#f6f8fa; --card:#fff; --ink:#1f2328; --muted:#59636e; --line:#d1d9e0; --accent:#6366f1; }
  * { box-sizing:border-box }
  body { margin:0; background:var(--bg); color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif }
  .shell { max-width:1080px; margin:0 auto; padding:32px 20px 80px }
  header h1 { font-size:24px; margin:0 0 6px } header p { color:var(--muted); margin:0; line-height:1.7 }
  .tabs { display:flex; gap:8px; flex-wrap:wrap; position:sticky; top:0; background:var(--bg);
    padding:14px 0 12px; z-index:50; border-bottom:1px solid var(--line) }
  .tab { border:1px solid var(--line); background:var(--card); color:var(--ink); padding:8px 16px;
    border-radius:999px; cursor:pointer; font-size:14px; font-weight:600 }
  .tab.active { background:var(--accent); color:#fff; border-color:var(--accent) }
  .theme-toggle { margin-left:auto; border:1px solid var(--line); background:var(--card);
    border-radius:999px; padding:8px 14px; cursor:pointer; font-size:13px }
  .meta { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 20px; margin:18px 0 14px }
  .meta h2 { margin:0 0 4px; font-size:17px } .meta .toolline { color:var(--muted); font-size:13px; margin-bottom:10px }
  .meta .toolline a { color:var(--accent); text-decoration:none }
  .meta .grid { display:grid; grid-template-columns:64px 1fr; gap:5px 10px; font-size:13.5px; line-height:1.6 }
  .meta .k { color:var(--muted); font-weight:600 }
  .preview-frame { border:1px solid var(--line); border-radius:12px; overflow:hidden; background:var(--card) }
  .preview-bar { padding:10px 14px; border-bottom:1px solid var(--line); background:#f0f3f6; font-size:12px; color:var(--muted) }
  .markdown-body { padding:32px 40px; max-width:none }
  body.dark { --bg:#0d1117; --card:#161b22; --ink:#e6edf3; --muted:#9198a1; --line:#30363d }
  body.dark .preview-bar { background:#21262d }
  .panel { display:none } .panel.active { display:block }
  .hint { text-align:center; color:var(--muted); font-size:13px; margin-top:24px; line-height:1.8 }
</style>
</head>
<body>
<div class="shell">
  <header>
    <h1>__TITLE__</h1>
    <p>Each tab renders one README variant with GitHub CSS. Badges and banners load live, so what you see is what GitHub shows.</p>
  </header>
  <nav class="tabs" id="tabs"></nav>
  <main id="panels"></main>
  <p class="hint">Reply with the variant name you want. The toggle at the top right previews GitHub dark mode.</p>
</div>
<script>
const VARIANTS = __DATA__;
const REPO = __REPO__;
marked.setOptions({ gfm:true });
mermaid.initialize({ startOnLoad:false });
const tabsEl = document.getElementById('tabs'), panelsEl = document.getElementById('panels');
VARIANTS.forEach((v,i) => {
  const tab = document.createElement('button');
  tab.className = 'tab' + (i===0?' active':'');
  tab.textContent = v.name; tab.dataset.target = 'p'+i;
  tab.onclick = () => activate('p'+i);
  tabsEl.appendChild(tab);
  let h = marked.parse(v.markdown);
  h = h.replace(/<pre><code class="language-mermaid">([\\s\\S]*?)<\\/code><\\/pre>/g, (m,c) => {
    const t = document.createElement('textarea'); t.innerHTML = c;
    return '<div class="mermaid">' + t.value + '</div>';
  });
  // GitHub sanitizes README HTML; mirror that so the preview matches reality and stays safe locally
  h = DOMPurify.sanitize(h, {FORBID_TAGS: ['script', 'style'], ADD_ATTR: ['align', 'width', 'height']});
  const metaRows = ['effort','pros','cons','fit']
    .filter(k => v[k]).map(k => `<span class="k">${k}</span><span>${v[k]}</span>`).join('');
  const toolline = v.tool ? `<div class="toolline">source: <a href="${v.url||'#'}" target="_blank">${v.tool}</a>${v.stars?' · ⭐'+v.stars:''}${v.status?' · '+v.status:''}</div>` : '';
  const panel = document.createElement('section');
  panel.className = 'panel' + (i===0?' active':''); panel.id = 'p'+i;
  panel.innerHTML = `
    <div class="meta"><h2>${v.name}</h2>${toolline}${metaRows?'<div class="grid">'+metaRows+'</div>':''}</div>
    <div class="preview-frame">
      <div class="preview-bar">github.com/${REPO} · README.md preview</div>
      <article class="markdown-body">${h}</article>
    </div>`;
  panelsEl.appendChild(panel);
});
const toggle = document.createElement('button');
toggle.className = 'theme-toggle'; toggle.textContent = '🌙 dark';
toggle.onclick = () => {
  const dark = document.body.classList.toggle('dark');
  document.getElementById('gh-css').href =
    'https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown-' + (dark?'dark':'light') + '.min.css';
  toggle.textContent = dark ? '☀️ light' : '🌙 dark';
  renderMermaid(true);
};
tabsEl.appendChild(toggle);
function activate(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.target===id));
  document.querySelectorAll('.panel').forEach(p => p.classList.toggle('active', p.id===id));
  window.scrollTo({top:0}); renderMermaid();
}
let seq = 0;
function renderMermaid(force) {
  const dark = document.body.classList.contains('dark');
  mermaid.initialize({ startOnLoad:false, theme: dark?'dark':'default' });
  document.querySelectorAll('.panel.active .mermaid').forEach(el => {
    if (el.dataset.done && !force) return;
    const src = el.dataset.src || el.textContent; el.dataset.src = src;
    mermaid.render('m'+(++seq), src).then(r => { el.innerHTML = r.svg; el.dataset.done='1'; }).catch(()=>{});
  });
}
renderMermaid();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="*", help="README variant .md files")
    ap.add_argument("--manifest", help="JSON manifest enriching variant cards")
    ap.add_argument("--repo", required=True, help="OWNER/REPO shown in the preview bar")
    ap.add_argument("--title", default=None, help="Page title")
    ap.add_argument("--out", default="readme-compare.html")
    args = ap.parse_args()

    variants = []
    if args.manifest:
        base = Path(args.manifest).parent
        for v in json.loads(Path(args.manifest).read_text(encoding="utf-8")):
            v["markdown"] = (base / v.pop("file")).read_text(encoding="utf-8")
            variants.append(v)
    for f in args.files:
        p = Path(f)
        variants.append({"name": p.stem, "markdown": p.read_text(encoding="utf-8")})
    if not variants:
        ap.error("provide variant .md files or --manifest")

    title = args.title or f"{args.repo} · README style comparison"
    page = (PAGE
            .replace("__TITLE__", html.escape(title))
            .replace("__DATA__", json.dumps(variants, ensure_ascii=False))
            .replace("__REPO__", json.dumps(args.repo)))
    Path(args.out).write_text(page, encoding="utf-8")
    print(f"OK -> {args.out} ({len(variants)} variants)")


if __name__ == "__main__":
    main()
