> 组织标准：见 `~/.user-agents/standards/hekouwang-skill-structure.md`  
> 本文件只写本仓特例与成熟度档位。

# hekouwang-writer-skill · 目录结构

## 本仓特例与成熟度

| 项 | 本仓 |
|---|---|
| 成熟度目标 | **L3**（主仓 = Lite；`edition/` = Pro 增量；Pages = `docs/`；白名单 Pro 包；`RELEASE.md`；`.clawhubignore`；bump；`dist/<version>/`） |
| 主仓角色 | 完整 Lite 源码（`hekouwang-writer-lite-skill`）；可安全 `git push origin` |
| Pages | 主仓 **`docs/`**（仓库 Settings → Pages → `/docs`） |
| Pro 增量 | **`edition/`**（独立本地仓，无公开远程） |
| 升级规划 | **`plans/`**（独立本地仓；`evidence/` 可含订单截图） |
| 独立服务 | **`services/skillhub-402/`**（按次 402，独立版本线） |
| 货架物料 | **`materials/`**（原 `images/`；可进 git，不进 Skill/ClawHub 包） |

**已废止**：把必选 `public/` worktree / `product` 分支当作标准发布方式。新人不必学 worktree；日常发版推主仓即可。

## 标准目录树（本仓）

```text
hekouwang-writer-skill/          # = 公开 Git 仓本体（Lite）
├── SKILL.md                     Lite 入口（name: hekouwang-writer-lite-skill）
├── scripts/ · references/ · examples/
├── docs/                        站点源 = GitHub Pages
├── RELEASE.md · STRUCTURE.md · AGENTS.md
├── _meta.json · listing-skillpay.md
├── .clawhubignore
├── materials/                   货架物料（不进安装包）
├── edition/                     Pro 增量（无公开远程）；VERSION 为双产物版本真源
├── plans/                       升级规划与 evidence
├── services/skillhub-402/       按次服务（私有仓）
├── archive/ · dist/             不版控；dist/<version>/ 只留当前版 zip
└── public/                      【遗留】旧 product worktree，非标准，见下文迁移说明
```

```text
专业版 zip  =  主仓（Lite）  ∪  edition/
免费版/公开 =  主仓本身（push origin；Pages 吃 docs/）
```

## 命名

| 版本 | 命名 | 本仓 |
|---|---|---|
| 专业版 | `<name>-skill` | `hekouwang-writer-skill` |
| 免费版 | `<name>-lite-skill` | `hekouwang-writer-lite-skill` |

按次客户端 `hekouwang-writer-check-paid` 不套用上述命名；版本线独立，见 `RELEASE.md`。

## 归属判定

1. 进安装包？→ 主仓（Pro 增量 → `edition/`）  
2. 站点给买家看？→ **`docs/`（主仓内）**  
3. 不能公开？→ `edition/` 或 `plans/`  
4. 独立部署生命周期？→ `services/`

## 推送与远程

| Remote | 用途 |
|---|---|
| `origin` | 公开 Lite 仓；**日常 `git push origin` 推主仓** |
| `paid` | 可选；仅当 Pro 以 git 交付 |

禁止给 `edition/`、`plans/` 加公开远程。`services/<name>/` 只推自己的私有远程。

## `dist/`

产物写在根目录 **`dist/<version>/`**（与 `edition/VERSION` 同号），默认只放 zip，不强制 `SHA256SUMS` / `MANIFEST`。只保留当前版一个 `<version>/` 目录。

## 一期迁移说明（过渡）

旧设计用 `public/` 作为 `product` 分支 worktree、推送公开仓。**该方式已废止为标准**，但本机若仍挂着 `public/`：

- **可暂留**，勿当日常发版出口；`.gitignore` 可保留 `public/` 一行并注明遗留。  
- **日常发版（目标）**：改主仓 → 推主仓到 `origin`；Pages 直接用主仓 `docs/`。  
- **本机陷阱（2026-11-19 仍在）**：`remote.origin.push = refs/heads/product:refs/heads/main`，裸跑 `git push` **不会**推工作区 `main`，只会推 `product`。清掉该 refspec、改 upstream、以及 GitHub Pages 切到默认分支 `/docs`，须维护者确认后另令执行；在此之前不要假设「文档口径 = 本机 push 行为」。  
- ClawHub：从主仓（或打包脚本产出的 Lite 树）发布，勿再以 `public/` 树为真源。  
- `bump_version.py` 对 `public/SKILL.md` / `public/_meta.json` 仍「存在才改」，仅为过渡兼容；目标态不再依赖它们。  
- 废止条件：GitHub Pages 已切到主仓 `docs/`，本地 `origin.push` 已恢复为推主仓，且不再需要经 `product` 旁路后，可拆除 worktree（另令，本阶段不删目录）。

## 禁止（本仓 + 组织标准）

- 免费版与专业版同名  
- 给 `edition/`、`plans/` 加公开远程  
- 把「必选 `public/` 工作树」写进新 Skill 脚手架或本仓日常流程  
- `materials/` / listing / 订单证据打进 Skill 安装包  
- 按次 client 冒充专业版全集  

## 启动指令

> 读组织标准 `~/.user-agents/standards/hekouwang-skill-structure.md`。按「主仓=Lite + `docs/` 做 Pages」「`edition/`=Pro 增量」「`plans/`=升级规划」「`services/`=独立服务」、`-skill`/`-lite-skill` 命名、`materials/` 货架目录、白名单 Pro 打包，审视并改造本仓库；多渠道则更新 `RELEASE.md`。不要再引入必选的 `public/` 工作树。
