#!/usr/bin/env python3
"""release_check.py — 作者自用发版检查（2.1 版本规划第六节）

放根目录 tools/，不在 scripts/；不写进 _meta.json、listing、docs/。
build_paid_package.py 的 PUBLIC_TOP_DIRS / PUBLIC_TOP_FILES 不含 tools/，
因此本脚本物理上不进任何用户包。主仓即公开仓，没有旁路分支。

检查项：版本一致性、脚本自检、数量词一致性、listing 对齐、分级映射、
新包完整性（阻塞）；CHANGELOG、死链（警告）。

用法：python3 tools/release_check.py --check
退出码：阻塞项全过 = 0；有阻塞项不过 = 1；未带 --check = 2。
"""

import argparse
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_VERSION = "2.2.0"  # 本检查工具面向当前写作技能号；发版前 bump_version 到该号

# 4.4 节数量词一致性检查范围；CHANGELOG 历史条目属例外，不在其中。
COUNT_FILES = (
    "docs/index.html",
    "SKILL.md",
    "edition/SKILL.paid-section.md",
    "edition/README.paid.md",
    "edition/meta.paid.json",
    "scripts/build_paid_package.py",
    "RELEASE.md",
    "README.md",
    "examples/README.md",
    "listing-skillpay.md",
)

# 旧数量词残留：勿再写 3/5/7 套或 16/18/20 参考（当前真源为 8 套 / 21 参考）。
BAD_COUNT_WORDS = (
    "三套", "3 套", "三份", "3 份", "五套", "5 套", "五份", "5 份",
    "七套", "7 套", "七份场景",
    "16 参考", "16 个参考", "16 份参考", "18 参考", "18 个参考", "18 份参考",
    "20 参考", "20 个参考", "20 份参考", "20 个参考文件",
)

# 规划的 8 套场景包名单。
KNOWN_PACKS = (
    "pack-gov-service.md",
    "pack-project-report.md",
    "pack-article-longform.md",
    "pack-research-report.md",
    "pack-execution-plan.md",
    "pack-tech-docs.md",
    "pack-prd-spec.md",
    "pack-meeting-notes.md",
)

# 作者工具，不计入 11 个用户向脚本。
AUTHOR_SCRIPTS = {"scripts/build_paid_package.py", "scripts/bump_version.py"}

RELEASE_COMMANDS = """
# 0. 提交主仓并打 tag（主仓即公开仓：origin/main 免费版，Pages 吃主仓 docs/）
git add -A && git commit -m "release: {version}"
git tag v{version} && git push origin main && git push origin v{version}

# 1. 免费版 → ClawHub（必须带 Catalog metadata，2.0.6 踩过坑）
clawhub skill publish --public --categories creative,productivity --topics "中文写作,文档质检,去AI味,写作规范"

# 2. 专业版 → SkillPay（手工上传）
打开 https://pay.alipay.com/skillpay/upload
上传：dist/release-{version}/hekouwang-writer-skill-{version}-paid.zip
上传后清空商品名与商品描述字段，重贴 listing-skillpay.md 成稿；记录 SHA256

# 3. GitHub Release（notes 用 CHANGELOG {version} 章节，别整份塞）
gh release create v{version} --notes-file <{version} 章节摘出>

# 4. SkillHub 按次体检：2.1 不涉及，独立版本线不动

# 5. Pages：主仓 docs/ 已随第 0 步的 origin/main 推送，无需单独 worktree 操作
"""


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def run(argv):
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)


def pack_files():
    return sorted(glob.glob(os.path.join(ROOT, "edition", "references", "pack-*.md")))


def ref_count():
    root_refs = glob.glob(os.path.join(ROOT, "references", "*.md"))
    paid_refs = glob.glob(os.path.join(ROOT, "edition", "references", "*.md"))
    return len(root_refs) + len(paid_refs)


def check_version():
    r = run([sys.executable, "scripts/bump_version.py", "--check"])
    version = read("edition/VERSION").strip()
    if r.returncode == 0:
        return True, f"{version}（bump_version --check，4 处一致）"
    detail = (r.stdout + r.stderr).strip().replace("\n", "；")
    return False, f"{version} 版本点不一致：{detail}"


def check_scripts():
    paths = sorted(glob.glob(os.path.join(ROOT, "scripts", "*.py")))
    paths += sorted(glob.glob(os.path.join(ROOT, "edition", "scripts", "*.py")))
    user = [p for p in paths if os.path.relpath(p, ROOT) not in AUTHOR_SCRIPTS]
    failed = []
    for path in user:
        rel = os.path.relpath(path, ROOT)
        if run([sys.executable, rel, "--selftest"]).returncode != 0:
            failed.append(rel)
    if failed:
        return False, f"{len(user)} 个用户向脚本，失败：{', '.join(failed)}"
    return True, f"{len(user)} 个用户向脚本全部通过"


def check_counts():
    problems = []
    n_packs = len(pack_files())
    n_refs = ref_count()
    if n_packs != 8:
        problems.append(f"pack-*.md = {n_packs}（应为 8）")
    if n_refs != 21:
        problems.append(f"参考总数 = {n_refs}（应为 21）")
    hits = []
    for rel in COUNT_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            hits.append(f"{rel}（缺文件）")
            continue
        text = read(rel)
        if rel == "RELEASE.md":
            # 「封版记录」「上线」节（第七节起）是历史快照，保留当时数量词，只查当前口径区。
            m = re.search(r"(?m)^## .*(封版记录|上线)", text)
            if m:
                text = text[:m.start()]
        for word in BAD_COUNT_WORDS:
            if word in text:
                hits.append(f"{rel}:{word}")
    if hits:
        problems.append("残留：" + ", ".join(hits[:20]))
    if problems:
        return False, "；".join(problems)
    words = " / ".join(BAD_COUNT_WORDS)
    return True, f"8 套场景包 / 21 参考，无「{words}」残留"


def check_listing():
    m = re.search(r"```text\n(.*?)\n```", read("listing-skillpay.md"), re.S)
    if not m:
        return False, "缺 ```text 成稿块"
    desc = m.group(1)
    chars = len(desc.replace("\n", ""))
    problems = []
    if chars > 500:
        problems.append(f"平台计 {chars}/500 超限")
    n_packs, n_refs = len(pack_files()), ref_count()
    if f"{n_packs} 套场景包" not in desc:
        problems.append(f"能力句缺「{n_packs} 套场景包」")
    if f"{n_refs} 个参考文件" not in desc:
        problems.append(f"能力句缺「{n_refs} 个参考文件」")
    for name in ("办事指南", "项目报告", "长文写作", "调研报告", "执行计划", "技术文档", "PRD 规格书", "会议纪要"):
        if name not in desc:
            problems.append(f"缺场景包名「{name}」")
    if problems:
        return False, "；".join(problems)
    return True, f"能力句与包内一致，平台计 {chars}/500 字"


def check_mapping():
    rel = "edition/references/evidence-and-delivery.md"
    if not os.path.isfile(os.path.join(ROOT, rel)):
        return False, f"缺 {rel}"
    text = read(rel)
    required = (
        "supported", "overclaimed", "missing-locator", "contradicted",
        "Strength", "可互转映射", "观察", "推断", "未验证", "A/B/C",
    )
    missing = [w for w in required if w not in text]
    if missing:
        return False, "缺映射要素：" + ", ".join(missing)
    return True, "证据对账表 Verdict/Strength ↔ 证据三分 A/B/C 已互转"


def check_packs():
    packs = sorted(os.path.basename(p) for p in pack_files())
    problems = [f"缺 {name}" for name in KNOWN_PACKS if name not in packs]
    build_src = read("scripts/build_paid_package.py")
    dirs = re.search(r"PUBLIC_TOP_DIRS\s*=\s*\((.*?)\)", build_src, re.S)
    files = re.search(r"PUBLIC_TOP_FILES\s*=\s*\((.*?)\)", build_src, re.S)
    whitelist = (dirs.group(1) if dirs else "") + (files.group(1) if files else "")
    if "references" not in whitelist:
        problems.append("构建白名单缺 references")
    if "tools" in whitelist:
        problems.append("tools 进了构建白名单（作者工具不得进用户包）")
    if "copy_paid_assets" not in build_src or "set_meta" not in build_src:
        problems.append("构建脚本不再把 edition/references 并入包内 _meta")
    if problems:
        return False, "；".join(problems)
    return True, f"{len(packs)} 个 pack 均在 _meta 清单与构建白名单中"


def check_changelog():
    text = read("CHANGELOG.md")
    if f"## v{TARGET_VERSION}" in text or f"## {TARGET_VERSION}" in text:
        return True, f"有 {TARGET_VERSION} 条目"
    return False, f"缺 {TARGET_VERSION} 条目"


def check_deadlinks():
    targets = ["SKILL.md"]
    targets += [os.path.relpath(p, ROOT) for p in sorted(glob.glob(os.path.join(ROOT, "references", "*.md")))]
    r = run([sys.executable, "scripts/doc_lint.py"] + targets)
    if r.returncode == 0:
        return True, "doc_lint.py 结构体检通过"
    lines = (r.stdout + r.stderr).strip().splitlines()
    return False, "doc_lint.py 报硬错误：" + "；".join(lines[:5])


CHECKS = (
    ("版本一致性", check_version, False),
    ("脚本自检", check_scripts, False),
    ("数量词一致性", check_counts, False),
    ("listing 对齐", check_listing, False),
    ("分级映射", check_mapping, False),
    ("新包完整性", check_packs, False),
    ("CHANGELOG", check_changelog, True),
    ("死链", check_deadlinks, True),
)


def main(argv=None):
    ap = argparse.ArgumentParser(description="发版前检查（作者自用，不进用户包）")
    ap.add_argument("--check", action="store_true", help="执行全部检查")
    args = ap.parse_args(argv)
    if not args.check:
        ap.print_help()
        return 2

    print("=== 发版检查 ===")
    blocked = 0
    for name, fn, warn_only in CHECKS:
        ok, msg = fn()
        mark = "✅" if ok else "⚠️"
        suffix = "" if warn_only or ok else "（阻塞）"
        print(f"{mark} {name}：{msg}{suffix}")
        if not ok and not warn_only:
            blocked += 1

    current = read("edition/VERSION").strip()
    print("\n=== 分渠道发布命令 ===")
    print(f"# 目标版本 {TARGET_VERSION}；当前 edition/VERSION = {current}，发版前先 bump_version")
    print(RELEASE_COMMANDS.format(version=TARGET_VERSION), end="")
    if blocked:
        print(f"\n阻塞项 {blocked} 项未过，不要发版。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
