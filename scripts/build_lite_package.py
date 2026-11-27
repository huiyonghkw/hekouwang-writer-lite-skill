#!/usr/bin/env python3
"""按白名单构建可复现的 Lite 安装包。"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TOP_FILES = ("SKILL.md", "_meta.json", "README.md", "LICENSE", "CHANGELOG.md")
ARC_ROOT = "hekouwang-writer-lite-skill"


def read_meta():
    with (ROOT / "_meta.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def current_version():
    version_file = ROOT / "edition" / "VERSION"
    if version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()
    return str(read_meta()["version"])


def safe_rel(value):
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"非法包内路径: {value}")
    return str(path)


def public_files():
    meta = read_meta()
    rels = list(PUBLIC_TOP_FILES)
    rels += meta.get("scripts", []) + meta.get("references", [])
    examples = ROOT / "examples"
    for base, dirs, files in os.walk(examples):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "__pycache__")
        for name in sorted(files):
            if name.startswith(".") or name.endswith(".pyc"):
                continue
            rels.append((Path(base) / name).relative_to(ROOT).as_posix())
    unique = sorted(set(safe_rel(rel) for rel in rels))
    for rel in unique:
        if not (ROOT / rel).is_file():
            raise FileNotFoundError(f"白名单文件不存在: {rel}")
    return unique


def build_zip(out):
    files = public_files()
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel in files:
                info = zipfile.ZipInfo(f"{ARC_ROOT}/{rel}", (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                zf.writestr(info, (ROOT / rel).read_bytes())
        verify_zip(tmp)
        os.replace(tmp, out)
    finally:
        if tmp.exists():
            tmp.unlink()
    return files


def verify_zip(path):
    expected = {f"{ARC_ROOT}/{rel}" for rel in public_files()}
    with zipfile.ZipFile(path) as zf:
        actual = set(zf.namelist())
        if actual != expected:
            raise ValueError(f"包内清单不一致: extra={sorted(actual - expected)}, missing={sorted(expected - actual)}")
        if zf.testzip() is not None:
            raise ValueError("zip CRC 校验失败")
        meta = json.loads(zf.read(f"{ARC_ROOT}/_meta.json").decode("utf-8"))
        for key in ("scripts", "references"):
            for rel in meta.get(key, []):
                if f"{ARC_ROOT}/{rel}" not in actual:
                    raise ValueError(f"_meta.json 列出但包内缺失: {rel}")
        if f"{ARC_ROOT}/DEVELOPMENT.md" in actual:
            raise ValueError("维护文档不得进入 Lite 安装包")


def selftest():
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lite-selftest-", dir=dist) as tmp:
        out = Path(tmp) / "lite.zip"
        files = build_zip(out)
        with zipfile.ZipFile(out) as zf:
            readme = zf.read(f"{ARC_ROOT}/README.md").decode("utf-8")
            assert readme.startswith("# 会勇禾口王 · 写作技能（免费版）")
            assert len([rel for rel in files if rel.startswith("scripts/")]) == 4
            assert len([rel for rel in files if rel.startswith("references/")]) == 8
            assert f"{ARC_ROOT}/scripts/build_lite_package.py" not in zf.namelist()
            assert f"{ARC_ROOT}/scripts/build_paid_package.py" not in zf.namelist()
    print("selftest: 全部通过（白名单、4 脚本、8 参考、用户 README、无作者工具）")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="构建 Lite 白名单安装包")
    parser.add_argument("--out", help="输出 zip，默认 dist/clawhub/<name>-<version>.zip")
    parser.add_argument("--force", action="store_true", help="允许覆盖已存在的输出文件")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()

    version = current_version()
    out = Path(args.out) if args.out else ROOT / "dist" / "clawhub" / f"hekouwang-writer-lite-skill-{version}.zip"
    if not out.is_absolute():
        out = (Path.cwd() / out).resolve()
    if out.exists() and not args.force:
        print(f"输出已存在：{out}；确认未发布且确需覆盖时加 --force", file=sys.stderr)
        return 2
    try:
        files = build_zip(out)
    except (OSError, ValueError) as exc:
        print(f"构建失败：{exc}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"打包完成：{out}")
    print(f"包内 {len(files)} 个文件，版本 {version}")
    print(f"SHA256：{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
