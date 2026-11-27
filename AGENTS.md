# hekouwang-writer-skill · 维护规则

本仓库是开发与构建仓库：根目录 `SKILL.md` 是免费版（`hekouwang-writer-lite-skill`），专业版（`hekouwang-writer-skill`）由 `edition/` 叠加组装。本文件只管"改这个仓库时"的规矩。

## 30 秒速览

- 产品：中文写作 skill，文档模式（写作/体检）+ 文章模式（写作/修订/去 AI 味）。技术栈：Markdown + Python 3 stdlib 脚本，零依赖。
- 三个渠道：支付宝 SkillPay 专业版、ClawHub 免费版、腾讯 SkillHub 按次体检。口径见 [`RELEASE.md`](RELEASE.md)。
- 新内容放哪：规则细节 → `references/`；可执行检查 → `scripts/`；`SKILL.md` 只放铁律、路由和指针。

## 常用命令

```bash
# 全套脚本自检（6 个脚本，改动 scripts/*.py 后必跑）
for f in scripts/*.py; do python3 "$f" --selftest || exit 1; done

# 单脚本自检（定位单个检查器时用）
python3 scripts/doc_lint.py --selftest

# 升级版本（6 个版本点一次更新）/ 校验一致
python3 scripts/bump_version.py 2.1.0
python3 scripts/bump_version.py --check

# 组装专业版包（默认读 edition/VERSION；发布视图走渠道轴 dist/skillpay/）
python3 scripts/build_paid_package.py

# 改过 docs/ 文案后重建字体子集
bash scripts/subset-fonts.sh

# 本地预览产品页
python3 -m http.server 8788 --directory docs
```

无第三方依赖，也不需要单独的 lint/test 框架——测试就是每个脚本内置的 `--selftest`。构建脚本默认输出在 `dist/<version>/` 仅为留档；发布出口按 STRUCTURE 渠道轴 `dist/<channel>/`，历史版只读归档、非发布真源。

## 架构：一份源码，三个产物

- **免费版** = 主仓本身（根 `SKILL.md` + `scripts/` 4 个检查器 + `references/` 8 份；MIT-0）。
- **专业版** = 主仓 ∪ `edition/` 叠加层（`build_paid_package.py` 先拷主仓、再叠 `edition/`、替换 name/描述/许可、删掉只对免费版成立的段落；11 脚本 / 21 参考）。
- **按次体检** = `services/skillhub-402/`，独立服务 + 独立版本线，只检查不改写，不是专业版脚本包。
- 版本真源是 `edition/VERSION`，`bump_version.py` 统一维护 6 个版本点；写作技能两产物同号，按次体检独立。
- 四个文档检查器（`doc_lint.py`、`sentence_load.py`、`rhythm_scan.py`、`sawdust_scan.py`）统一契约：可接文件参数或 stdin、`--json` 输出、**只报告不改写用户文档**；`--json` 字段名是 `dianping-review-skill/writer_bridge.py` 的运行时依赖，只许加不许改。

## 目录结构

按组织标准 `~/.user-agents/standards/huiyonghkw/skills/skill-structure.md` 与本仓 [`STRUCTURE.md`](STRUCTURE.md) 执行：主仓 = Lite 源码 + `docs/`（GitHub Pages）；日常 `git push origin` 推 `main`；`edition/` = Pro 增量；`roadmap/` = 升级与作战地图（规划/方案/执行计划与发版结论，不留过程凭证；勿与对外产品路线混淆）；`services/` = 独立服务；`materials/` = 货架物料；`archive/`、`dist/` 不版控。**已废止** `public/` worktree / `product` 旁路（见 STRUCTURE 迁移说明）。新建或改造其他 Skill 仓库时照组织标准执行。

## 铁律

1. 改 `scripts/*.py` 后必须跑上面「常用命令」一节的全套自检（6 个 `--selftest` 全过）才能提交；定位单个检查器时用单脚本自检。
2. 版本号分两条线，渠道不要混：
   - **两个写作技能产物同号**：以 `edition/VERSION` 为准。升级跑 `python3 scripts/bump_version.py <version>`，再跑 `--check`；构建仍跑 `python3 scripts/build_paid_package.py`。不要手改 `SKILL.md`、`_meta.json`、`edition/meta.paid.json` 的版本号。
   - **按次体检客户端独立版本线**：`services/skillhub-402/client/SKILL.md` 本地已备 2.2.0（与写作技能号对齐，功能同 2.0.1，待上传），线上仍 2.0.1；不自动跟随写作技能版本，也不要把专业版 11 个脚本塞进去。
   - 渠道与版本矩阵见 [`RELEASE.md`](RELEASE.md)；发版前先看，别把三个渠道混成一条线。
   产品页不展示版本号，别在 HTML 里加回去。
   发版前还要比对仓库根目录的 `listing-skillpay.md`：包内能力有变化，先改那份文案再改平台商品描述；顺序反了就是拿旧描述送审，SkillPay 会以「描述与上传文件能力说明不一致」驳回。
3. 新增或改名 `references/*.md` 时，同步 `SKILL.md` 指针和根 `_meta.json` 的 `references`。**文件在根目录和 `edition/` 之间移动时，两边都要改**：根目录只放免费内容，`edition/` 放专业版增量；移动后必须重建专业版包并检查两个版本各自无死链。
4. `SKILL.md` 不重复 `references/` 的细节，只留要点 + 一行指针；改完跑 skill doctor 确认无死链、门禁 PASS。
5. 改 `docs/` 页面文案后必须重跑 `bash scripts/subset-fonts.sh`（字体子集只含现有文字，漏跑新字会回退苹方）。

## 禁止清单（Do NOT）

- 不要引入第三方依赖（因为卖点是零依赖、装上即跑）。
- 不要把 SkillHub 按次体检当成专业版 11 脚本包，也不要把专业版发到 ClawHub；三个渠道见 [`RELEASE.md`](RELEASE.md)。
- 不要让脚本改写用户文档（因为修订铁律要求改动可列出、可回退，脚本只报告）。
- 不要在 `.learnings/`、`examples/` 写入真实姓名、证件号、令牌（因为安装包会分发到用户手上）。
- 不要改动四个文档检查器 `--json` 输出的已有字段名和含义，也不要去掉 stdin 输入（因为 dianping-review-skill 的 `writer_bridge.py` 在运行时依赖它们）。只许加字段；非改不可时升主版本，并同步改 dianping。
