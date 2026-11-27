# 渠道与版本矩阵

> 本文件是产品、版本状态与发布顺序的唯一当前口径。历史封版记录只证明当时状态，不代表现在。
>
> 写作技能版本真源是 [`edition/VERSION`](edition/VERSION)，升级用 `python3 scripts/bump_version.py <version>`；按次客户端和服务镜像各自独立版本。
>
> 最后更新：2026-11-27。

## 一、三个产品，不是三个版本

| 产品 | 包名 / slug | 许可 | 当前能力 | 不是什么 |
|---|---|---|---|---|
| 免费版 | `hekouwang-writer-lite-skill` | MIT-0 | 4 检查器、8 参考；文档写作/修订/体检、成稿去 AI 味 | 不含数字对账、出处卡、长文写作、场景包 |
| 专业版 | `hekouwang-writer-skill` | Proprietary | 11 脚本、21 参考；免费版全部能力 + 对账层 + 8 套场景包 | 不是按次服务，不通过 SkillHub 交付 |
| 按次体检 | `hekouwang-writer-check-paid` | Proprietary | 远端组合检查长句、锯末词、数字对账、待核实标记；文章另查节奏；¥1/次，单篇 ≤20,000 字 | 不是专业版脚本包，不给脚本、参考、场景包 |

## 二、当前版本状态

“本地源码 / 本地包”与“线上版本”分开记录；未经平台回读，不把历史记录写成当前线上事实。

| 产物 | 本地源码 | 本地新包 | 审核 / 线上状态 |
|---|---|---|---|
| 写作技能 Lite | 2.2.1 | 2.2.1，已构建并通过最终验收 | ClawHub latest **2.2.0**，扫描 **clean**；2026-11-27 已通过 `clawhub inspect` 回读 |
| 写作技能 Pro | 2.2.1 | 2.2.1，已构建并通过最终验收 | SkillPay 后台待核实；本地历史记录为线上 2.0.7，公开购买页只能读到通用说明 |
| 按次客户端 | 2.2.0 | 2.2.0，已构建并通过确定性构建验收 | 2.1.1 已于 2026-11-27 提交审核；线上版本待后台核实，本地历史记录为 2.1.0 |
| 按次服务镜像 | 0.2.0 | 本地构建与镜像内 smoke test 通过 | 尚未推送或部署；线上服务版本与真实支付链路待核实 |

新版本均未上传、未提审。2.2.1 不覆盖写作技能 2.2.0 包，按次 2.2.0 不覆盖已提审的 2.1.1 包。

## 三、渠道矩阵

| 渠道 | 上架产品 | 发布来源 | 价格 | 当前动作 |
|---|---|---|---|---|
| 支付宝 SkillPay | 专业版 | `dist/skillpay/hekouwang-writer-skill-2.2.1-paid.zip` | ¥9.9 / 30 天，0 试用，不自动续费 | 后台先核实线上版本，再上传 2.2.1 并重贴商品名与描述 |
| ClawHub | 免费版 | 主仓 Lite 树；zip 只作存档 | 免费，MIT-0 | 已确认线上 2.2.0 clean；发布 2.2.1 时设置 categories/topics 并回读 |
| 腾讯 SkillHub | 按次体检 | `services/skillhub-402/dist/2.2.0/` 与 `dist/skillhub/` 发布副本 | ¥1 / 次 | 先部署服务 0.2.0，再提审客户端 2.2.0，最后确认线上结果 |
| GitHub / GitHub Pages | 免费版与产品页 | 主仓 `main`，Pages 源 = `docs/` | 免费 | 对外推送后回读；按次新能力文案须在服务部署后公开 |

专业版不在 ClawHub。免费版不在支付宝。SkillHub 上的按次客户端不是专业版 11 脚本包。

## 四、命名对照

| 场景 | 用哪个名字 |
|---|---|
| 免费版包名、slug、仓库名 | `hekouwang-writer-lite-skill` |
| 专业版包名、slug | `hekouwang-writer-skill` |
| 按次体检客户端 slug | `hekouwang-writer-check-paid` |
| 支付宝商品名 | 会勇禾口王 · 写作技能 |
| SkillHub 商品名 | 会勇禾口王 · 写作体检（按次） |
| 用户面文案 | 免费版 / 专业版 / 按次体检；“付费版”只作商业描述，“完整版”“订阅版”不当产品名 |

## 五、发版规则

1. **先核实状态**：区分源码、已打包、审核中、线上版本；平台状态不明时先回读后台。
2. **升级写作技能**：跑 `bump_version.py <version>` 与 `--check`；标准布局检查 4 个版本点，不手改。
3. **文案先行**：Pro 能力变化先改 `listing-skillpay.md`，再改平台商品描述。
4. **构建新包**：Lite 跑 `build_lite_package.py`；Pro 用 `--out` 指向 `dist/skillpay/`。不覆盖已发布包，已存在输出只有确认未发布后才用 `--force`。
5. **最终验收**：跑 `python3 tools/release_check.py --check`，必须全部 PASS；按次另跑服务端 `unittest`、客户端 `node --test`、跨语言集成和镜像 smoke test。再跑 `python3 tools/docs_check.py`，检查无 JS 回退、链接、复制目标、分享元数据、升级路径和可访问性约束。
6. **Pages 发布门禁**：SkillPay 可下载包、按次线上服务与官网能力描述必须一致。若线上仍是旧包或未部署新服务，只发布仓库代码，不公开对应官网文案；先完成平台对齐再推 Pages。
7. **按次发布顺序**：先部署服务 0.2.0 并验证组合检查、故障语义和沙箱支付，再提审客户端 2.2.0，最后公开对应官网文案。
8. **免费版 / Pages**：改主仓后推送 `origin/main`；ClawHub 发布必须设置 categories/topics，不使用已废止的 `public/` worktree / `product` 分支。
9. **不覆盖已发布包**：任何包内容变化都升对应版本线。
10. **回读再记账**：上传、提审或部署后回读线上版本、扫描状态、商品描述和实际检查结果，再更新本文件。

## 六、当前工作区备注

- `dist/<channel>/` 是当前发布视图；`dist/<version>/` 仅临时构建留档，不是发布真源。
- `dist/README.md` 是包索引，不另立线上状态；与本文件冲突时以平台回读和本文件为准。
- 根 `README.md` 随 Lite 分发，`DEVELOPMENT.md` 只随仓库；两个写作包都由白名单构建并做确定性输出。
- 按次服务包在 `services/skillhub-402/dist/<version>/`，不与写作技能版本混放。
- 推送、上传、提审、部署和真实支付验证均需本人明确确认，不由检查脚本自动执行。

## 七、2.0.6 封版记录（2026-11-16）

> 以下为当时发布快照；路径写法（`public/product`、`dist/release-*`）属历史事实，日常流程以本文第三～六节为准。

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

## 八、2.0.7 与 2.1.0 封版记录（2026-11-17 / 2026-11-25）

> 以下为当时发布快照；路径写法属历史事实，日常流程以本文第三～六节为准。

| 项 | 状态 |
|---|---|
| 免费版 / 专业版 | 2.0.7，内容冻结 |
| GitHub | `public/product` `c269bab`；tag `v2.0.7` 已对齐 `c269bab`；Release 资产已上传 |
| ClawHub | 2.0.7 已审核通过并上线；Catalog metadata 已设置（Creative + Productivity；4 个 topics） |
| SkillPay | 2.0.7 已审核通过并发布；包在 `dist/release-2.0.7/hekouwang-writer-skill-2.0.7-paid.zip` |
| SkillHub | 2.0.1 客户端包待审核；线上 2.0.0 |

- 免费包 SHA256：`1a0cd812a9d4bdecb57681ce38e113bd5fce3b5f566e11d62b35c34911455ce7`
- 专业版 SHA256：`ebdbfed4958da85625de66d3596f18e6033d718c1e9a00204b377fe2e419257b959`
- SkillHub SHA256：`a8e9fd4ed3eb431a8c73e282ff5d8c97ddaafd7b953cfc6143572027281db303`
- 发版结论见 `roadmap/` 对应规划；SkillHub zip：`services/skillhub-402/dist/2.0.1/`
- 2.0.7 内容冻结；下一次内容变更按 2.1.0 执行；ClawHub 发布必须设置 Catalog metadata。

### 2.1.0 封版记录（2026-11-25，规划定稿）

| 项 | 状态 |
|---|---|
| 免费版 / 专业版 | 2.1.0 规划定稿，发版时两产物同号 |
| 专业版能力 | 7 套场景包（新增调研报告 / 技术文档 / PRD 规格书 / 会议纪要）、假靶心判定规则 + 证据核对、证据对账表、体检档、文章偏好、正式体例豁免、场景路由；两个脚本增强（sawdust_scan、doc_lint） |
| 清单口径 | 专业版 11 脚本 / 20 参考；listing 平台计 442/500 字 |

- 有意识跨 minor（新场景包 + 新能力），从 2.0.7 直接到 2.1.0。
- 当时发版按 `roadmap/写作技能2.1版本规划.md` 第八节执行；当前流程以第五～六节为准。

## 九、SkillHub 2.0.1 上线（2026-11-20）

| 项 | 状态 |
|---|---|
| 按次体检客户端 | 2.0.1 已审核通过并上线，替换原线上 2.0.0 |
| 商品页 | https://skillhub.cn/skills/indiv-huiyonghkw/hekouwang-writer-skill ，标题「会勇禾口王 · 写作体检（按次）」，当时标 v2.0.1 |
| SHA256 | `a8e9fd4ed3eb431a8c73e282ff5d8c97ddaafd7b953cfc6143572027281db303`（与提交包一致） |
| 包路径 | `services/skillhub-402/dist/2.0.1/`；发版结论见 `roadmap/` 对应规划 |

本历史记录只证明 2.0.1 当时上线；当前线上版本须按第二～五节重新回读。
