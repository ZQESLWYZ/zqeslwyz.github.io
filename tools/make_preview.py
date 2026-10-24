"""Render full-page screenshots of the site (desktop + mobile) via CDP.

Usage: conda run -n deeplearn python tools_shot.py <site-dir> <out-dir>
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

import websocket

SITE = sys.argv[1]
OUT = sys.argv[2]
PORT = 9344
SCRATCH = os.environ.get("PI_SCRATCH_DIR", os.getcwd())
PROFILE = os.path.join(SCRATCH, "edge-shot-profile")

EDGE = next(
    (p for p in (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ) if os.path.exists(p)),
    None,
)


def call(ws, mid, method, **params):
    ws.send(json.dumps({"id": mid, "method": method, "params": params}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == mid:
            return msg.get("result", {})


def shoot(ws, mid, name, width, height, dsf, dark=False):
    call(ws, mid, "Emulation.setDeviceMetricsOverride",
         width=width, height=height, deviceScaleFactor=dsf, mobile=dsf > 1)
    mid += 1
    if dark:
        call(ws, mid, "Runtime.evaluate", expression="document.documentElement.setAttribute('data-theme','dark')")
        mid += 1
    time.sleep(1.0)
    metrics = call(ws, mid, "Page.getLayoutMetrics")
    mid += 1
    content = metrics.get("cssContentSize") or metrics["contentSize"]
    full_h = int(content["height"]) + 20
    result = call(
        ws, mid, "Page.captureScreenshot",
        format="png", captureBeyondViewport=True,
        clip={"x": 0, "y": 0, "width": width, "height": full_h, "scale": 1},
    )
    mid += 1
    # reset theme
    call(ws, mid, "Runtime.evaluate", expression="document.documentElement.setAttribute('data-theme','light')")
    mid += 1
    path = os.path.join(OUT, name)
    with open(path, "wb") as handle:
        handle.write(base64.b64decode(result["data"]))
    print(f"  {name}  {width}x{full_h}  {os.path.getsize(path)} bytes")
    return mid


def main():
    if not EDGE:
        print("no browser found"); sys.exit(2)
    os.makedirs(OUT, exist_ok=True)
    shutil.rmtree(PROFILE, ignore_errors=True)

    proc = subprocess.Popen([
        EDGE, "--headless=new", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--hide-scrollbars",
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
        proc.kill(); print("attach failed"); sys.exit(2)

    ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=60)
    mid = 1
    call(ws, mid, "Runtime.enable"); mid += 1
    call(ws, mid, "Page.enable"); mid += 1
    time.sleep(1.5)

    mid = shoot(ws, mid, "preview-desktop.png", 1180, 900, 1, dark=False)
    mid = shoot(ws, mid, "preview-mobile.png", 390, 844, 2, dark=False)

    ws.close()
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
    shutil.rmtree(PROFILE, ignore_errors=True)


if __name__ == "__main__":
    main()
