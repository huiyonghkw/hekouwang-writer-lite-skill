#!/usr/bin/env python3
"""官网结构、资源、实证与基础可访问性验收。"""

from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = DOCS / "index.html"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []
        self.copy_targets = []
        self.json_scripts = []
        self.inline_scripts = []
        self._script = None
        self._script_type = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.refs.append((tag, key, attrs[key]))
        if "data-copy" in attrs:
            self.copy_targets.append(attrs["data-copy"])
        if tag == "script":
            self._script = []
            self._script_type = attrs.get("type", "")

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            content = "".join(self._script)
            if self._script_type == "application/ld+json":
                self.json_scripts.append(content)
            else:
                self.inline_scripts.append(content)
            self._script = None

    def handle_data(self, data):
        if self._script is not None:
            self._script.append(data)


def luminance(value):
    values = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return .2126 * values[0] + .7152 * values[1] + .0722 * values[2]


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + .05) / (low + .05)


def jpeg_size(path):
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        return None
    index = 2
    while index + 9 < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        index += 2
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[index:index + 2], "big")
        if marker in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[index + 5:index + 7], "big"), int.from_bytes(data[index + 3:index + 5], "big")
        index += length
    return None


def parse_page(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def check_structure(pages):
    problems = []
    for path, parser in pages.items():
        if len(parser.ids) != len(set(parser.ids)):
            problems.append(f"{path.name}: 存在重复 id")
        for target in parser.copy_targets:
            if not target.startswith("#") or target[1:] not in parser.ids:
                problems.append(f"{path.name}: 复制目标不存在 {target}")
        for _, _, raw in parser.refs:
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                continue
            rel = unquote(parsed.path)
            target_page = path
            if rel:
                target_page = DOCS / posixpath.normpath(posixpath.join(path.parent.relative_to(DOCS).as_posix(), rel))
            if not target_page.exists():
                problems.append(f"{path.name}: 本地资源不存在 {raw}")
                continue
            if parsed.fragment and target_page.suffix == ".html":
                target_parser = pages.get(target_page)
                if target_parser and parsed.fragment not in target_parser.ids:
                    problems.append(f"{path.name}: 锚点不存在 {raw}")
    return problems


def check_content(html):
    problems = []
    required = (
        ".reveal{opacity:1;transform:none}",
        ".js .reveal{opacity:0",
        "先卸载或禁用 Lite",
        "copy-status",
        "floating-close",
        "floatingCta.inert=!show",
        "examples/checker-demo.json",
        "compatibility.html",
        'rel="canonical"',
        'property="og:image"',
        'rel="preload"',
        "hkw:metric",
    )
    for value in required:
        if value not in html:
            problems.append(f"首页缺少：{value}")
    faint = re.search(r"--faint:(#[0-9a-fA-F]{6})", html)
    if not faint:
        problems.append("找不到首页 --faint")
    else:
        for background in ("#f7f8f7", "#ffffff"):
            if contrast(faint.group(1), background) < 4.5:
                problems.append(f"辅助文字对比度不足：{faint.group(1)} / {background}")
    image = DOCS / "writer-skill-overview.jpg"
    if jpeg_size(image) != (1200, 630):
        problems.append("分享图不是 1200×630 JPEG")
    return problems


def check_case_style():
    page = DOCS / "cases" / "family-pension-case.html"
    css_path = DOCS / "cases" / "family-pension-case.css"
    problems = []
    if "family-pension-case.css" not in page.read_text(encoding="utf-8"):
        problems.append("家庭养老案例未加载专用对齐样式")
    css = css_path.read_text(encoding="utf-8")
    required = (
        "--paper:#f7f8f7", "--accent:#0a7d64", "font-family:var(--font)",
        "font-size:clamp(48px,6.5vw,88px)", "font-weight:900", "border-radius:16px",
    )
    for value in required:
        if value not in css:
            problems.append(f"案例页样式未与首页对齐：{value}")
    return problems


def check_json_ld(parser):
    problems = []
    if not parser.json_scripts:
        return ["首页缺 JSON-LD"]
    for raw in parser.json_scripts:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            problems.append(f"JSON-LD 无法解析: {exc}")
            continue
        types = {item.get("@type") for item in data.get("@graph", [])}
        if "WebSite" not in types or "FAQPage" not in types:
            problems.append("JSON-LD 缺 WebSite 或 FAQPage")
    return problems


def check_javascript(parser):
    if not shutil.which("node"):
        return ["未安装 Node.js，无法检查首页脚本语法"]
    script = "\n".join(parser.inline_scripts)
    result = subprocess.run(["node", "--check"], input=script, capture_output=True, text=True)
    if result.returncode != 0:
        return ["首页脚本语法错误：" + result.stderr.strip()[:300]]
    return []


def check_demo_evidence():
    problems = []
    source = "docs/examples/checker-demo.md"
    expected_path = DOCS / "examples" / "checker-demo.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    commands = {
        "sentence_load": "scripts/sentence_load.py",
        "sawdust_scan": "scripts/sawdust_scan.py",
        "doc_lint": "scripts/doc_lint.py",
    }
    if (ROOT / "edition" / "scripts" / "check_fidelity.py").is_file():
        commands["check_fidelity"] = "edition/scripts/check_fidelity.py"
    for name, script in commands.items():
        result = subprocess.run(
            [sys.executable, script, "--json", source], cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode not in (0, 1):
            problems.append(f"{name} 执行失败: {result.stderr[:200]}")
            continue
        actual = json.loads(result.stdout)
        if actual != expected["outputs"].get(name):
            problems.append(f"{name} 实证输出与示例输入不一致")
    outputs = expected["outputs"]
    if not outputs["check_fidelity"]["errors"]:
        problems.append("实证没有数字错误")
    if not (outputs["sentence_load"]["over"] or outputs["sentence_load"]["warn_items"]):
        problems.append("实证没有长句")
    if not outputs["sawdust_scan"]["over"]:
        problems.append("实证没有锯末词密度告警")
    if not outputs["doc_lint"]["pending_markers"]:
        problems.append("实证没有待核实标记")
    return problems


def main():
    pages = {INDEX: parse_page(INDEX)}
    compatibility = DOCS / "compatibility.html"
    pages[compatibility] = parse_page(compatibility)
    family_case = DOCS / "cases" / "family-pension-case.html"
    pages[family_case] = parse_page(family_case)
    html = INDEX.read_text(encoding="utf-8")
    checks = (
        ("结构与本地资源", check_structure(pages)),
        ("无 JS、对比度与关键内容", check_content(html)),
        ("案例页视觉对齐", check_case_style()),
        ("JSON-LD", check_json_ld(pages[INDEX])),
        ("JavaScript 语法", check_javascript(pages[INDEX])),
        ("真实脚本实证", check_demo_evidence()),
    )
    failed = 0
    for name, problems in checks:
        if problems:
            failed += 1
            print(f"[FAIL] {name}")
            for problem in problems:
                print(f"  {problem}")
        else:
            print(f"[PASS] {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
