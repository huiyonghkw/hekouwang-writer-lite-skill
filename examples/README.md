# 案例索引

这些案例展示 writer-skill 如何处理不同任务。

- **真实实测**（3）：`family-pension-case.md`、`terminal-readme-deai-case.md`、`skill-research-case.md`——有当次诊断、改法与检查／对账摘要；已脱敏，不附完整原稿。
- **练习卷**（1）：`gov-service-drill.md`——故意写错，用来练三种假账怎么被脚本拦住。
- **流程演示**（其余）：说明如何调用规则和检查器；占位数据须替换。

产品页突出 **2 个真实实测** + **1 个示意**（只检查）；练习卷以本目录为准。

| 案例 | 交付能力 | 模式 | 主要检查/交付证据 |
|---|---|---|---|
| [家庭办事文档](family-pension-case.md) | 从真实材料写办事文档 | 文档写作 | 出处、模态、数字出处卡、改动清单、对账与脚本结果 |
| [产品 README 去 AI 味](terminal-readme-deai-case.md) | 先诊断再保真改写 | 文章修订 | 分档合并、产品词人话、盲读、change_list 摘要 |
| [办事假账练习卷](gov-service-drill.md) | 练合计错、跨接口合并、出处卡 | 文档检查 | check_fidelity / scope_lint / provenance_card 期望退出码 |
| [同类 SKILL 调研报告](skill-research-case.md) | 从多来源材料写调研报告 | 文档写作 | 证据分级 A/B/C、样本表、局限单列、三个检查器与数字出处卡 |
| [新写操作说明](write-sop.md) | 从素材写新文档 | 文档写作 | WRITE 五步、章节核心句、术语和待核实项 |
| [修订项目汇报](revise-project-report.md) | 改进既有文档并保护用户文字 | 文档修订 | 改前后差异、改动清单、范围保护和数字变化处理 |
| [只检查，不改写](doc-checkup-only.md) | 体检并定位问题 | 文档检查 | 原句/问题/建议；advisory 告警与硬错误退出码区别 |
| [从研究材料写文章](article-from-research.md) | 将已确认材料组织成正文 | 文章写作 | 核心判断、数字三标签、来源边界和盲读 |
| [文章去 AI 味](deai-rewrite.md) | 先诊断再保真改写（占位） | 文章修订 | 流程示意；真实测见 terminal-readme-deai-case |

流程演示里的「预期检查」只说明应当如何验证，不是已经执行过的脚本输出。真实使用时需对实际输入运行对应脚本，并报告实际结果。
