#!/usr/bin/env python3
"""bump_version.py — 一次更新写作技能的版本点

唯一真源：edition/VERSION（专业版），免费版与专业版同号。
一次更新主仓与 edition 版本点；若遗留 public/ worktree 仍存在则顺带改其版本（过渡兼容，非标准出口）：
  - SKILL.md 的 metadata.version
  - 根 _meta.json 的 version
  - public/SKILL.md 的 metadata.version（存在才改；遗留）
  - public/_meta.json 的 version（存在才改；遗留）
  - edition/VERSION
  - edition/meta.paid.json 的 version

用法：
    python3 scripts/bump_version.py 2.0.7
    python3 scripts/bump_version.py --check
    python3 scripts/bump_version.py 2.0.7 --changelog   # 额外插 CHANGELOG 空条目
    python3 scripts/bump_version.py --selftest

退出码：成功/一致 = 0；版本不一致 = 1；参数或写入错误 = 2。
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
META = ROOT / "_meta.json"
EDITION = ROOT / "edition"
VERSION_FILE = EDITION / "VERSION"
PAID_META = EDITION / "meta.paid.json"
PUBLIC = ROOT / "public"
PUBLIC_SKILL = PUBLIC / "SKILL.md"
PUBLIC_META = PUBLIC / "_meta.json"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def read_version():
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def set_skill_version(path, version):
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(r"(?m)^  version: .+$", f"  version: {version}", text, count=1)
    if n != 1:
        raise SystemExit(f"{path} 里找不到 metadata.version")
    path.write_text(new, encoding="utf-8")


def set_meta_version(path, version):
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = version
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_skill_version(path):
    m = re.search(r"(?m)^  version: (.+)$", path.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"{path} 里找不到 metadata.version")
    return m.group(1).strip()


def get_meta_version(path):
    return str(json.loads(path.read_text(encoding="utf-8")).get("version", "")).strip()


def _insert_changelog_stub(path, version):
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if f"## v{version}" in text:
        return False
    stub = f"## v{version}（{datetime.date.today().isoformat()}）\n\n- 待补。\n\n"
    if text.startswith("## v"):
        pos = 0
    else:
        pos = text.find("\n## v")
        pos = pos + 1 if pos != -1 else -1
    if pos == -1:
        text = text.rstrip() + "\n\n" + stub
    elif pos == 0:
        text = stub + text
    else:
        text = text[:pos].rstrip() + "\n\n" + stub + text[pos:]
    path.write_text(text, encoding="utf-8")
    return True


def check(verbose=True):
    """返回问题列表；空表示 6 个版本点一致。"""
    problems = []
    try:
        version = read_version()
    except OSError as e:
        return [f"读不到 edition/VERSION：{e}"]
    points = [
        ("SKILL.md", get_skill_version(SKILL)),
        ("_meta.json", get_meta_version(META)),
        ("edition/meta.paid.json", get_meta_version(PAID_META)),
    ]
    if PUBLIC_SKILL.exists():
        points.append(("public/SKILL.md", get_skill_version(PUBLIC_SKILL)))
    if PUBLIC_META.exists():
        points.append(("public/_meta.json", get_meta_version(PUBLIC_META)))
    for name, value in points:
        if value != version:
            problems.append(f"{name} = {value or '（空）'}，edition/VERSION = {version}")
    if verbose:
        print(f"edition/VERSION = {version}")
        for name, value in points:
            mark = "PASS" if value == version else "FAIL"
            print(f"  [{mark}] {name} = {value or '（空）'}")
        print("版本检查：", "全部一致" if not problems else f"{len(problems)} 处不一致")
    return problems


def bump(version, changelog=False):
    if not VERSION_RE.match(version):
        print(f"版本号格式不对：{version}（示例 2.0.7）", file=sys.stderr)
        return 2
    if not EDITION.is_dir():
        print("缺少 edition/，无法确定专业版版本", file=sys.stderr)
        return 2

    VERSION_FILE.write_text(version + "\n", encoding="utf-8")
    set_skill_version(SKILL, version)
    set_meta_version(META, version)
    set_meta_version(PAID_META, version)
    updated = ["edition/VERSION", "SKILL.md", "_meta.json", "edition/meta.paid.json"]
    if PUBLIC_SKILL.exists():
        set_skill_version(PUBLIC_SKILL, version)
        updated.append("public/SKILL.md")
    if PUBLIC_META.exists():
        set_meta_version(PUBLIC_META, version)
        updated.append("public/_meta.json")
    if changelog:
        if _insert_changelog_stub(ROOT / "CHANGELOG.md", version):
            updated.append("CHANGELOG.md（空条目）")
    print(f"已升到 {version}：")
    for name in updated:
        print(f"  - {name}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="更新写作技能版本点")
    ap.add_argument("version", nargs="?", help="新版本号，如 2.0.7")
    ap.add_argument("--check", action="store_true", help="只检查 6 个版本点是否一致")
    ap.add_argument("--changelog", action="store_true", help="在 CHANGELOG.md 插入空条目")
    ap.add_argument("--selftest", action="store_true", help="检查当前版本点是否一致")
    args = ap.parse_args(argv)

    if args.selftest:
        problems = check()
        print("selftest:", "全部通过" if not problems else "有失败项")
        return 0 if not problems else 1
    if args.check:
        return 0 if not check() else 1
    if not args.version:
        ap.print_help()
        return 2
    return bump(args.version, changelog=args.changelog)


if __name__ == "__main__":
    sys.exit(main())
