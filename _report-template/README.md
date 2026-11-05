# Client Marketing Reports

Every seller report is built from ONE template so they all look exactly like the Turkey Creek report.

- `report.html` – the report page; `__DATA__` and `__IMGS__` are filled per report.
- `_middleware.js` – the branded password screen (Cloudflare Pages Function); `__HASH__`, `__PATH__`, `__ADDRESS__`, `__CITY__` filled per report.
- `build.py report.json` – writes `<domain>/<path>/index.html`, `<domain>/functions/<path>/_middleware.js` and the noindex rule in `<domain>/_headers`.
- `reports/<id>.json` – the last-published copy of each report (meta + data + imgs). The live source of truth is the Client Marketing Report Dashboard database.

Each report lives on its listing's own domain at `/report-<random>/`, photos in `<domain>/<path>/img/`.
The hourly "Client reports – publish" scheduled task rebuilds any report changed in the dashboard and pushes here; Cloudflare Pages deploys on push.

## Publishing (no git needed)
A publish is ONE commit of `<domain>/<path>/data.json` (via Zapier GitHub "Create or Update File"). The password middleware serves `<path>/rev.txt` publicly from data.json's `rev`, so a publish is confirmed by fetching rev.txt.

## Weekly seller email
- `email.html` – the seller email (Mailchimp-safe tables); `email.py data.json meta.json out.html` fills it from the live data.json and prints the subject.
- Sent through Mailchimp audience "Seller Clients" (06ded627fa), one static segment per report named `report-<id>`, from Aaron Scott <aaron@mymusiccityagent.com>.
