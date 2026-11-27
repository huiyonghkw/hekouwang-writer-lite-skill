#!/usr/bin/env python3
"""作者自用发版验收：源码、最终安装包与渠道副本一致才通过。"""

import argparse
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
import zipfile


ROOT = Path(__file__).resolve().parents[1]
COUNT_FILES = (
    "docs/index.html",
    "README.md",
    "DEVELOPMENT.md",
    "SKILL.md",
    "edition/SKILL.paid-section.md",
    "edition/README.paid.md",
    "edition/meta.paid.json",
    "scripts/build_paid_package.py",
    "RELEASE.md",
    "examples/README.md",
    "listing-skillpay.md",
)
BAD_COUNT_WORDS = (
    "三套", "3 套", "三份", "3 份", "五套", "5 套", "五份", "5 份",
    "七套", "7 套", "七份场景", "16 参考", "16 个参考", "16 份参考",
    "18 参考", "18 个参考", "18 份参考", "20 参考", "20 个参考", "20 份参考", "20 个参考文件",
)
EXPECTED_PACKS = {
    "pack-gov-service.md", "pack-project-report.md", "pack-article-longform.md",
    "pack-research-report.md", "pack-execution-plan.md", "pack-tech-docs.md",
    "pack-prd-spec.md", "pack-meeting-notes.md",
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
REQUIRE_CHANNEL = True


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def current_version():
    version_file = ROOT / "edition" / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    return str(json.loads(read("_meta.json"))["version"])


def run(argv, cwd=ROOT):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True)


def pack_files():
    return sorted((ROOT / "edition" / "references").glob("pack-*.md"))


def ref_count():
    return len(list((ROOT / "references").glob("*.md"))) + len(list((ROOT / "edition" / "references").glob("*.md")))


def check_version():
    result = run([sys.executable, "scripts/bump_version.py", "--check"])
    if result.returncode == 0:
        return True, f"{current_version()}（标准布局 4 处一致）"
    return False, (result.stdout + result.stderr).strip().replace("\n", "；")


def check_scripts():
    paths = sorted((ROOT / "scripts").glob("*.py"))
    paths += sorted((ROOT / "edition" / "scripts").glob("*.py"))
    failed = []
    for path in paths:
        result = run([sys.executable, str(path.relative_to(ROOT)), "--selftest"])
        if result.returncode != 0:
            failed.append(f"{path.relative_to(ROOT)}: {result.stdout[-300:]}")
    if failed:
        return False, "；".join(failed)
    return True, f"{len(paths)} 个脚本自检通过（11 个用户脚本 + 3 个作者工具）"


def check_lite_version():
    meta = json.loads(read("_meta.json"))
    version = current_version()
    if str(meta.get("version")) == version and f"  version: {version}" in read("SKILL.md"):
        return True, f"{version}（Lite 两处一致）"
    return False, "SKILL.md 与 _meta.json 的 Lite 版本不一致"


def check_lite_scripts():
    paths = [ROOT / "scripts" / name for name in (
        "doc_lint.py", "sentence_load.py", "rhythm_scan.py", "sawdust_scan.py", "build_lite_package.py",
    )]
    failed = []
    for path in paths:
        result = run([sys.executable, str(path.relative_to(ROOT)), "--selftest"])
        if result.returncode != 0:
            failed.append(path.name)
    if failed:
        return False, "失败：" + ", ".join(failed)
    return True, "Lite 4 个用户脚本与构建工具自检通过"


def check_behavior(lite=False):
    command = [sys.executable, "tools/agent_behavior_check.py", "--selftest"]
    if lite:
        command.append("--lite")
    result = run(command)
    if result.returncode == 0:
        return True, f"{len(json.loads(read('evals/agent-behavior.json'))['cases'])} 个行为用例结构与正负例通过"
    return False, (result.stdout + result.stderr).strip().replace("\n", "；")


def check_behavior_lite():
    return check_behavior(lite=True)


def check_docs():
    result = run([sys.executable, "tools/docs_check.py"])
    if result.returncode == 0:
        return True, "官网结构、资源、无 JS、对比度、脚本语法与实证全部通过"
    return False, (result.stdout + result.stderr).strip().replace("\n", "；")


def check_counts():
    problems = []
    n_packs = len(pack_files())
    n_refs = ref_count()
    if {path.name for path in pack_files()} != EXPECTED_PACKS:
        problems.append("场景包名单与 EXPECTED_PACKS 不一致")
    if n_packs != 8:
        problems.append(f"pack-*.md = {n_packs}（应为 8）")
    if n_refs != 21:
        problems.append(f"参考总数 = {n_refs}（应为 21）")
    hits = []
    for rel in COUNT_FILES:
        path = ROOT / rel
        if not path.is_file():
            hits.append(f"{rel}（缺文件）")
            continue
        text = read(rel)
        if rel == "RELEASE.md":
            match = re.search(r"(?m)^## .*(封版记录|上线)", text)
            if match:
                text = text[:match.start()]
        for word in BAD_COUNT_WORDS:
            if word in text:
                hits.append(f"{rel}:{word}")
    if hits:
        problems.append("残留：" + ", ".join(hits[:20]))
    if problems:
        return False, "；".join(problems)
    return True, "8 套场景包 / 21 参考，当前口径区无旧数量词"


def check_listing():
    match = re.search(r"```text\n(.*?)\n```", read("listing-skillpay.md"), re.S)
    if not match:
        return False, "缺 ```text 成稿块"
    desc = match.group(1)
    chars = len(desc.replace("\n", ""))
    problems = []
    if chars > 500:
        problems.append(f"平台计 {chars}/500 超限")
    n_packs, n_refs = len(pack_files()), ref_count()
    if f"{n_packs} 套场景包" not in desc:
        problems.append(f"缺「{n_packs} 套场景包」")
    if f"{n_refs} 个参考文件" not in desc:
        problems.append(f"缺「{n_refs} 个参考文件」")
    for name in ("办事指南", "项目报告", "长文写作", "调研报告", "执行计划", "技术文档", "PRD 规格书", "会议纪要"):
        if name not in desc:
            problems.append(f"缺场景包名「{name}」")
    if problems:
        return False, "；".join(problems)
    return True, f"能力句与包内一致，平台计 {chars}/500 字"


def check_mapping():
    rel = "edition/references/evidence-and-delivery.md"
    if not (ROOT / rel).is_file():
        return False, f"缺 {rel}"
    text = read(rel)
    required = (
        "supported", "overclaimed", "missing-locator", "contradicted",
        "Strength", "可互转映射", "观察", "推断", "未验证", "A/B/C",
    )
    missing = [word for word in required if word not in text]
    if missing:
        return False, "缺映射要素：" + ", ".join(missing)
    return True, "Verdict/Strength 与证据分级映射要素齐全"


def strip_code(text):
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            in_fence = not in_fence
            lines.append("")
            continue
        lines.append("" if in_fence else line)
    return re.sub(r"`[^`\n]*`", "", "\n".join(lines))


def heading_slug(value):
    value = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`~]", "", value).strip().lower()
    value = unicodedata.normalize("NFKC", value)
    chars = []
    for char in value:
        if char == " ":
            chars.append("-")
        elif char.isalnum() or char in "_-":
            chars.append(char)
    return "".join(chars)


def anchors_for(text):
    anchors = set()
    counts = {}
    for line in strip_code(text).splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = heading_slug(match.group(2))
        index = counts.get(base, 0)
        counts[base] = index + 1
        anchors.add(base if index == 0 else f"{base}-{index}")
    return anchors


def markdown_link_problems(documents, sources=None):
    problems = []
    if sources is None:
        sources = documents
    for name in sorted(sources):
        text = documents[name]
        clean = strip_code(text)
        for raw in LINK_RE.findall(clean):
            target = raw.strip()
            if target.startswith("<") and ">" in target:
                target = target[1:target.index(">")]
            else:
                target = target.split()[0]
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            path_part = unquote(parsed.path)
            anchor = unquote(parsed.fragment)
            if not path_part:
                resolved = name
            else:
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), path_part))
            if resolved.startswith("../") or resolved not in documents:
                problems.append(f"{name}: {raw} -> 缺 {resolved}")
                continue
            if anchor and resolved.endswith(".md") and anchor not in anchors_for(documents[resolved]):
                problems.append(f"{name}: {raw} -> 缺锚点 #{anchor}")
    return problems


def zip_documents(zf):
    docs = {}
    directories = set()
    for name in zf.namelist():
        if name.endswith("/"):
            directories.add(name.rstrip("/"))
            continue
        if name.endswith(".md"):
            docs[name] = zf.read(name).decode("utf-8")
        parent = posixpath.dirname(name)
        while parent:
            directories.add(parent)
            parent = posixpath.dirname(parent)
    for directory in directories:
        docs.setdefault(directory + "/", "")
    for name in zf.namelist():
        if not name.endswith((".md", "/")):
            docs[name] = ""
    return docs


def fingerprint(path):
    with zipfile.ZipFile(path) as zf:
        return {name: hashlib.sha256(zf.read(name)).hexdigest() for name in zf.namelist() if not name.endswith("/")}


def validate_package(path, edition, extract_dir):
    is_paid = edition == "pro"
    arc_root = "hekouwang-writer-skill" if is_paid else "hekouwang-writer-lite-skill"
    expected_scripts = 11 if is_paid else 4
    expected_refs = 21 if is_paid else 8
    expected_name = "hekouwang-writer-skill" if is_paid else "hekouwang-writer-lite-skill"
    expected_license = "Proprietary" if is_paid else "MIT-0"
    problems = []
    with zipfile.ZipFile(path) as zf:
        bad_crc = zf.testzip()
        if bad_crc:
            problems.append(f"CRC 错误: {bad_crc}")
        names = set(zf.namelist())
        meta = json.loads(zf.read(f"{arc_root}/_meta.json").decode("utf-8"))
        skill = zf.read(f"{arc_root}/SKILL.md").decode("utf-8")
        if meta.get("name") != expected_name or f"name: {expected_name}" not in skill:
            problems.append("name 不一致")
        if meta.get("license") != expected_license or f"license: {expected_license}" not in skill:
            problems.append("license 不一致")
        if str(meta.get("version")) != current_version() or f"  version: {current_version()}" not in skill:
            problems.append("version 不一致")
        if len(meta.get("scripts", [])) != expected_scripts or len(meta.get("references", [])) != expected_refs:
            problems.append("_meta 脚本/参考数量不符")
        for key in ("scripts", "references"):
            for rel in meta.get(key, []):
                if f"{arc_root}/{rel}" not in names:
                    problems.append(f"缺 {rel}")
        if f"{arc_root}/DEVELOPMENT.md" in names:
            problems.append("维护文档进入安装包")
        for author_tool in ("build_lite_package.py", "build_paid_package.py", "bump_version.py"):
            if f"{arc_root}/scripts/{author_tool}" in names:
                problems.append(f"作者工具进入安装包: {author_tool}")
        problems.extend(markdown_link_problems(zip_documents(zf)))
        zf.extractall(extract_dir)

    package_root = extract_dir / arc_root
    for script in sorted((package_root / "scripts").glob("*.py")):
        result = run([sys.executable, str(script), "--selftest"], cwd=package_root)
        if result.returncode != 0:
            problems.append(f"包内自检失败 {script.name}: {result.stdout[-200:]}")
    return problems


def check_artifacts(lite_only=False):
    version = current_version()
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    problems = []
    with tempfile.TemporaryDirectory(prefix="release-check-", dir=dist) as tmp:
        tmp = Path(tmp)
        lite = tmp / "lite.zip"
        pro = tmp / "pro.zip"
        builds = [("Lite", [sys.executable, "scripts/build_lite_package.py", "--out", str(lite)])]
        if not lite_only:
            builds.append(("Pro", [sys.executable, "scripts/build_paid_package.py", "--out", str(pro)]))
        for name, command in builds:
            result = run(command)
            if result.returncode != 0:
                problems.append(f"{name} 构建失败: {(result.stdout + result.stderr)[-500:]}")
        if problems:
            return False, "；".join(problems)

        problems.extend(validate_package(lite, "lite", tmp / "lite-src"))
        if not lite_only:
            problems.extend(validate_package(pro, "pro", tmp / "pro-src"))

        lite_second = tmp / "lite-2.zip"
        run([sys.executable, "scripts/build_lite_package.py", "--out", str(lite_second)])
        if lite.read_bytes() != lite_second.read_bytes():
            problems.append("Lite 两次构建哈希不一致")
        if not lite_only:
            pro_second = tmp / "pro-2.zip"
            run([sys.executable, "scripts/build_paid_package.py", "--out", str(pro_second)])
            if pro.read_bytes() != pro_second.read_bytes():
                problems.append("Pro 两次构建哈希不一致")

        if not lite_only and REQUIRE_CHANNEL:
            channels = {
                "Lite": (dist / "clawhub" / f"hekouwang-writer-lite-skill-{version}.zip", lite),
                "Pro": (dist / "skillpay" / f"hekouwang-writer-skill-{version}-paid.zip", pro),
            }
            for name, (published, fresh) in channels.items():
                if not published.is_file():
                    problems.append(f"{name} 渠道副本缺失: {published.relative_to(ROOT)}")
                elif fingerprint(published) != fingerprint(fresh):
                    problems.append(f"{name} 渠道副本与当前源码不一致: {published.relative_to(ROOT)}")

    if problems:
        return False, "；".join(problems[:20])
    if lite_only:
        return True, "Lite 最终包、包内自检、链接与确定性构建全部通过"
    suffix = "与渠道副本" if REQUIRE_CHANNEL else "（CI 模式，不要求既有渠道副本）"
    return True, f"Lite/Pro 最终包、包内自检、链接、确定性构建{suffix}全部通过"


def check_lite_artifacts():
    return check_artifacts(lite_only=True)


def check_source_links():
    sources = ["README.md", "DEVELOPMENT.md", "SKILL.md", "RELEASE.md", "STRUCTURE.md", "AGENTS.md"]
    documents = {}
    excluded = {".git", "dist", ".build", "__pycache__"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or excluded.intersection(path.parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        documents[rel] = path.read_text(encoding="utf-8") if path.suffix == ".md" else ""
    problems = markdown_link_problems(documents, sources=sources)
    if problems:
        return False, "；".join(problems[:20])
    return True, "维护入口与最终包 Markdown 文件链接检查通过"


def check_changelog():
    version = current_version()
    text = read("CHANGELOG.md")
    if f"## v{version}" in text or f"## {version}" in text:
        return True, f"有当前版本 {version} 条目"
    return False, f"缺当前版本 {version} 条目"


CHECKS = (
    ("版本一致性", check_version),
    ("源码脚本自检", check_scripts),
    ("数量词一致性", check_counts),
    ("listing 对齐", check_listing),
    ("分级映射", check_mapping),
    ("CHANGELOG", check_changelog),
    ("行为用例自检", check_behavior),
    ("官网验收", check_docs),
    ("维护文档链接", check_source_links),
    ("最终产物验收", check_artifacts),
)

LITE_CHECKS = (
    ("Lite 版本一致性", check_lite_version),
    ("Lite 源码脚本自检", check_lite_scripts),
    ("Lite 行为用例自检", check_behavior_lite),
    ("官网验收", check_docs),
    ("Lite 最终产物验收", check_lite_artifacts),
)


def print_release_commands():
    version = current_version()
    print("\n=== 人工发布路径（不会自动执行） ===")
    print(f"Lite 渠道包：dist/clawhub/hekouwang-writer-lite-skill-{version}.zip")
    print(f"Pro 渠道包：dist/skillpay/hekouwang-writer-skill-{version}-paid.zip")
    print("ClawHub：发布主仓 Lite 树，必须设置 categories/topics，发布后回读。")
    print("SkillPay：上传上述 Pro zip，商品名与描述以 listing-skillpay.md 为准。")
    print("SkillHub：独立版本线，见 services/skillhub-402/README.md；不要复用写作技能版本。")
    print("推送、上传、提审和真实支付验收均需本人明确确认。")


def main(argv=None):
    global REQUIRE_CHANNEL
    parser = argparse.ArgumentParser(description="发版前验收（作者自用，不进用户包）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="执行 Lite/Pro 全部检查")
    mode.add_argument("--lite", action="store_true", help="公开 Lite 仓 CI 检查，不要求 edition/")
    parser.add_argument("--skip-channel", action="store_true", help="干净 CI 工作区中不要求既有渠道副本")
    args = parser.parse_args(argv)
    if not args.check and not args.lite:
        parser.print_help()
        return 2
    REQUIRE_CHANNEL = not args.skip_channel

    print("=== 发版检查 ===")
    blocked = 0
    for name, fn in (LITE_CHECKS if args.lite else CHECKS):
        try:
            ok, msg = fn()
        except Exception as exc:
            ok, msg = False, f"{type(exc).__name__}: {exc}"
        print(f"[{'PASS' if ok else 'FAIL'}] {name}：{msg}")
        if not ok:
            blocked += 1
    if not args.lite:
        print_release_commands()
    if blocked:
        print(f"\n阻塞项 {blocked} 项未过，不要发版。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
