#!/usr/bin/env python3
"""固定 Agent 行为用例的机械约束检查；语义质量仍需人工复核。"""

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals" / "agent-behavior.json"


def load_cases():
    with CASES_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("schema_version") != 1:
        raise ValueError("不支持的用例 schema_version")
    return data["cases"]


def matches(patterns, text):
    return [pattern for pattern in patterns if re.search(pattern, text, re.I | re.M)]


def evaluate(case, transcript):
    problems = []
    output = transcript.get("output", "")
    if not isinstance(output, str) or not output.strip():
        return ["transcript.output 必须是非空字符串"], []
    for pattern in case.get("required_output", []):
        if not re.search(pattern, output, re.I | re.M):
            problems.append(f"输出缺少必需模式: {pattern}")
    for pattern in matches(case.get("forbidden_output", []), output):
        problems.append(f"输出命中禁止模式: {pattern}")

    route = case.get("expected_route")
    if route and transcript.get("route") != route:
        problems.append(f"路由应为 {route}，实际为 {transcript.get('route')}")
    scripts_run = {PurePosixPath(item).name for item in transcript.get("scripts_run", [])}
    missing_scripts = set(case.get("required_scripts", [])) - scripts_run
    if missing_scripts:
        problems.append("缺少必跑脚本: " + ", ".join(sorted(missing_scripts)))

    written = transcript.get("files_written", [])
    if not isinstance(written, list):
        return problems + ["transcript.files_written 必须是数组"], []
    policy = case.get("write_policy", "allow_list")
    if policy == "none" and written:
        problems.append("本用例禁止写文件: " + ", ".join(written))
    elif policy == "allow_list":
        allowed = set(case.get("allowed_files", []))
        for path in written:
            if PurePosixPath(path).name not in allowed:
                problems.append(f"写入未允许文件: {path}")
    for path in written:
        if PurePosixPath(path).name in case.get("protected_files", []):
            problems.append(f"覆盖受保护文件: {path}")

    manual = case.get("manual_review", [])
    passed = set(transcript.get("manual_pass", []))
    missing_manual = [item for item in manual if item not in passed]
    return problems, missing_manual


def validate_cases(cases, lite=False):
    problems = []
    ids = set()
    for case in cases:
        case_id = case.get("id", "")
        if not case_id or case_id in ids:
            problems.append(f"用例 id 为空或重复: {case_id}")
        ids.add(case_id)
        if case.get("edition") not in ("lite", "pro", "both"):
            problems.append(f"{case_id}: edition 非法")
        anchor = case.get("rule_anchor")
        if not anchor or not (ROOT / anchor).is_file():
            if not lite or case.get("edition") in ("lite", "both"):
                problems.append(f"{case_id}: 规则锚点不存在 {anchor}")
        for group in ("required_output", "forbidden_output"):
            for pattern in case.get(group, []):
                try:
                    re.compile(pattern)
                except re.error as exc:
                    problems.append(f"{case_id}: 正则 {pattern} 无效: {exc}")
        if case.get("write_policy", "allow_list") == "allow_list" and not case.get("allowed_files"):
            problems.append(f"{case_id}: allow_list 但没有 allowed_files")
    return problems


def selftest(lite=False):
    cases = load_cases()
    problems = validate_cases(cases, lite=lite)
    by_id = {case["id"]: case for case in cases}
    good = {
        "output": "位置：第 1 行\n原句：原文\n问题：问题\n建议：建议\n确认后不写文件",
        "route": "体检",
        "files_written": [],
        "scripts_run": [],
        "manual_pass": by_id["lite-check-only"]["manual_review"],
    }
    _, manual = evaluate(by_id["lite-check-only"], good)
    if manual:
        problems.append("自检人工复核字段未识别")
    bad = dict(good, output="润色后全文", files_written=["原文.md"], manual_pass=[])
    mechanical, _ = evaluate(by_id["lite-check-only"], bad)
    if len(mechanical) < 4:
        problems.append("自检负例未捕获缺少字段、禁止措辞和写文件")
    if problems:
        print("selftest: 有失败项", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    print(f"selftest: 全部通过（{len(cases)} 个行为用例，正负例机械检查）")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Agent 行为用例机械约束检查")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--lite", action="store_true", help="公开 Lite 仓没有 edition，跳过 Pro 锚点存在性检查")
    parser.add_argument("--case", dest="case_id", help="evals/agent-behavior.json 的用例 id")
    parser.add_argument("--transcript", help="实际宿主输出 JSON")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest(lite=args.lite)
    if not args.case_id or not args.transcript:
        parser.print_help()
        return 2

    cases = {case["id"]: case for case in load_cases()}
    case = cases.get(args.case_id)
    if not case:
        print(f"未知用例: {args.case_id}", file=sys.stderr)
        return 2
    transcript_path = Path(args.transcript)
    with transcript_path.open(encoding="utf-8") as fh:
        transcript = json.load(fh)
    if transcript.get("case_id") != args.case_id:
        print("transcript.case_id 与 --case 不一致", file=sys.stderr)
        return 2
    mechanical, manual = evaluate(case, transcript)
    for problem in mechanical:
        print(f"FAIL: {problem}")
    for item in manual:
        print(f"MANUAL: {item}")
    if mechanical:
        return 1
    if manual:
        print("机械约束通过；人工语义复核尚未完成。")
        return 3
    print("机械约束与人工语义复核均通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
