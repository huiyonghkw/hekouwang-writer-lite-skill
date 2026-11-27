# hekouwang-writer-skill · 开发与维护

本仓是本地开发与构建仓库。根目录 `README.md` 是随 Lite 分发的用户入口；本文件只服务维护者，并通过 `.clawhubignore` 排除在安装包之外。

同一份源码出两个写作技能产物：免费版 `hekouwang-writer-lite-skill` 与专业版 `hekouwang-writer-skill`；另有独立的按次体检客户端 `hekouwang-writer-check-paid`。命名与目录边界见 [`STRUCTURE.md`](STRUCTURE.md)，渠道和线上状态见 [`RELEASE.md`](RELEASE.md)。

## 产物与源码

| 产物 | 来源 | 许可 | 脚本 / 参考 |
|---|---|---|---|
| 免费版 `hekouwang-writer-lite-skill` | 根目录白名单 | MIT-0 | 4 / 8 |
| 专业版 `hekouwang-writer-skill` | 根目录 + `edition/` | Proprietary | 11 / 21 |
| 按次体检 `hekouwang-writer-check-paid` | `services/skillhub-402/client/` | Proprietary | 独立远端服务与版本线 |

免费版管表达（结构、句子、去 AI 味）。专业版增加证据纪律、数字对账、出处卡、修订对账、文体规范、长文写作与八套场景包。

## 目录

| 路径 | 归属 | 用途 |
|---|---|---|
| `SKILL.md`、`scripts/`、`references/`、`examples/` | 主仓 | 免费版源码，也是专业版底座 |
| `README.md` | 主仓 | Lite 用户入口，进安装包 |
| `DEVELOPMENT.md` | 主仓 | 维护文档，不进安装包 |
| `docs/` | 主仓 | 产品页与案例页源（GitHub Pages） |
| `materials/` | 主仓 | 货架物料，不进安装包 |
| `edition/` | 独立本地仓 | 专业版增量与构建材料，无公开远程 |
| `roadmap/` | 独立本地仓 | 规划与验收结论，无公开远程 |
| `services/skillhub-402/` | 独立私有仓 | 402 服务与 SkillHub 按次客户端 |
| `dist/` | 不版控 | `dist/<channel>/` 发布视图；`dist/<version>/` 只作临时构建留档 |

组织标准见 `~/.user-agents/standards/huiyonghkw/skills/skill-structure.md`，本仓特例见 [`STRUCTURE.md`](STRUCTURE.md)。

## 开发命令

```bash
# 作者工具 + 用户脚本自检；改 scripts/*.py 后必跑
for f in scripts/*.py; do python3 "$f" --selftest || exit 1; done

# 包括专业版脚本
for f in edition/scripts/*.py; do python3 "$f" --selftest || exit 1; done

# 升级写作技能版本 / 校验标准布局的 4 个版本点
python3 scripts/bump_version.py <version>
python3 scripts/bump_version.py --check

# 构建 Lite 与专业版渠道包
python3 scripts/build_lite_package.py
python3 scripts/build_paid_package.py --out "dist/skillpay/hekouwang-writer-skill-$(cat edition/VERSION)-paid.zip"

# 最终产物、链接、数量、版本与发布副本验收（包含官网 docs_check）
python3 tools/release_check.py --check

# 单独验收官网 / 修改演示输入后重建实证 JSON
python3 tools/docs_check.py
python3 tools/build_demo_evidence.py

# 按次服务端与客户端
python3 -m unittest discover -s services/skillhub-402/tests
(cd services/skillhub-402/client && node --test)

# 改过页面文案后重建字体子集
bash scripts/subset-fonts.sh

# 本地预览产品页
python3 -m http.server 8788 --directory docs
```

无第三方依赖，也不需要单独的 lint/test 框架。写作脚本的测试是内置 `--selftest`；按次服务使用 Python `unittest` 与 Node `node:test`。

## 构建边界

- `build_lite_package.py` 按白名单打包根 `README.md`、`SKILL.md`、许可、变更记录、`_meta.json` 清单和示例。
- `build_paid_package.py` 先拷 Lite 底座，再叠加 `edition/`，替换名称、描述、README 与许可，删除 `lite-only` 段落。
- `.clawhubignore` 排除维护文档、产品页、货架物料、作者工具、`edition/`、`roadmap/`、`services/` 和 `dist/`。
- `tools/release_check.py` 动态读取当前版本，重新构建两个写作包，在解压目录运行自检，检查最终包链接与渠道副本内容哈希。

## CI 与行为验收

- 公开仓 `.github/workflows/lite.yml` 运行 `release_check.py --lite`，不假设 `edition/` 存在。
- 按次服务私有仓 `.github/workflows/service.yml` 安装锁定依赖，运行服务端与客户端测试，再构建镜像并做 smoke test。
- 完整开发仓或私有 runner 运行 `bash tools/ci_all.sh`，其中全量产物检查使用 `--skip-channel`，干净 CI 不依赖本地 `dist/`。
- `evals/agent-behavior.json` 是 12 个真实宿主行为用例；`agent_behavior_check.py --selftest` 只验证用例与机械约束。实际发版还需按 `evals/README.md` 在目标宿主运行 prompt，并完成人工语义复核。
- `docs/compatibility.html` 只能根据真实宿主验收结果更新；本地脚本通过不等于宿主完整兼容，未完成项保留「待验收」。
- 官网交互只派发 `hkw:metric` 自定义事件，事件名来自 `data-metric` 或复制目标 id，不携带正文、不联网、不写本地统计。需要分析时由站点所有者另行接入隐私友好的监听端，不在页面里直接加第三方追踪。
- 官网无 JS 采用默认可见、`.js` 才启用动画的渐进增强；`docs_check.py` 负责链接、复制目标、对比度、JSON-LD、脚本语法、分享图和真实实证验收。

## 发版检查

1. 先看 [`RELEASE.md`](RELEASE.md)，区分源码版本、已打包版本、审核中版本和线上版本。
2. 写作技能升级运行 `bump_version.py`，不要手改各版本点；标准布局为 4 个，遗留 `public/` 两个仅在目录存在时兼容检查。
3. 专业版能力变化先改 [`listing-skillpay.md`](listing-skillpay.md)，再改平台商品描述。
4. 构建 Lite、Pro 和按次客户端的新版本包，不覆盖已发布版本。
5. 运行 `tools/release_check.py --check` 与按次服务全部测试；页面文案改动后运行字体子集脚本。
6. 对外推送、上传、提审和真实支付验收均需本人明确确认；完成后回读平台并更新 `RELEASE.md`。

## 文档指针

| 文件 | 用途 |
|---|---|
| [`RELEASE.md`](RELEASE.md) | 产品、版本状态、渠道矩阵与发版规则 |
| [`STRUCTURE.md`](STRUCTURE.md) | 目录结构、命名与推送边界 |
| [`AGENTS.md`](AGENTS.md) | 改本仓库时的规则 |
| [`listing-skillpay.md`](listing-skillpay.md) | 支付宝商品文案副本 |
| [`CHANGELOG.md`](CHANGELOG.md) | 免费版与专业版变更记录 |
| [`services/skillhub-402/README.md`](services/skillhub-402/README.md) | 按次服务部署、检查和故障恢复 |

## 许可

- 免费版：MIT-0，可用、可改、可商用、可再分发。
- 专业版：Proprietary，个人使用，不可转售或再分发。
- 更早版本的许可说明见公开仓历史中的 `LEGACY-MIT-0.md`，已发出的副本继续适用。
