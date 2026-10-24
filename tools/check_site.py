"""Static checks for the GitHub Pages personal site.

1. HTML tag balance (html.parser based, void-element aware)
2. Local asset references resolve to real files
3. CSS brace balance / unterminated comments
4. JS syntax via `node --check` when node is available
"""
import os
import sys
from html.parser import HTMLParser

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

failures = []
notes = []


class Balance(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        pass  # self-closing, nothing to track

    def handle_endtag(self, tag):
        if tag in VOID:
            self.errors.append(f"line {self.getpos()[0]}: stray closing </{tag}>")
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: </{tag}> with nothing open")
            return
        open_tag, open_line = self.stack.pop()
        if open_tag != tag:
            self.errors.append(
                f"line {self.getpos()[0]}: </{tag}> closes <{open_tag}> opened at line {open_line}"
            )

    def report(self):
        for tag, line in self.stack:
            self.errors.append(f"unclosed <{tag}> opened at line {line}")
        return self.errors


class Refs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("src", "href") and value:
                self.refs.append(value)


PENDING = set()   # nothing pending: assets/photo.jpg is in place
warnings = []


def check_html(path):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()

    parser = Balance(path)
    parser.feed(text)
    parser.close()
    errors = parser.report()
    if errors:
        failures.append(f"{os.path.basename(path)}: " + "; ".join(errors))
    else:
        notes.append(f"{os.path.basename(path)}: tags balanced")

    refs = Refs()
    refs.feed(text)
    checked = 0
    seen = set()
    for ref in refs.refs:
        if ref.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
            continue
        target = ref.split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        if target in seen:
            continue
        seen.add(target)

        if target.startswith("/"):
            # absolute path -> resolve against the site root
            resolved = os.path.join(ROOT, target.lstrip("/"))
        else:
            resolved = os.path.join(os.path.dirname(path), target)

        rel = os.path.relpath(resolved, ROOT).replace("\\", "/")
        checked += 1
        if os.path.exists(resolved):
            continue
        if rel in PENDING:
            warnings.append(
                f"{os.path.basename(path)}: {rel} not uploaded yet (see README section 4)"
            )
        else:
            failures.append(f"{os.path.basename(path)}: missing local reference {ref}")
    notes.append(f"{os.path.basename(path)}: {checked} local references checked")


def check_css(path):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    stripped = []
    i, n = 0, len(text)
    while i < n:
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end == -1:
                failures.append(f"{os.path.basename(path)}: unterminated /* comment")
                return
            i = end + 2
            continue
        stripped.append(text[i])
        i += 1
    body = "".join(stripped)
    depth = body.count("{") - body.count("}")
    if depth != 0:
        failures.append(f"{os.path.basename(path)}: unbalanced braces ({{}} delta = {depth})")
    else:
        notes.append(f"{os.path.basename(path)}: braces balanced ({body.count('{')} blocks)")


def check_js(path):
    import shutil
    import subprocess

    node = shutil.which("node")
    if not node:
        notes.append("js/main.js: node not found, syntax check skipped")
        return
    result = subprocess.run([node, "--check", path], capture_output=True, text=True)
    if result.returncode != 0:
        failures.append(f"js/main.js: node --check failed\n{result.stderr.strip()}")
    else:
        notes.append("js/main.js: syntax OK (node --check)")


if __name__ == "__main__":
    for name in ("index.html", "404.html"):
        check_html(os.path.join(ROOT, name))
    check_css(os.path.join(ROOT, "css", "style.css"))
    check_js(os.path.join(ROOT, "js", "main.js"))

    print("--- notes ---")
    for note in notes:
        print("  ", note)
    if warnings:
        print("--- warnings ---")
        for item in warnings:
            print("  ~~", item)
    print("--- failures ---")
    if failures:
        for item in failures:
            print("  !!", item)
        sys.exit(1)
    print("   none")
