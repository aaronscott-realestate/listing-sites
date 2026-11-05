#!/usr/bin/env python3
"""Render the weekly seller email for one report.

Usage: python3 email.py data.json meta.json [out.html]
data.json = the report's live data (<domain>/<path>/data.json)
meta.json = {"domain","path","sellers","emailHero"}
Prints the subject line; writes the HTML (default email-out.html).
Numbers match the live report exactly: social reach total, the six boxes.
"""
import json, sys, os, html, datetime
from zoneinfo import ZoneInfo

here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1])); m = json.load(open(sys.argv[2]))
out = sys.argv[3] if len(sys.argv) > 3 else "email-out.html"
today = datetime.datetime.now(ZoneInfo("America/Chicago")).date()
start = datetime.date.fromisoformat(d["start"])
days = max(1, (today - start).days + 1)
week = (days - 1) // 7 + 1
social = sum((r.get("v") or 0) for r in d.get("social", []))
e = lambda x: html.escape(str(x))
sellers = (m.get("sellers") or "").strip()
vals = {
  "REPORT_URL": "https://%s/%s/" % (m["domain"], m["path"]),
  "HERO": m.get("emailHero") or "https://4283turkeycreek.com/media/email-hero-drone.jpg",
  "ADDRESS": e(d["address"]), "CITY": e(d.get("city", "")),
  "GREETING": (e(sellers) + ", ") if sellers else "",
  "WEEK": str(week), "SOCIAL": "{:,}".format(social),
  "B_LAUNCH": str(d.get("actions", {}).get("launch", 0)), "B_PRE": str(d.get("actions", {}).get("pre", 0)),
  "B_PHOTOS": str(d.get("photoCount", 0)), "B_VIDEO": str(d.get("videoAssets", 0)),
  "B_PLACE": str(len(d.get("channels", []))), "B_DAYS": str(days),
}
t = open(os.path.join(here, "email.html")).read()
for k, v in vals.items(): t = t.replace("{{%s}}" % k, v)
if not sellers: t = t.replace("here's where your home", "Here's where your home")
assert "{{" not in t, "unfilled placeholder"
open(out, "w").write(t)
print("Week %d: your marketing report for %s" % (week, d["address"]))
