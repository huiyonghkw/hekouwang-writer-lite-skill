# Agent 行为验收

`agent-behavior.json` 固定 12 个最小行为用例，覆盖只检查不改写、模态保留、不编经历、免费版升版、数字对账、场景路由、修订对账、诊断落盘和偏好确认。

## 两层判定

1. **机械约束**：必需措辞、禁止措辞、路由、必跑脚本、允许写入文件、受保护文件。
2. **人工语义复核**：每个用例的 `manual_review` 逐项确认。关键词通过不等于文章自然，也不等于事实与意图完整保留。

## 自检

```bash
python3 tools/agent_behavior_check.py --selftest
# 公开 Lite 仓没有 edition/ 时
python3 tools/agent_behavior_check.py --selftest --lite
```

自检验证用例结构、规则锚点、正则和正负例识别，不代表真实宿主已通过行为验收。

## 实际宿主验收

分别在目标 Lite / Pro 安装包和实际宿主 Agent 中运行用例 prompt。保存脱敏 transcript，不保存用户原文、凭证或隐私。格式：

```json
{
  "case_id": "lite-check-only",
  "output": "位置：第 1 行\n原句：……\n问题：……\n建议：……",
  "route": "体检",
  "scripts_run": [],
  "files_written": [],
  "manual_pass": ["只有诊断，没有夹带任何改写文本"]
}
```

运行：

```bash
python3 tools/agent_behavior_check.py \
  --case lite-check-only --transcript <脱敏-transcript.json>
```

退出码：0 = 机械与人工复核均通过；1 = 机械约束失败；2 = 输入错误；3 = 机械通过但人工复核未完成。`manual_pass` 必须逐项包含该用例的 `manual_review` 原文，避免把未检查项误判为通过。

真实宿主验收应在发版前完成并记录宿主、模型、安装包版本和日期；过程 transcript 默认留在本地，不进入用户安装包。
