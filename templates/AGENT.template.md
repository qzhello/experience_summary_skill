<!--
  这是 AGENT.template.md 通用骨架。AI 首读入口 + 人类导航页。
  所有具体类别的预设(source-read/source-fork/application/tool)都基于这个骨架,只调"高频入口"和"active 精选"的分组重点。
  硬上限 ~150 行。超过 = 该走整理路径。
  log.md 是 source of truth,本文件是衍生视图。漂移以 log.md 为准。
-->

# <项目名> · 经验目录

> 这里是 AI 与人共同的入口。详细规则见仓库的 `experience-summary` skill 的 `conventions.md`。
> 本目录存储一律遵循:**log.md 是 source of truth,本文件可重建**。

---

## 1. 项目快照

- **一句话定位**: <TBD>
- **技术栈**: <TBD,如 Java 17 / Spring Boot 3.x / PostgreSQL 15>
- **入口文件**: <TBD,如 `src/main/.../Application.java`>
- **次要总结**(最多 3 条,溢出降级为 log 的 type=note):
  - <TBD>

## 2. 适用版本 / 分支

- **当前版本**: <TBD,如 `internal-app@2026-04` 或 `redis@7.2.4`>
- **跟踪分支**: <TBD,如 `main` / `release/2.x`>
- **历史范围**: 本经验目录覆盖 <起始日期> 至今的认知

## 3. 高频入口

> 最常被问到、最容易踩、最值得先看的位置。每条 ≤ 1 行 + 一个文件锚点。

- <主流程入口>: `path/to/file.ext:line`
- <最容易出问题的配置>: `path/to/config.ext:line`
- <核心数据结构定义>: `path/to/file.ext:line`

## 4. 当前 active 条目精选

> 只链 `status: active` 的 entry。**绝不链 stale / fixed / archived**。
> 按 type 分组。每条只写 id 与一句话标题。详细看 [`log.md`](log.md)。

### bug
- [`<id>`](log.md#<id>) — <一句话>

### pitfall
- [`<id>`](log.md#<id>) — <一句话>

### decision
- [`<id>`](log.md#<id>) — <一句话>

### note
- [`<id>`](log.md#<id>) — <一句话>

## 5. 录入规则(本仓库精简提示卡)

- 记新经验:在 `log.md` **顶部**追加,格式照 `conventions.md` §1。**不要改已有 entry 的正文**。
- 修正旧结论:写新 entry,`supersedes: <old-id>`,旧条目 `status` 改 `stale` 或 `fixed`。
- 必填字段:`id` `type` `version` `status` `last_verified`;`bug`/`pitfall` 还需 `anchor`。
- type 只能 4 选 1:`bug` / `pitfall` / `decision` / `note`。`risk` 是 tag,不是 type。
- 展开超 5 行 → 写 `details/<id>.md`,log 里只留链接。
- 本 AGENT.md 触达 ~150 行 → 走整理路径,不要继续往里塞。

完整规则见 skill 的 `conventions.md`。
