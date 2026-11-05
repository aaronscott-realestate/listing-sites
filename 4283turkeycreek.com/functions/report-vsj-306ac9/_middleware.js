// Simple password gate for the seller report. Password is stored only as a hash.
const PASS_HASH = "cca4a946b4affb82629ca200b783b6bb6d541f6b5fb1e8026278fabdf9bd707d"; // sha256("tc-report:" + password)
const COOKIE = "tc_report";
const YEAR = 60 * 60 * 24 * 365;

async function sha(s) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map(b => b.toString(16).padStart(2, "0")).join("");
}

function page(err) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Your Marketing Report · 4283 Turkey Creek Rd</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0B1A33;color:#EEF1F4;font-family:Arial,Helvetica,sans-serif;padding:24px 16px}
.card{width:100%;max-width:400px;text-align:center}
img{width:96px;height:96px;display:block;margin:0 auto 22px}
.k{font-size:11px;letter-spacing:3px;font-weight:bold;color:#9FB0C8;text-transform:uppercase}
h1{font-size:30px;line-height:1.05;margin:10px 0 6px;text-transform:uppercase;letter-spacing:1px}
.c{font-size:13px;letter-spacing:3px;color:#9FB0C8;text-transform:uppercase}
.bar{height:4px;width:64px;background:#B3202C;margin:22px auto}
input{width:100%;font-size:18px;padding:16px;border:1px solid #5E6E86;background:#12264A;color:#fff;text-align:center;letter-spacing:1px;border-radius:0;-webkit-appearance:none}
input:focus{outline:2px solid #E04A55;outline-offset:0}
button{width:100%;margin-top:10px;font-size:16px;font-weight:bold;letter-spacing:2px;text-transform:uppercase;padding:17px;border:0;background:#B3202C;color:#fff;cursor:pointer;border-radius:0}
.e{color:#E04A55;font-size:14px;margin:0 0 12px;font-weight:bold}
.n{font-size:12px;color:#7D8CA3;margin-top:14px;line-height:1.5}
</style></head><body><form class="card" method="POST">
<img src="/media/aaron-scott-seal.png" alt="Aaron Scott">
<div class="k">Your Marketing Report</div>
<h1>4283 Turkey Creek Rd</h1><div class="c">Williamsport, Tennessee</div>
<div class="bar"></div>
${err ? '<p class="e">That password didn\'t match. Try again.</p>' : ''}
<input type="password" name="pw" placeholder="Password" inputmode="numeric" pattern="[0-9]*" autocomplete="off" required autofocus>
<button type="submit">Open the report</button>
<div class="n">You'll only need this once on each phone or computer.</div>
</form></body></html>`;
}

const html = (body, status = 200, extra = {}) => new Response(body, {
  status, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex, nofollow", ...extra }
});

export async function onRequest(ctx) {
  const { request, next } = ctx;
  // rev.txt is public (just a version stamp) so publishing can confirm the update went live
  if (new URL(request.url).pathname.endsWith("/rev.txt")) return next();
  const cookie = request.headers.get("cookie") || "";
  const m = cookie.match(new RegExp("(?:^|; )" + COOKIE + "=([a-f0-9]{64})"));
  if (m && m[1] === PASS_HASH) return next();

  if (request.method === "POST") {
    const form = await request.formData();
    const pw = String(form.get("pw") || "").trim().toLowerCase().replace(/\s+/g, "");
    if ((await sha("tc-report:" + pw)) === PASS_HASH) {
      const url = new URL(request.url);
      return new Response(null, { status: 303, headers: {
        location: url.pathname + url.search,
        "set-cookie": `${COOKIE}=${PASS_HASH}; Max-Age=${YEAR}; Path=/report-vsj-306ac9; Secure; HttpOnly; SameSite=Lax`,
        "cache-control": "no-store"
      }});
    }
    return html(page(true), 401);
  }
  return html(page(false), 401);
}
