# 渠道与版本矩阵

> 本文件是「哪个产品、哪个版本、发在哪个渠道」的唯一口径。发版前先看这里；`README.md`、`AGENTS.md`、`listing-skillpay.md` 与各渠道后台都以本表为准。
>
> 写作技能版本以 [`edition/VERSION`](edition/VERSION) 为准，不在本文件重复写死；升级用 `python3 scripts/bump_version.py <version>`。
>
> 目录与推送：组织标准见 `~/.user-agents/standards/hekouwang-skill-structure.md`；本仓特例见 [`STRUCTURE.md`](STRUCTURE.md)。Pages = 主仓 `docs/`；日常 `git push origin` 推主仓。  
> 付费化：`~/.user-agents/standards/hekouwang-skill-monetize.md` · 执行门：`…/hekouwang-skill-monetize-playbook.md`。公开面 = **策略 A（Lite 引流）**。  
> 按次产物：`services/skillhub-402/dist/<version>/`（不与技能 `dist/<version>/` 混放）。
>
> 最后更新：2026-11-20

## 一、三个产品，不是三个版本

| # | 产品 | 包名 / slug | 许可 | 卖什么 | 不卖什么 |
|---|---|---|---|---|---|
| 1 | 免费版 | `hekouwang-writer-lite-skill` | MIT-0 | 4 个检查器、8 份参考；文档写作/修订/体检、成稿去 AI 味 | 数字对账、出处卡、修订对账、长文写作、场景包 |
| 2 | 专业版 | `hekouwang-writer-skill` | Proprietary | 11 个脚本、16 份参考；免费版全部能力 + 对账层 + 三套场景包 | 不是按次服务；不通过 SkillHub 交付 |
| 3 | 按次体检 | `hekouwang-writer-check-paid` | Proprietary | 远端检查一段正文：长句、锯末词、数字对账、待核实标记；¥1/次，单篇 ≤ 20,000 字 | 不是专业版 11 脚本包；不给脚本、参考、场景包 |

**一句话**：免费版和专业版是「写作技能」的两个产物；按次体检是另一个「只检查不改写」的远端服务，只是也收费、也在 SkillHub。

## 二、三条版本线

| 版本线 | 版本 | 谁在用 | 规则 |
|---|---|---|---|
| 写作技能 · 免费版 | 见 `edition/VERSION` | ClawHub、GitHub、GitHub Pages | 与专业版同号 |
| 写作技能 · 专业版 | 见 `edition/VERSION` | 支付宝 SkillPay 订阅 | 与免费版同号；包在 `dist/<version>/hekouwang-writer-skill-<version>-paid.zip` |
| 按次体检 · 客户端/服务 | 线上 2.0.1 | 腾讯 SkillHub Pay Skill | 独立版本线，不跟随写作技能版本；2.0.1 补「会」字与文案，已审核通过 |

**不要把写作技能版本和 2.0.0/2.0.1 对比**：它们不是同一个产品的版本号。

## 三、渠道矩阵

| 渠道 | 上架产品 | 版本 | 包 / 源 | 价格 | 线上状态 |
|---|---|---|---|---|---|
| 支付宝 SkillPay | 专业版 `hekouwang-writer-skill` | 见 `edition/VERSION` | `dist/<version>/hekouwang-writer-skill-<version>-paid.zip` | ¥9.9 / 30 天，0 试用，不自动续费 | 以支付宝商品页为准；新构建上传后更新 |
| ClawHub | 免费版 `hekouwang-writer-lite-skill` | 见 `edition/VERSION` | 主仓 Lite 树（`.clawhubignore` 排除 materials/listing/edition/roadmap/services/dist 等） | 免费，MIT-0 | 以 ClawHub 页面为准；新版本发布后更新 |
| 腾讯 SkillHub | 按次体检 `hekouwang-writer-check-paid` | 线上 2.0.1 | `services/skillhub-402/client/` | ¥1 / 次 | 2.0.1 已审核通过并上线；详情页 https://skillhub.cn/skills/indiv-huiyonghkw/hekouwang-writer-skill |
| GitHub / GitHub Pages | 免费版 | 见 `edition/VERSION` | 主仓；Pages 源 = 主仓 **`docs/`** | 免费 | 以 Pages 为准；`git push origin` 后更新 |

**专业版不在 ClawHub。免费版不在支付宝。SkillHub 上的不是专业版 11 脚本包。**

## 四、命名对照

| 场景 | 用哪个名字 |
|---|---|
| 免费版包名、slug、仓库名 | `hekouwang-writer-lite-skill` |
| 专业版包名、slug、仓库名 | `hekouwang-writer-skill` |
| 按次体检客户端 slug | `hekouwang-writer-check-paid` |
| 支付宝商品名 | 会勇禾口王 · 写作技能（平台字段不带「专业版」后缀） |
| SkillHub 商品名 | 会勇禾口王 · 写作体检（按次） |
| 用户面文案 | 免费版 / 专业版 / 按次体检；「付费版」只作商业描述，「完整版」「订阅版」不当产品名 |

## 五、发版规则

1. **先看本表**：确认要发的是哪个产品、哪个渠道、哪条版本线。
2. **升级写作技能版本**：跑 `python3 scripts/bump_version.py <version>`，再跑 `--check` 必须 PASS；不要手改 `SKILL.md`、`_meta.json`、`edition/meta.paid.json`。
3. **专业版**：先改 `listing-skillpay.md`，再改平台商品描述；然后跑 `python3 scripts/build_paid_package.py`，产物是 `dist/<version>/hekouwang-writer-skill-<version>-paid.zip`。
4. **免费版 / Pages**：改主仓（含 `docs/`）→ `git push origin`；ClawHub 从主仓发布，版本与根 `_meta.json` / `SKILL.md` 一致。不要再走 `public/` worktree / `product` 分支（遗留见 STRUCTURE 迁移说明）。
5. **按次体检**：只改 `services/skillhub-402/client/`，版本线独立；不要把它改成写作技能版本，也不要把专业版的 11 个脚本塞进去。
6. **不覆盖已发布包**：任何包内容变化都要升对应版本线的号；不要用同一个版本号覆盖已发布包。
7. **ClawHub 发布必须设置 Catalog metadata**：CATEGORIES 不要留 `Other`，TOPICS 不能为空；CLI 用 `--categories` / `--topics`，发布后回读设置页核对。
8. **`dist/`**：只保留当前版 `dist/<version>/`，目录内默认只放 zip；不强制 `SHA256SUMS` / `MANIFEST`（需要校验时临时 `shasum -a 256`，结果可写 `roadmap/` 发版回执）。

## 六、当前工作区备注

- `dist/` 只保留当前版 `dist/<version>/`，**目录内默认只放 zip**（Lite + Pro）。发版说明 / SHA256 快照在 `roadmap/evidence/`（如 `2026-11-17-release-2.0.7/`）。
- 按次 SkillHub 包在 `services/skillhub-402/dist/<version>/`，不与技能 `dist/` 混放。
- 主仓是免费版真源；日常 `git push origin`；GitHub Pages = 主仓 `docs/`。`public/` 旁路已拆除。
- `roadmap/` 执行计划与证据；渠道/版本口径以本文件为准。公开面 = 策略 A（Lite 引流）。

## 七、2.0.6 封版记录（2026-11-16）

> 以下为当时发布快照；路径写法（`public/product`、`dist/release-*`）属历史事实，日常流程以本文第三～五节为准。

| 项 | 状态 |
|---|---|
| 免费版 / 专业版 | 2.0.6，内容冻结 |
| GitHub | `public/product` `6e00777`，tag `v2.0.6`，Release 已发布 |
| ClawHub | 2.0.6 已审核通过并上线；Catalog metadata 仍是 Other，下个版本必须补 categories/topics |
| SkillPay | 2.0.6 已上架；包在 `dist/release-2.0.6/hekouwang-writer-skill-2.0.6-paid.zip` |
| SkillHub | 2.0.1 客户端包待审核；线上 2.0.0 |

- 免费包 SHA256：`a5b824c3d29c3ef5642a6a964af18e6eb290baf202c0ad47fab0501f1d38b7c8`
- 专业版 SHA256：`4d1ab0d081919717d5b30359107c95457dce3deb8b880eb0b8a7062c471a85fb`
- SkillHub SHA256：`a8e9fd4ed3eb431a8c73e282ff5d8c97ddaafd7b953cfc6143572027281db303`
- 详细说明：`dist/release-2.0.6/RELEASE-2.0.6.md`、`SKILLPAY-2.0.6.md`、`SKILLHUB-2.0.1.md`
- 2.0.6 内容冻结；下一次内容变更升 2.0.7，SkillHub 客户端继续独立版本线。

## 八、2.0.7 封版记录（2026-11-17）

> 以下为当时发布快照；路径写法属历史事实，日常流程以本文第三～五节为准。

| 项 | 状态 |
|---|---|
| 免费版 / 专业版 | 2.0.7，内容冻结 |
| GitHub | `public/product` `c269bab`；tag `v2.0.7` 已对齐 `c269bab`；Release 资产已上传 |
| ClawHub | 2.0.7 已审核通过并上线；Catalog metadata 已设置（Creative + Productivity；4 个 topics） |
| SkillPay | 2.0.7 已审核通过并发布；包在 `dist/release-2.0.7/hekouwang-writer-skill-2.0.7-paid.zip` |
| SkillHub | 2.0.1 客户端包待审核；线上 2.0.0 |

- 免费包 SHA256：`1a0cd812a9d4bdecb57681ce38e113bd5fce3b5f566e11d62b35c34911455ce7`
- 专业版 SHA256：`ebdbfed4958da85625de66d3596f18e6033d718c1e9a00204b4975cb1e93728d`
- SkillHub SHA256：`a8e9fd4ed3eb431a8c73e282ff5d8c97ddaafd7b953cfc6143572027281db303`
- 详细说明（已迁）：`roadmap/evidence/2026-11-17-release-2.0.7/`；SkillHub zip：`services/skillhub-402/dist/2.0.1/`
- 2.0.7 内容冻结；下一次内容变更升 2.0.8；ClawHub 发布必须设置 Catalog metadata。

## 九、SkillHub 2.0.1 上线（2026-11-20）

| 项 | 状态 |
|---|---|
| 按次体检客户端 | 2.0.1 已审核通过并上线，替换原线上 2.0.0 |
| 商品页 | https://skillhub.cn/skills/indiv-huiyonghkw/hekouwang-writer-skill ，标题「会勇禾口王 · 写作体检（按次）」，标 v2.0.1 |
| SHA256 | `a8e9fd4ed3eb431a8c73e282ff5d8c97ddaafd7b953cfc6143572027281db303`（与提交包一致） |
| 包路径 | `services/skillhub-402/dist/2.0.1/`；说明见 `roadmap/evidence/2026-11-17-release-2.0.7/SKILLHUB-2.0.1.md` |

本变更只更新渠道口径与证据；写作技能免费版 / 专业版版本号不变。
