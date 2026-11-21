"""Draw the app icons (a waxing gibbous Moon) with the same code the page uses."""
import asyncio, base64, pathlib, re
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).parent
src = (ROOT / "src" / "index.html").read_text()
fn = re.search(r"function drawIcon\(size, litFrac = 0\.78\) \{.*?\n\}\n", src, re.S).group(0)
async def main():
    async with async_playwright() as p:
        chrome = pathlib.Path("/usr/bin/google-chrome")
        b = await p.chromium.launch(executable_path=str(chrome) if chrome.exists() else None)
        pg = await b.new_page()
        await pg.set_content("<script>" + fn + """
          function maskable(size) {           // full-bleed background, Moon inside the safe zone
            const cv = document.createElement('canvas'); cv.width = cv.height = size; const g = cv.getContext('2d');
            g.fillStyle = '#1b1d24'; g.fillRect(0, 0, size, size);
            const img = new Image(); img.src = drawIcon(size);
            return new Promise(r => img.onload = () => { const k = 0.78, o = size * (1 - k) / 2;
              g.drawImage(img, o, o, size * k, size * k); r(cv.toDataURL('image/png')); });
          }</script>""")
        out = {"icon-192.png": "drawIcon(192)", "icon-512.png": "drawIcon(512)", "icon-maskable-512.png": "maskable(512)"}
        for name, js in out.items():
            uri = await pg.evaluate(js)
            (ROOT / "src" / "icons" / name).write_bytes(base64.b64decode(uri.split(",")[1]))
        await b.close()
asyncio.run(main())
# shrink: 256-colour PNGs look the same and are ~10x smaller
from PIL import Image
for f in (ROOT / "src" / "icons").glob("*.png"):
    Image.open(f).quantize(256, method=Image.Quantize.FASTOCTREE).save(f, "PNG", optimize=True)
