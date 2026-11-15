# 会勇禾口王 · 写作技能（免费版）

**把话说清楚。** 给素材，写成结构干净的中文文档；给成稿，去掉 AI 味、拆开长句、治标点。

免费版是 MIT-0 开源，克隆即用，不用付款、不用注册。数字对账、证据出处卡、文体规范、长文写作在[付费版](#付费版多什么)。

## 安装

把仓库放进宿主的 skill 目录即可。以 Claude Code 为例：

```bash
git clone https://github.com/huiyonghkw/hekouwang-writer-lite-skill.git \
  ~/.claude/skills/hekouwang-writer-lite-skill
```

也支持 Cursor、Codex、CodeBuddy 等能识别 Skill 目录的宿主。需要 Python 3，不需要装任何第三方库。

## 包含什么

- **4 个检查器**：锯末词、句长、节奏、文档体检（表格列数与标题层级）。只报告，不改写你的文件。
- **8 份参考**：WRITE 五步、七种文档原型、句法纪律、修订模式、去 AI 味、说人话、术语表、盲读。
- **两种模式**：文档写作与体检；文章去 AI 味（`/deai`）。
- **三条铁律**：出处、模态（约／可能／待核实保留）、修订（不悄悄改用户事实）。

常用命令：

```bash
python3 scripts/sawdust_scan.py 文档.md     # 锯末词密度
python3 scripts/sentence_load.py 文档.md    # 长句与分句堆叠
python3 scripts/rhythm_scan.py 文档.md      # 结构层 AI 味
python3 scripts/doc_lint.py 文档.md         # 表格与标题层级
```

## 付费版多什么

付费版名字是 `hekouwang-writer-skill`，能力对照如下。

| 能力 | 免费版 | 付费版 |
|---|---|---|
| 脚本 | 4 | 11 |
| 参考 | 8 | 16 |
| 数字对账、来源范围、修订对账、出处卡 | 无 | 有 |
| 证据纪律、调研报告文体规范 | 无 | 有 |
| 长文写作与三套场景包 | 无 | 有 |

- 在线介绍：<https://huiyonghkw.github.io/hekouwang-writer-lite-skill/>
- 付费版入口见该页面底部

两个版本不要同时安装。

## 许可

MIT-0：可用、可改、可商用、可再分发，不要求署名。见 [LICENSE](LICENSE)。

## 不适用

无素材的营销文案、诗歌小说、英文写作。
