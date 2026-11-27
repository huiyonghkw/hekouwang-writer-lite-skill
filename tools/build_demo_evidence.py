#!/usr/bin/env python3
"""从官网脱敏输入重新生成真实检查器 JSON 输出。"""

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "docs/examples/checker-demo.md"
COMMANDS = {
    "check_fidelity": "edition/scripts/check_fidelity.py",
    "sentence_load": "scripts/sentence_load.py",
    "sawdust_scan": "scripts/sawdust_scan.py",
    "doc_lint": "scripts/doc_lint.py",
}


def main():
    outputs = {}
    for name, script in COMMANDS.items():
        result = subprocess.run(
            [sys.executable, script, "--json", SOURCE], cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode not in (0, 1):
            print(f"{name} 执行失败：{result.stderr}", file=sys.stderr)
            return 1
        outputs[name] = json.loads(result.stdout)
    if not outputs["check_fidelity"]["errors"]:
        raise ValueError("示例未检出数字错误")
    if not (outputs["sentence_load"]["over"] or outputs["sentence_load"]["warn_items"]):
        raise ValueError("示例未检出长句")
    if not outputs["sawdust_scan"]["over"]:
        raise ValueError("示例未检出锯末词密度告警")
    if not outputs["doc_lint"]["pending_markers"]:
        raise ValueError("示例未检出待核实标记")
    evidence = {
        "description": "脱敏演示的真实脚本输出；未手工修改数字或结论。",
        "input": SOURCE,
        "commands": {name: f"python3 {script} --json {SOURCE}" for name, script in COMMANDS.items()},
        "outputs": outputs,
    }
    target = ROOT / "docs" / "examples" / "checker-demo.json"
    target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已生成：{target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
