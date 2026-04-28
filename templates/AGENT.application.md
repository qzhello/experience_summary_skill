<!--
  application 预设:公司内部业务系统、SaaS、网站、APP 后端等。也是 categories 判不准时的兜底。
  导航重点:业务入口 / 上下游依赖 / 配置项 / 线上事故。
  log.md 高频 type:bug(线上故障) / pitfall(配置/依赖陷阱)。
-->

# <项目名> · 应用项目经验

> AI 首读入口。本目录遵循:log.md 是 source of truth,本文件可重建。

---

## 1. 项目快照

- **一句话定位**: <TBD,如 "订单服务,承接 C 端下单与支付回调">
- **技术栈**: <TBD>
- **入口**: <TBD,主入口文件>
- **运行环境**: <TBD,如 K8s / VM / Serverless>

## 2. 适用版本 / 分支

- **当前版本**: <TBD,如 `internal-app@2026-04`>
- **跟踪分支**: <TBD,如 `main` 持续部署>
- **关键依赖版本**: <TBD,如 "MySQL 8.0 / Redis 7.0 / Kafka 3.5">

## 3. 业务入口与依赖速查

> 最常被排查、最容易出问题的位置。

- 主业务流程入口: `<file>:<line>`
- 关键配置文件: `<file>:<line>`
- 上游依赖(我们调谁): <TBD>
- 下游消费者(谁调我们): <TBD>
- 关键定时任务 / 消费者: `<file>:<line>`

## 4. 当前 active 条目精选

> 只链 `status: active`。

### bug(线上 / 测试已发生过的事故)
- [`<id>`](log.md#<id>) — <一句话>

### pitfall(配置 / 部署 / 依赖使用陷阱)
- [`<id>`](log.md#<id>) — <一句话>

### decision(技术选型、架构权衡)
- [`<id>`](log.md#<id>) — <一句话>

### note(架构认知、性能观察、容量边界)
- [`<id>`](log.md#<id>) — <一句话>

## 5. 录入规则

- 线上事故 → `type: bug`,`anchor` 指向问题代码,正文 trigger/cause/fix 一句话各一条,完整复盘进 `details/<id>.md`。
- "这块代码以后改要小心" → 在已有 entry 加 `tags: risk`,**不**单开一条。
- 配置项陷阱 → `pitfall`,`anchor` 指向配置文件具体行。
- `version` 用 `<app-name>@YYYY-MM` 或 git tag,不要省略。
- 其余规则见 skill 的 `conventions.md`。
