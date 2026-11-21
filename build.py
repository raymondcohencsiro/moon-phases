#!/usr/bin/env python3
"""Build both copies of the Moon phases simulator from one source (src/index.html).

  the repo's top level   the GitHub Pages website: index.html, separate WebP images
                         (assets/), three.js copied into vendor/, an offline service
                         worker (sw.js) and an app manifest, so it can be installed
  dist/moon_phases.html  one self-contained file for claude.ai: images embedded as data:
                         URIs, three.js from the jsDelivr CDN (all claude.ai allows)

Usage:  npm install          (once: fetches three.js 0.170.0 into node_modules/)
        pip install pillow   (once)
        python3 build.py

Edit src/index.html, never the built index.html at the top level.
"""
import base64, io, json, pathlib, shutil
from PIL import Image

BUILD_NO = 8
BUILD = f"build {BUILD_NO} · 21 Nov 2026"
THREE_VERSION = "0.170.0"

ROOT = pathlib.Path(__file__).parent
SRC, SITE, DIST = ROOT / "src", ROOT, ROOT / "dist"
THREE = ROOT / "node_modules" / "three"
ADDONS = ["controls/OrbitControls.js", "lines/Line2.js", "lines/LineMaterial.js",
          "lines/LineGeometry.js", "lines/LineSegments2.js", "lines/LineSegmentsGeometry.js"]


def webp(src, quality=75):
    buf = io.BytesIO()
    Image.open(src).convert("RGB").save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def fill(template, **values):
    for k, v in values.items():
        template = template.replace(f"__{k}__", v)
    assert "__" + "IMPORTMAP" + "__" not in template
    return template


def importmap(base):
    return json.dumps({"imports": {"three": f"{base}build/three.module.min.js",
                                   "three/addons/": f"{base}examples/jsm/"}}, indent=2)


def main():
    tpl = (SRC / "index.html").read_text(encoding="utf-8")
    land = (SRC / "assets" / "land.json").read_text(encoding="utf-8").strip()
    earth, moon = webp(SRC / "assets" / "earth.jpg"), webp(SRC / "assets" / "moon.jpg")

    # ---- GitHub Pages site ----------------------------------------------------------
    for old in ["assets", "vendor", "icons", "vr"]:        # built folders only
        if (SITE / old).exists():
            shutil.rmtree(SITE / old)
    (SITE / "assets").mkdir(parents=True)
    (SITE / "assets" / "earth.webp").write_bytes(earth)
    (SITE / "assets" / "moon.webp").write_bytes(moon)
    for rel in ["build/three.module.min.js", "LICENSE"] + [f"examples/jsm/{a}" for a in ADDONS]:
        dst = SITE / "vendor" / "three" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(THREE / rel, dst)
    shutil.copytree(SRC / "icons", SITE / "icons")
    head = "\n".join([
        '<link rel="manifest" href="manifest.webmanifest">',
        '<meta name="theme-color" content="#1b1d24">',
        '<link rel="apple-touch-icon" href="icons/icon-192.png">',
    ])
    html = fill(tpl, IMPORTMAP=importmap("./vendor/three/"), LAND_JSON=land, TARGET="site", BUILD=BUILD,
                EARTH_URL="assets/earth.webp", MOON_URL="assets/moon.webp")
    html = html.replace("<!--HEAD_EXTRA-->", head)
    (SITE / "index.html").write_text(html, encoding="utf-8")

    # Old address (the first VR copy lived at /vr/): send people to the main page
    (SITE / "vr").mkdir()
    (SITE / "vr" / "index.html").write_text(
        '<!DOCTYPE html><meta charset="utf-8"><title>Phases of the Moon</title>'
        '<meta http-equiv="refresh" content="0; url=../">'
        '<script>location.replace("../" + location.search + location.hash)</script>'
        '<p>The simulator has moved to <a href="../">the main page</a>.</p>\n', encoding="utf-8")

    manifest = {
        "name": "Phases of the Moon", "short_name": "Moon Phases",
        "description": "Interactive 3D simulator of the phases of the Moon, with a VR mode.",
        "start_url": "./", "scope": "./", "display": "standalone",
        "background_color": "#1b1d24", "theme_color": "#1b1d24",
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (SITE / "manifest.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    cached = [SITE / "index.html", SITE / "manifest.webmanifest"] + [
        p for d in ["assets", "icons", "vendor"] for p in (SITE / d).rglob("*") if p.is_file() and p.name != "LICENSE"]
    files = sorted("./" + p.relative_to(SITE).as_posix() for p in cached)
    files = ["./" if f == "./index.html" else f for f in files]
    sw = (SRC / "sw.js").read_text(encoding="utf-8")
    sw = sw.replace("__CACHE__", f"moon-phases-v{BUILD_NO}").replace("__FILES__", json.dumps(files, indent=2))
    (SITE / "sw.js").write_text(sw, encoding="utf-8")
    (SITE / ".nojekyll").write_text("")     # serve files as they are (no Jekyll processing)

    # ---- claude.ai single file --------------------------------------------------------
    DIST.mkdir(exist_ok=True)
    b64 = lambda b: base64.b64encode(b).decode()
    one = fill(tpl, IMPORTMAP=importmap(f"https://cdn.jsdelivr.net/npm/three@{THREE_VERSION}/"),
               LAND_JSON=land, TARGET="claude", BUILD=BUILD,
               EARTH_URL="data:image/webp;base64," + b64(earth), MOON_URL="data:image/webp;base64," + b64(moon))
    one = one.replace("<!--HEAD_EXTRA-->\n", "")
    (DIST / "moon_phases.html").write_text(one, encoding="utf-8")

    total = sum((SITE / f).stat().st_size for f in files if f != "./") + (SITE / "index.html").stat().st_size
    print(f"{BUILD}: website {total // 1024} KB ({len(files)} files cached for offline use, index.html "
          f"{(SITE / 'index.html').stat().st_size // 1024} KB, earth {len(earth) // 1024} KB, moon {len(moon) // 1024} KB); "
          f"dist/moon_phases.html {(DIST / 'moon_phases.html').stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
