#!/usr/bin/env python3
"""build_paid_package.py — 组装专业版安装包

把主仓库的免费内容与 edition/ 里的付费资产合并成一份 zip：
  - 主仓库只拷白名单：5 个根文件 + _meta.json 列出的 scripts/references + examples/
  - edition/scripts/*.py   → scripts/
  - edition/references/*.md → references/
  - edition/examples/*     → examples/（若目录存在）
  - SKILL.paid-section.md 插到 SKILL.md 的「## 八、边界」之前
  - meta.paid.json 的 headerNote 替换「本版」行，name/description/homepage/handoff 覆盖
  - SKILL.md 与 _meta.json 的版本号改成付费版号
  - _meta.json 的 scripts / references 列表补上付费资产

不用 .clawhubignore：那份清单服务平台发布，这里是白名单，新增本地目录不会溜进包。
构建末尾 verify_package() 对账包内文件与 _meta.json，并对全文扫残留措辞。

用法：
    python3 scripts/build_paid_package.py           # 默认读 edition/VERSION，输出 dist/<version>/
    python3 scripts/build_paid_package.py --version <version>
    python3 scripts/build_paid_package.py --out /tmp/x.zip

退出码：成功 = 0；前置缺失 = 2；包内自检不过 = 1。
"""

import argparse
import json
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EDITION = os.path.join(ROOT, "edition")
EDITION_README = os.path.join(EDITION, "README.paid.md")
EDITION_LICENSE = os.path.join(EDITION, "LICENSE.paid")
ANCHOR = "## 七、边界与付费版"

# 白名单：只拷这些根文件与目录。新增的本地目录（.qwen/.claude/.gstack 等）自动不进包。
PUBLIC_TOP_FILES = ("SKILL.md", "_meta.json", "README.md", "LICENSE", "CHANGELOG.md")
PUBLIC_TOP_DIRS = ("scripts", "references", "examples")

# 付费包不该出现的措辞：免费版残留、包外权威、内部渠道名。
PAID_BANNED_PHRASES = (
    "见第八节",
    "SKILL.md 1.2 节",
    "AGENTS 一票否决",
    "AGENTS 红线",
    "订阅版",
    "公开的 `references/article-writing.md`",
    "公开仓库 `examples/",
)


def read_public_meta():
    with open(os.path.join(ROOT, "_meta.json"), encoding="utf-8") as fh:
        return json.load(fh)


def copy_public(dest):
    """按白名单拷免费内容：根文件 + _meta.json 清单 + examples 整目录。"""
    meta = read_public_meta()
    copied = 0
    for name in PUBLIC_TOP_FILES:
        src = os.path.join(ROOT, name)
        if not os.path.isfile(src):
            raise SystemExit(f"白名单文件缺失：{name}")
        shutil.copy2(src, os.path.join(dest, name))
        copied += 1

    listed = list(meta.get("scripts", [])) + list(meta.get("references", []))
    for rel in listed:
        src = os.path.join(ROOT, rel)
        if not os.path.isfile(src):
            raise SystemExit(f"_meta.json 列出的文件不存在：{rel}")
        target = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copy2(src, target)
        copied += 1

    examples = os.path.join(ROOT, "examples")
    for base, dirs, files in os.walk(examples):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in sorted(files):
            if name.startswith("."):
                continue
            src = os.path.join(base, name)
            rel = os.path.relpath(src, ROOT)
            target = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(src, target)
            copied += 1
    return copied


def copy_paid_assets(dest):
    added = []
    for sub, target_sub in (
        ("scripts", "scripts"),
        ("references", "references"),
        ("examples", "examples"),
    ):
        src_dir = os.path.join(EDITION, sub)
        if not os.path.isdir(src_dir):
            continue
        out_dir = os.path.join(dest, target_sub)
        os.makedirs(out_dir, exist_ok=True)
        for name in sorted(os.listdir(src_dir)):
            if name.startswith(".") or name == "__pycache__":
                continue
            src = os.path.join(src_dir, name)
            if not os.path.isfile(src):
                continue
            dest_path = os.path.join(out_dir, name)
            # 付费示例索引只作增补，合并进免费案例总索引；不单独成文件
            if target_sub == "examples" and name == "PAID-EXAMPLES.md":
                dest_readme = os.path.join(dest, "examples", "README.md")
                with open(src, encoding="utf-8") as fh:
                    frag = fh.read().strip()
                mode = "a" if os.path.exists(dest_readme) else "w"
                with open(dest_readme, mode, encoding="utf-8") as fh:
                    if mode == "a":
                        fh.write("\n\n---\n\n")
                    fh.write(frag)
                    fh.write("\n")
                continue
            shutil.copy2(src, dest_path)
            added.append(f"{target_sub}/{name}")
    return added


def inject_section(skill_path):
    with open(os.path.join(EDITION, "SKILL.paid-section.md"), encoding="utf-8") as fh:
        section = fh.read().strip()
    with open(skill_path, encoding="utf-8") as fh:
        text = fh.read()
    if ANCHOR not in text:
        raise SystemExit(f"SKILL.md 里找不到锚点「{ANCHOR}」，注入位置无法确定")
    if "付费版扩展" in text:
        return False
    text = text.replace(ANCHOR, section + "\n\n---\n\n" + ANCHOR, 1)
    with open(skill_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return True


def set_skill_version(skill_path, version):
    with open(skill_path, encoding="utf-8") as fh:
        text = fh.read()
    new, n = re.subn(r"(?m)^  version: .+$", f"  version: {version}", text, count=1)
    new, n_license = re.subn(r"(?m)^license: .+$", "license: Proprietary", new, count=1)
    if n != 1 or n_license != 1:
        raise SystemExit("SKILL.md 里没找到 metadata.version 或 license 行")
    with open(skill_path, "w", encoding="utf-8") as fh:
        fh.write(new)


def _meta_list_key(item):
    if item.startswith("scripts/"):
        return "scripts"
    if item.startswith("references/"):
        return "references"
    if item.startswith("examples/"):
        return "examples"
    return None


def set_meta(meta_path, version, added):
    with open(meta_path, encoding="utf-8") as fh:
        meta = json.load(fh)
    meta["version"] = version
    meta["license"] = "Proprietary"
    for item in added:
        key = _meta_list_key(item)
        if not key:
            continue
        if item not in meta.get(key, []):
            meta.setdefault(key, []).append(item)

    # examples 没有手工清单，按构建后的实际文件写全，_meta.json 才能与包内对账。
    examples_dir = os.path.join(os.path.dirname(meta_path), "examples")
    if os.path.isdir(examples_dir):
        meta["examples"] = [
            f"examples/{n}" for n in sorted(os.listdir(examples_dir)) if n.endswith(".md")
        ]

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def add_edition_note(dest, version, added):
    path = os.path.join(dest, "PAID-EDITION.md")
    lines = [
        f"# 专业版说明（v{version}）",
        "",
        f"本包是 {version} 专业版，包含完整 SKILL.md、11 个脚本、16 个参考文件（8 个通用参考加 8 个进阶参考，其中 3 份是场景包）。",
        "免费版是另一个名字 hekouwang-writer-lite-skill，两者不要同时安装。",
        "",
        "## 增量文件",
        "",
    ]
    lines += [f"- `{item}`" for item in added]
    lines += ["", "## 版本", "", f"- 本包版本：{version}", "- 许可：Proprietary", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def strip_lite_blocks(text):
    """删掉只对免费版成立的段落。段落用 <!-- lite-only --> 包住。"""
    return re.sub(r"<!-- lite-only -->.*?<!-- /lite-only -->\n?", "", text, flags=re.S)


def _format_handoff_block(raw):
    """把 meta.paid.json 的 handoff 字符串写成 YAML 块标量（有则覆盖用）。"""
    body = raw.strip("\n")
    if body.startswith("|"):
        body = body[1:]
        if body.startswith("\n"):
            body = body[1:]
    lines = []
    for line in body.splitlines():
        if not line.strip():
            lines.append("")
        elif line.startswith("    "):
            lines.append(line)
        else:
            lines.append("    " + line.lstrip())
    return "  handoff: |\n" + "\n".join(lines) + "\n"


def apply_paid_meta(dest):
    """把免费版的名称、描述换成付费版，并删掉只对免费版成立的段落。

    meta.paid.json 的 headerNote 替换「本版」行；homepage / handoff 有则覆盖；
    缺 headerNote 直接报错，避免免费版措辞漏进付费包。
    """
    meta_src = os.path.join(EDITION, "meta.paid.json")
    if not os.path.exists(meta_src):
        raise SystemExit("缺少 edition/meta.paid.json")
    with open(meta_src, encoding="utf-8") as fh:
        paid = json.load(fh)

    header_note = (paid.get("headerNote") or "").strip()
    if not header_note:
        raise SystemExit("edition/meta.paid.json 缺少 headerNote，付费版头部无法改写")

    skill_path = os.path.join(dest, "SKILL.md")
    with open(skill_path, encoding="utf-8") as fh:
        text = fh.read()
    text = strip_lite_blocks(text)
    text = text.replace("## 七、边界与付费版", "## 七、边界", 1)

    text, n_note = re.subn(r"(?m)^> \*\*本版\*\*：.*$", lambda m: header_note, text, count=1)
    if n_note != 1:
        raise SystemExit("SKILL.md 里找不到「> **本版**：」行，头部无法改写")

    for key in ("name", "description"):
        pattern = rf"(?m)^{key}: .*$"
        text, n = re.subn(pattern, lambda m, k=key: f"{k}: {paid[k]}", text, count=1)
        if n != 1:
            raise SystemExit(f"SKILL.md 里找不到 {key} 行")
    for key in ("slug", "displayName", "summary"):
        pattern = rf"(?m)^  {key}: .*$"
        text, n = re.subn(pattern, lambda m, k=key: f"  {k}: {paid[k]}", text, count=1)
        if n != 1:
            raise SystemExit(f"SKILL.md 里找不到 {key} 行")

    if "homepage" in paid and paid["homepage"]:
        hp = paid["homepage"]
        text, n_hp = re.subn(r"(?m)^  homepage: .+$", f"  homepage: {hp}", text, count=1)
        text, n_oc = re.subn(r"(?m)^    homepage: .+$", f"    homepage: {hp}", text, count=1)
        if n_hp != 1:
            raise SystemExit("SKILL.md 里找不到 metadata.homepage 行")
        if n_oc != 1:
            raise SystemExit("SKILL.md 里找不到 metadata.openclaw.homepage 行")

    if "handoff" in paid and paid["handoff"]:
        block = _format_handoff_block(paid["handoff"])
        text, n_ho = re.subn(
            r"(?ms)^  handoff: \|$.*?(?=^  [a-zA-Z])",
            block,
            text,
            count=1,
        )
        if n_ho != 1:
            raise SystemExit("SKILL.md 里找不到 metadata.handoff 块")

    with open(skill_path, "w", encoding="utf-8") as fh:
        fh.write(text)

    meta_path = os.path.join(dest, "_meta.json")
    with open(meta_path, encoding="utf-8") as fh:
        meta = json.load(fh)
    for key in ("name", "displayName", "tagline", "description", "summary", "homepage"):
        if key in paid:
            meta[key] = paid[key]
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def replace_asset(dest, name, src):
    """用付费版专用资产替换同名文件。缺文件时返回 False，由调用方报错。"""
    if not os.path.exists(src):
        return False
    shutil.copy2(src, os.path.join(dest, name))
    return True


def zip_tree(src, out_zip, arc_root):
    count = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for base, dirs, files in os.walk(src):
            dirs.sort()
            for name in sorted(files):
                full = os.path.join(base, name)
                rel = os.path.relpath(full, src)
                zf.write(full, os.path.join(arc_root, rel))
                count += 1
    return count


def verify_package(dest, version):
    """构建后自检：文件清单对账 + 残留措辞扫描。返回问题列表，空表示通过。"""
    problems = []
    with open(os.path.join(dest, "_meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)

    expected_top = {"SKILL.md", "_meta.json", "README.md", "LICENSE",
                    "CHANGELOG.md", "PAID-EDITION.md", "scripts", "references", "examples"}
    actual_top = set(os.listdir(dest))
    extra_top = sorted(actual_top - expected_top)
    missing_top = sorted(expected_top - actual_top)
    if extra_top:
        problems.append(f"顶层多余条目：{', '.join(extra_top)}")
    if missing_top:
        problems.append(f"顶层缺少条目：{', '.join(missing_top)}")

    for sub in ("scripts", "references", "examples"):
        expected = {os.path.basename(p) for p in meta.get(sub, [])}
        actual = set(os.listdir(os.path.join(dest, sub)))
        extra = sorted(actual - expected)
        missing = sorted(expected - actual)
        if extra:
            problems.append(f"{sub}/ 多余文件：{', '.join(extra)}")
        if missing:
            problems.append(f"{sub}/ 缺少文件：{', '.join(missing)}")

    for base, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            if name.startswith("."):
                problems.append(f"隐藏文件进包：{os.path.relpath(os.path.join(base, name), dest)}")

    targets = [os.path.join(dest, "SKILL.md"), os.path.join(dest, "README.md")]
    for sub in ("references", "examples"):
        d = os.path.join(dest, sub)
        targets += [os.path.join(d, n) for n in sorted(os.listdir(d)) if n.endswith(".md")]
    for path in targets:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for phrase in PAID_BANNED_PHRASES:
            if phrase in text:
                problems.append(f"{os.path.relpath(path, dest)} 含残留措辞「{phrase}」")

    print()
    if problems:
        print(f"包内自检 FAIL（{len(problems)} 项）：")
        for item in problems:
            print(f"  ✗ {item}")
    else:
        print(f"包内自检 PASS：v{version}，顶层 {len(actual_top)} 项，"
              f"脚本 {len(os.listdir(os.path.join(dest, 'scripts')))} 个，"
              f"参考 {len(os.listdir(os.path.join(dest, 'references')))} 个，"
              f"示例 {len(os.listdir(os.path.join(dest, 'examples')))} 个，"
              "无隐藏文件，无残留措辞")
    return problems


def read_listing_product_name():
    """商品名以 listing-skillpay.md 的「## 商品名称」段为准，不用包内 displayName。"""
    path = os.path.join(ROOT, "listing-skillpay.md")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"(?m)^## 商品名称\s*\n+([^\n#]+?)\s*$", text)
    return m.group(1).strip() if m else ""


def print_upload_checklist(dest, version):
    """打印上传前的人工核对项。平台会按包内元数据自动填充商品名称，这是最容易错的地方。"""
    with open(os.path.join(dest, "_meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    with open(os.path.join(dest, "SKILL.md"), encoding="utf-8") as fh:
        head = fh.read(800)
    m = re.search(r"(?m)^name:\s*(.+)$", head)
    slug = m.group(1).strip() if m else "（未找到 name）"
    display = (meta.get("displayName") or "").strip()
    product_name = read_listing_product_name()

    listing = os.path.join(ROOT, "listing-skillpay.md")
    shop_desc = ""
    if os.path.exists(listing):
        with open(listing, encoding="utf-8") as fh:
            text = fh.read()
        m2 = re.search(r"```text\n(.*?)\n```", text, re.S)
        if m2:
            shop_desc = m2.group(1)

    print()
    print("上传平台前的核对项：")
    if product_name:
        print(f"  1. 商品名称填「{product_name}」（以 listing-skillpay.md 为准）")
    else:
        print("  1. 商品名称：listing-skillpay.md 缺「## 商品名称」段，无法核对")
    print(f"     包内 displayName 是「{display}」，只用于本地区分免费版与付费版，不是平台商品名。")
    print(f"     平台会按 SKILL.md 的 name 自动填成「{slug}」，上传新包后必须手动改回上面的商品名。")
    if shop_desc:
        print(f"  2. 商品描述用仓库根目录的 listing-skillpay.md 那份（{len(shop_desc)} 字含换行，"
              f"平台计 {len(shop_desc.replace(chr(10), ''))}）；别用 SKILL.md 的元数据描述")
    else:
        print("  2. 商品描述：listing-skillpay.md 缺失，无法比对")
    print(f"  3. 版本 {version}；价格沿用平台现有设置；免费试用核对为 0 次（不设试用）")
    n_scripts = len(meta.get("scripts", []))
    n_refs = len(meta.get("references", []))
    drill = os.path.exists(os.path.join(dest, "examples", "gov-service-drill.md"))
    print(f"  4. 包内核对：脚本 {n_scripts} 个；参考 {n_refs} 个；许可 Proprietary")
    print(f"  5. 示例文件 {len(meta.get('examples', []))} 个；办事假账练习卷 {'在' if drill else '缺'}")
    if n_scripts != 11 or n_refs != 16 or not drill:
        print(f"  ⚠ 包内数量与 {version} 预期不一致：应为 11 个脚本、16 个参考、练习卷在")
    if display and slug and display == slug:
        print("  ⚠ displayName 与 name 相同，平台无法区分两者，请检查 _meta.json")


def selftest():
    """按仓库铁律，scripts/*.py 必须能跑 --selftest。这里只验证路径与前置资产。"""
    checks = [
        ("ROOT 指向仓库根", os.path.exists(os.path.join(ROOT, "SKILL.md"))),
        ("edition/ 目录存在", os.path.isdir(EDITION)),
        ("付费章节片段存在", os.path.exists(os.path.join(EDITION, "SKILL.paid-section.md"))),
        ("付费 README 存在", os.path.exists(EDITION_README)),
        ("付费 LICENSE 存在", os.path.exists(EDITION_LICENSE)),
        ("付费 meta 存在", os.path.exists(os.path.join(EDITION, "meta.paid.json"))),
        ("VERSION 可读", os.path.exists(os.path.join(EDITION, "VERSION"))),
        ("_meta.json 可解析", bool(read_public_meta().get("scripts"))),
        ("listing 商品名称可读", bool(read_listing_product_name())),
    ]
    paid_meta = {}
    meta_path = os.path.join(EDITION, "meta.paid.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as fh:
            paid_meta = json.load(fh)
    checks.append(("meta.paid 有 headerNote", bool((paid_meta.get("headerNote") or "").strip())))
    # homepage/handoff：有则覆盖、无则保持——格式化与列表键容错
    ho = _format_handoff_block("- a\n- b\n")
    checks.append(("handoff 块格式化", ho.startswith("  handoff: |\n    - a\n    - b\n")))
    checks.append(("examples 列表键", _meta_list_key("examples/gov-service-drill.md") == "examples"))
    checks.append(("未知路径无列表键", _meta_list_key("other/x") is None))
    ok = True
    for name, good in checks:
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}")
    print("selftest:", "全部通过" if ok else "有失败项")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="组装专业版安装包")
    ap.add_argument("--version", help="专业版版本号（默认读 edition/VERSION）")
    ap.add_argument("--out", help="输出 zip 路径")
    ap.add_argument("--selftest", action="store_true", help="检查路径与前置资产")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    version = args.version
    if not version:
        vpath = os.path.join(EDITION, "VERSION")
        if not os.path.exists(vpath):
            print("缺少 edition/VERSION，也没有 --version", file=sys.stderr)
            return 2
        with open(vpath, encoding="utf-8") as fh:
            version = fh.read().strip()

    meta_path = os.path.join(EDITION, "meta.paid.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as fh:
            meta_version = (json.load(fh).get("version") or "").strip()
        if meta_version and meta_version != version:
            print(f"版本不一致：edition/VERSION={version}，meta.paid.json={meta_version}",
                  file=sys.stderr)
            return 2

    build_dir = os.path.join(EDITION, ".build", "hekouwang-writer-skill")
    if os.path.exists(os.path.join(EDITION, ".build")):
        shutil.rmtree(os.path.join(EDITION, ".build"))
    os.makedirs(build_dir, exist_ok=True)

    n_public = copy_public(build_dir)
    added = copy_paid_assets(build_dir)

    inject_section(os.path.join(build_dir, "SKILL.md"))
    set_skill_version(os.path.join(build_dir, "SKILL.md"), version)
    set_meta(os.path.join(build_dir, "_meta.json"), version, added)
    add_edition_note(build_dir, version, added)
    if not replace_asset(build_dir, "README.md", EDITION_README):
        raise SystemExit("缺少 edition/README.paid.md")
    if not replace_asset(build_dir, "LICENSE", EDITION_LICENSE):
        raise SystemExit("缺少 edition/LICENSE.paid")
    apply_paid_meta(build_dir)

    problems = verify_package(build_dir, version)
    if problems:
        print("未出包：先修上面的自检问题。", file=sys.stderr)
        return 1

    out = args.out or os.path.join(ROOT, "dist", version, f"hekouwang-writer-skill-{version}-paid.zip")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n_zip = zip_tree(build_dir, out, "hekouwang-writer-skill")

    size = os.path.getsize(out) / 1024 / 1024
    print(f"公开文件 {n_public} 个，付费增量 {len(added)} 个")
    print(f"打包完成：{out}")
    print(f"包内 {n_zip} 个文件，{size:.2f} MB，版本 {version}")
    print_upload_checklist(build_dir, version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
