#!/usr/bin/env python3
"""Build one client marketing report from a report JSON file.

Usage: python3 _report-template/build.py report.json [--check]

report.json = {
  "meta": {"domain": "4283turkeycreek.com", "path": "report-vsj-306ac9", "password": "3824", ...},
  "data": { ...the report data (same shape as Turkey Creek)... },
  "imgs": { "key": "img/file.jpg", ... }   # files already placed in <domain>/<path>/img/
}
Writes <domain>/<path>/index.html, <domain>/functions/<path>/_middleware.js and the
noindex block in <domain>/_headers. Every report uses the same template, so they all
look exactly like the Turkey Creek report.
"""
import json, hashlib, html, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, "_report-template")

def build(rep, check=False):
    m, d, imgs = rep["meta"], rep["data"], rep.get("imgs", {})
    dom, path = m["domain"].strip().lower(), m["path"].strip("/")
    assert re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}", dom), dom
    assert re.fullmatch(r"report-[a-z0-9-]+", path), path
    pw = str(m["password"]).strip().lower().replace(" ", "")
    assert pw, "password required"
    d = dict(d); d["domain"] = dom
    dj = json.dumps(d, ensure_ascii=False, indent=1).replace("</", "<\\/")
    ij = json.dumps(imgs, ensure_ascii=False).replace("</", "<\\/")
    page = open(os.path.join(T, "report.html")).read()
    page = page.replace("__DATA__", "\n" + dj + "\n").replace("__IMGS__", ij)
    mw = open(os.path.join(T, "_middleware.js")).read()
    h = hashlib.sha256(("tc-report:" + pw).encode()).hexdigest()
    mw = (mw.replace("__HASH__", h).replace("__PATH__", path)
            .replace("__ADDRESS__", html.escape(d.get("address", ""))).replace("__CITY__", html.escape(d.get("city", ""))))
    outs = {
        os.path.join(ROOT, dom, path, "index.html"): page,
        os.path.join(ROOT, dom, "functions", path, "_middleware.js"): mw,
        os.path.join(ROOT, dom, path, "rev.txt"): str(d.get("rev", "")) + "\n",
    }
    hp = os.path.join(ROOT, dom, "_headers")
    hdr = open(hp).read() if os.path.exists(hp) else ""
    block = "/%s/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Cache-Control: no-store\n" % path
    if ("/%s/*" % path) not in hdr:
        outs[hp] = (hdr.rstrip("\n") + "\n" if hdr.strip() else "") + block
    missing = [v for v in imgs.values() if not os.path.exists(os.path.join(ROOT, dom, path, v))]
    if missing: print("WARNING missing images:", missing)
    if check: return outs
    for p, txt in outs.items():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(txt)
        print("wrote", os.path.relpath(p, ROOT))
    return outs

if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), "--check" in sys.argv)
