"""Build the contact-card QR codes.  Usage: python3 build_qr.py https://card.1aaronscott.com
Writes qr.svg (used by the page's #qr view) and print files in qr/ (navy on white, seal in the center)."""
import sys, os, qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw

URL = sys.argv[1] if len(sys.argv) > 1 else "https://card.1aaronscott.com"
NAVY = "#0B1A33"
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(here, "qr"), exist_ok=True)

qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, border=4)
qr.add_data(URL)
qr.make(fit=True)
m = qr.get_matrix()  # includes border
n = len(m)

# --- SVG (modules only; the seal is layered on top in the page) ---
cells = "".join(f"M{x} {y}h1v1h-1z" for y, row in enumerate(m) for x, v in enumerate(row) if v)
hole = n * 0.26
c0 = (n - hole) / 2
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
       f'<rect width="{n}" height="{n}" fill="#fff"/><path d="{cells}" fill="{NAVY}"/>'
       f'<rect x="{c0:.2f}" y="{c0:.2f}" width="{hole:.2f}" height="{hole:.2f}" fill="#fff"/></svg>')
open(os.path.join(here, "qr.svg"), "w").write(svg)

# --- Print PNGs with the seal centered ---
seal = Image.open(os.path.join(here, "media", "aaron-scott-seal.png")).convert("RGBA")
for px in (1200, 3000):
    box = px // n
    size = box * n
    img = Image.new("RGB", (size, size), "white")
    d = ImageDraw.Draw(img)
    for y, row in enumerate(m):
        for x, v in enumerate(row):
            if v:
                d.rectangle([x * box, y * box, (x + 1) * box - 1, (y + 1) * box - 1], fill=NAVY)
    s = int(size * 0.24)
    pad = int(s * 0.08)
    cx = (size - s) // 2
    d.ellipse([cx - pad, cx - pad, cx + s + pad, cx + s + pad], fill="white")
    img.paste(seal.resize((s, s), Image.LANCZOS), (cx, cx), seal.resize((s, s), Image.LANCZOS))
    img.save(os.path.join(here, "qr", f"aaron-scott-contact-qr-{px}.png"))
import base64
b64 = base64.b64encode(open(os.path.join(here, "media", "aaron-scott-seal.png"), "rb").read()).decode()
sz = n * 0.24
o = (n - sz) / 2
print_svg = svg.replace("</svg>", f'<image x="{o:.2f}" y="{o:.2f}" width="{sz:.2f}" height="{sz:.2f}" href="data:image/png;base64,{b64}"/></svg>')
open(os.path.join(here, "qr", "aaron-scott-contact-qr.svg"), "w").write(print_svg)
print("QR for", URL, "-", n, "modules")
