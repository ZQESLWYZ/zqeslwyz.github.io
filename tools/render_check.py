"""Render-level verification of the jemdoc-style homepage through CDP.

Asserts what static analysis cannot:
  * style.css applied (page/card colours, Georgia serif, heading rules)
  * desktop two-column header, mobile single-column collapse
  * no horizontal overflow at 1180px and 390px
  * portrait either loads from assets/photo.jpg or degrades to the placeholder
  * publication list has all 6 entries and no placeholder left
  * no console errors or uncaught exceptions

Run:  conda run -n deeplearn python tools/render_check.py <site-dir>
"""
import base64
import io
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

import websocket
from PIL import Image, ImageStat

SITE = sys.argv[1]
PORT = 9333
SCRATCH = os.environ.get("PI_SCRATCH_DIR", os.getcwd())
PROFILE = os.path.join(SCRATCH, "edge-profile")

EDGE = next(
    (p for p in (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ) if os.path.exists(p)),
    None,
)

failures = []
notes = []


class CDP:
    def __init__(self, url):
        self.ws = websocket.create_connection(url, timeout=30)
        self.next_id = 0
        self.events = []

    def send(self, method, **params):
        self.next_id += 1
        mid = self.next_id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method} -> {msg['error']}")
                return msg.get("result", {})
            self.events.append(msg)

    def eval(self, expression):
        res = self.send("Runtime.evaluate", expression=expression,
                        returnByValue=True, awaitPromise=True)
        if res.get("exceptionDetails"):
            raise RuntimeError(f"JS exception: {res['exceptionDetails'].get('text')} :: {expression}")
        return res.get("result", {}).get("value")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def brightness(png_bytes):
    image = Image.open(io.BytesIO(png_bytes)).convert("L")
    return ImageStat.Stat(image).mean[0], image.size


OVERFLOW = """
(() => {
  const vw = document.documentElement.clientWidth;
  const bad = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    if (r.right > vw + 1.5) bad.push(el.tagName.toLowerCase() + '.' + (el.className || '').toString().split(' ')[0]);
  });
  const over = document.documentElement.scrollWidth > vw + 1 || document.body.scrollWidth > vw + 1;
  return JSON.stringify({vw, over, docScrollW: document.documentElement.scrollWidth, bad: bad.slice(0, 5)});
})()
"""

LAYOUT = """
(() => {
  const id = document.querySelector('.identity').getBoundingClientRect();
  const ct = document.querySelector('.content').getBoundingClientRect();
  return JSON.stringify({idTop: id.top, idRight: id.right, idBottom: id.bottom, idLeft: id.left,
                         ctTop: ct.top, ctLeft: ct.left, ctRight: ct.right});
})()
"""


def main():
    if not EDGE:
        print("no Chromium browser found"); sys.exit(2)
    shutil.rmtree(PROFILE, ignore_errors=True)
    proc = subprocess.Popen([
        EDGE, "--headless=new", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--disable-extensions",
        f"--remote-debugging-port={PORT}", f"--user-data-dir={PROFILE}",
        "--window-size=1180,900",
        "file:///" + os.path.join(SITE, "index.html").replace("\\", "/"),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    target = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=2) as resp:
                pages = json.load(resp)
            target = next((p for p in pages if p.get("type") == "page"), None)
            if target and target.get("webSocketDebuggerUrl"):
                break
        except Exception:
            pass
        time.sleep(0.5)
    if not target:
        proc.kill(); print("could not attach to a page target"); sys.exit(2)

    cdp = CDP(target["webSocketDebuggerUrl"])
    cdp.send("Runtime.enable"); cdp.send("Log.enable"); cdp.send("Page.enable")
    time.sleep(1.5)

    # ------------------------------------------------------------ css applied
    checks = [
        ("page background grey", "getComputedStyle(document.documentElement).backgroundColor", "rgb(238, 238, 238)"),
        ("card max-width 960px", "getComputedStyle(document.body).maxWidth", "960px"),
        ("h2 grey underline", "getComputedStyle(document.querySelector('h2')).borderBottomWidth", "1px"),
        ("link colour", "getComputedStyle(document.querySelector('.links a')).color", "rgb(34, 75, 141)"),
        ("footer is grey+small", "getComputedStyle(document.querySelector('.footer')).borderTopWidth", "1px"),
    ]
    for label, expr, expected in checks:
        actual = cdp.eval(expr)
        if actual == expected:
            notes.append(f"css: {label} -> {actual}")
        else:
            failures.append(f"css: {label} expected {expected}, got {actual}")

    font = cdp.eval("getComputedStyle(document.body).fontFamily")
    if "Georgia" in (font or ""):
        notes.append(f"css: serif font stack active ({font.split(',')[0]})")
    else:
        failures.append(f"css: expected Georgia first in font stack, got {font}")

    # ------------------------------------------------------- portrait + data
    img_ok = cdp.eval("""(() => { const el = document.getElementById('portrait');
        return !!el && el.complete && el.naturalWidth > 0; })()""")
    fb_box = cdp.eval("""(() => { const el = document.querySelector('.portrait-fallback');
        if (!el) return 'none'; const r = el.getBoundingClientRect();
        return Math.round(r.width) + 'x' + Math.round(r.height); })()""")
    if img_ok:
        notes.append("portrait image loads from assets/photo.jpg")
    elif fb_box not in ("none", "0x0"):
        notes.append(f"portrait falls back to the initials placeholder ({fb_box})")
    else:
        failures.append(f"portrait is broken: loaded={img_ok} fallback={fb_box}")

    pubs = cdp.eval("document.querySelectorAll('ul.pubs > li').length")
    todos = cdp.eval("document.querySelectorAll('li.todo').length")
    if pubs == 6 and todos == 0:
        notes.append(f"publication data complete: {pubs} entries, no placeholder left")
    else:
        failures.append(f"publication list incomplete: {pubs} entries (expected 6), {todos} TODO placeholder(s)")

    link_rows = cdp.eval("document.querySelectorAll('ul.pubs > li > .pub-links').length")
    link_real = cdp.eval("""document.querySelectorAll('.pub-links a[href^="http"]').length""")
    link_pending = cdp.eval("document.querySelectorAll('.pub-links .link-pending').length")
    if link_rows == 6:
        notes.append(f"[Paper]/[Code] row on all {link_rows} entries "
                     f"({link_real} real links, {link_pending} still pending)")
    else:
        failures.append(f"expected a .pub-links row on all 6 entries, found {link_rows}")

    # ------------------------------------------------------ desktop layout
    probe = json.loads(cdp.eval(OVERFLOW))
    if probe["bad"] or probe["over"]:
        failures.append(f"desktop 1180px: overflow -> {probe['bad']} scrollOverflow={probe['over']}")
    else:
        notes.append(f"desktop 1180px: no horizontal overflow (docScrollW={probe['docScrollW']}, vw={probe['vw']})")

    lay = json.loads(cdp.eval(LAYOUT))
    if lay["idRight"] <= lay["ctLeft"] + 1 and abs(lay["idTop"] - lay["ctTop"]) < 60:
        notes.append(f"desktop layout: two columns side by side "
                     f"(identity right={round(lay['idRight'])}, content left={round(lay['ctLeft'])})")
    else:
        failures.append(f"desktop layout: expected two columns, got identity right={round(lay['idRight'])}, "
                        f"content left={round(lay['ctLeft'])}, content top={round(lay['ctTop'])}")

    shot = base64.b64decode(cdp.send("Page.captureScreenshot", format="png")["data"])
    mean, size = brightness(shot)
    notes.append(f"desktop screenshot {size[0]}x{size[1]}, mean brightness {mean:.1f}")
    if mean < 200:
        failures.append(f"page looks too dark for a white card layout (mean brightness {mean:.1f})")

    # ------------------------------------------------------- mobile layout
    cdp.send("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    time.sleep(1.0)

    probe_m = json.loads(cdp.eval(OVERFLOW))
    if probe_m["bad"] or probe_m["over"]:
        failures.append(f"mobile 390px: overflow -> {probe_m['bad']} scrollOverflow={probe_m['over']}")
    else:
        notes.append(f"mobile 390px: no horizontal overflow (docScrollW={probe_m['docScrollW']}, vw={probe_m['vw']})")

    lay_m = json.loads(cdp.eval(LAYOUT))
    if lay_m["ctTop"] >= lay_m["idBottom"] - 1:
        notes.append(f"mobile layout: single column (identity bottom={round(lay_m['idBottom'])}, "
                     f"content top={round(lay_m['ctTop'])})")
    else:
        failures.append(f"mobile layout: expected stacking, got identity bottom={round(lay_m['idBottom'])}, "
                        f"content top={round(lay_m['ctTop'])}")

    # --------------------------------------------------------------- console
    time.sleep(0.5)
    errors = []
    tolerated = []
    for event in cdp.events:
        if event.get("method") == "Runtime.exceptionThrown":
            errors.append(event["params"]["exceptionDetails"].get("text", "exception"))
        elif event.get("method") == "Log.entryAdded":
            entry = event["params"]["entry"]
            if entry.get("level") in ("error", "warning"):
                text = entry.get("text", "")
                url = entry.get("url", "")
                # assets/photo.jpg is not uploaded yet (see README section 4):
                # its 404 is expected and already reported as a static warning.
                if "photo.jpg" in url or "photo.jpg" in text:
                    tolerated.append(f"{entry['level']}: {text[:120]}")
                    continue
                errors.append(f"{entry['level']}: {text[:140]} (url={url[:80]})")
    if errors:
        failures.append("console problems -> " + " | ".join(errors[:5]))
    else:
        notes.append("no console errors or uncaught exceptions"
                     + (f" (tolerated: {tolerated[0]})" if tolerated else ""))

    cdp.close()
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
    shutil.rmtree(PROFILE, ignore_errors=True)

    print("--- notes ---")
    for note in notes:
        print("  ", note)
    print("--- failures ---")
    if failures:
        for item in failures:
            print("  !!", item)
        sys.exit(1)
    print("   none")


if __name__ == "__main__":
    main()
