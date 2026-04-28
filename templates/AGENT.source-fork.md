<!--
  source-fork 预设:fork 上游 + 二开补丁 / 定制版。
  导航重点:改动点清单 / 兼容性风险 / 与上游 diff / 升级痛点。
  log.md 高频 type:decision(改造选型) / bug(改造引入故障) / pitfall(兼容性陷阱)。
-->

# <项目名> · 源码改造经验

> AI 首读入口。本目录遵循:log.md 是 source of truth,本文件可重建。

---

## 1. 项目快照

- **一句话定位**: <TBD,如 "fork 自 Redis 7.2,新增 XX 命令支持 YY 业务">
- **上游基线**: <TBD,如 `upstream redis@7.2.4`>
- **当前版本**: <TBD,如 `our-fork@2026.04>`
- **改造范围一句话**: <TBD>

## 2. 适用版本 / 分支

- **fork 分支**: <TBD,如 `release/our-2.x`>
- **上游 sync 频率**: <TBD,如 "每季度 rebase upstream/7.2">
- **最近 sync 时间**: <TBD>

## 3. 改动点速查

> 我们改了哪、动了什么。每条带文件锚点。

- <改动 1>: `<file>:<line>` — <一句话改了什么>
- <改动 2>: `<file>:<line>` — <一句话>
- <补充>

## 4. 当前 active 条目精选

> 只链 `status: active`。

### decision(为什么这么改 / 拒绝过哪些方案)
- [`<id>`](log.md#<id>) — <一句话>

### bug(改造引入或暴露的故障)
- [`<id>`](log.md#<id>) — <一句话>

### pitfall(与上游兼容性陷阱、升级时踩的坑)
- [`<id>`](log.md#<id>) — <一句话>

### note(架构理解 / 与上游差异点)
- [`<id>`](log.md#<id>) — <一句话>

## 5. 录入规则

- **每个改动点**应该至少有一条 `decision` entry,含 `alternatives:` + `rationale:`。
- 升级 / rebase 上游遇到的冲突,沉淀为 `pitfall`,带 `tags: upgrade`。
- `version` 同时标注本 fork 版本与对应上游版本,例如 `our-fork@2026.04 / upstream redis@7.2.4`。
- "这块以后升级要小心" → 给对应 entry 加 `tags: risk, upgrade`。
- 其余规则见 skill 的 `conventions.md`。
