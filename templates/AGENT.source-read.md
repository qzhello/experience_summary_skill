<!--
  source-read 预设:阅读外部源码项目(Redis / ES / MySQL / Kafka / Linux / React 源码学习)。
  导航重点:主链路、模块边界、关键算法、调用图。
  log.md 高频 type:note(架构理解) / decision(理解作者的设计选择)。
-->

# <项目名> · 源码阅读经验

> AI 首读入口。本目录遵循:log.md 是 source of truth,本文件可重建。

---

## 1. 项目快照

- **一句话定位**: <TBD,如 "Redis 7.x 网络与命令执行主链路阅读笔记">
- **上游版本**: <TBD,如 `redis@7.2.4` / commit hash>
- **阅读切片**: <TBD,如 "网络层 + 命令分发,不含集群与 RDB">
- **入口文件**: <TBD,如 `src/server.c:main`>

## 2. 适用版本 / 分支

- **跟踪版本**: <TBD>
- **不适用范围**: <TBD,如 "本笔记不适用 6.x 及之前">

## 3. 主链路速查

> 最值得先看的调用链 / 模块入口。

- 启动主流程: `<file>:<line>`
- 事件循环核心: `<file>:<line>`
- 命令分发: `<file>:<line>`
- 关键数据结构: `<file>:<line>`
- <补充>

## 4. 当前 active 条目精选

> 只链 `status: active`。

### note(架构 / 模块边界 / 算法)
- [`<id>`](log.md#<id>) — <一句话>

### decision(作者的设计选择,理解后记录)
- [`<id>`](log.md#<id>) — <一句话>

### pitfall(读源码踩的坑、文档与代码不一致等)
- [`<id>`](log.md#<id>) — <一句话>

### bug(罕见,通常是发现的上游真实 bug)
- [`<id>`](log.md#<id>) — <一句话>

## 5. 录入规则

- 阅读型项目重点用 `note`(架构认知)与 `decision`(理解作者权衡),少用 `bug`。
- `version` 必须精确到 commit 或 patch 版本,源码经验离开版本就是噪声。
- 锚点指向上游源码路径,行号会随版本漂移 → 整理路径定期校验。
- 其余规则见 skill 的 `conventions.md`。
