# Review — 阅读时的代码审视

阅读源码时顺手做轻量 review,产物**统一落 `log.md`**(不开新存储)。这是 SKILL 决策流程里的 **path E**。

## 核心原则

- **不修改代码**。review 是 read-only。
- **不擅自落库**。产出"候选 finding 清单",用户拍板挑哪几条进 log。
- **不擅自决定范围**。范围必须用户显式给。
- **不重复扫**。开扫前先读 [`review-state.md`](#review-state-跟踪本地库) 跳过未改动文件。

## 路径 E 流程

```
1. 接收用户范围声明     ──> 模糊就反问,不许猜
2. 读 .experience/review-state.md ──> 跳过未变文件
3. 选模式:Quick / Deep
4. 按 rubric 扫描        ──> 产出 finding 列表(带 severity + 置信度)
5. 输出候选清单          ──> 用户挑 commit / discard / 详细问
6. 选中的写入 log.md 顶部 ──> 同类问题合并为 1 条多锚点 entry
7. 追加 review-session 标记 entry(防重复)
8. 更新 review-state.md
```

## 模式硬指标

| 维度 | Quick (E1) | Deep (E2) |
|------|-----------|-----------|
| 单次范围上限 | ≤ 5 文件 / ≤ 1500 行 | ≤ 2 文件 / ≤ 800 行 |
| 通读次数 | 1 遍 | ≥ 2 遍 + 跟引用 1-2 跳 |
| 跨文件追踪 | 不追 | 追 |
| 与文档对照 | 不对 | README / 注释 / commit msg 对照 |
| 产出 finding 数 | 5-15(广度) | 3-8(深度) |
| 置信度档 | high / medium / low 必标 | 只产出 high / medium |
| 适用场景 | 第一次接触 / 巡检 | 改动前评估 / 事故复盘 |

**超上限处理**:压缩范围(按模块/职责合并代表文件) + 告知用户"已压缩到 N 个文件,要全扫请走 Deep 分批"。**不允许悄悄超扫**。

**Quick → Deep 自动升级触发**:Quick 中出现一条 finding 同时满足"low confidence" + "touches main flow" → 当条 finding 不直接落候选,改为提示用户:"建议对 `<area>` 走 Deep 模式精读"。**不在 Quick 内擅自展开**。

## 严重度 severity(锁定 4 档)

| 档 | 标准 |
|----|------|
| `critical` | 阻断主流程 / 数据丢失 / 安全风险 |
| `high` | 主流程在特定条件下出问题 |
| `medium` | 边角场景影响 / 认知陷阱(用了会出错但需要凑巧) |
| `low` | 风格 / 极小概率 / 微优化(默认忽略) |

**默认行为**:Quick / Deep **默认不输出 low**。要输出 low → 用户在范围声明里显式说 `include-low`。
**bug / pitfall 类 entry 必填 `severity` 字段**(进 conventions §3)。`note` / `decision` 不要这个字段。

## rubric(锁定 4 维度,其他不看)

1. **正确性风险** — 边界条件、并发假设、错误处理缺口、空值/溢出
2. **认知陷阱** — 易误用 API、命名/文档与行为不符、隐式默认值
3. **架构观察** — 模块边界、调用方向、隐含依赖
4. **隐藏不变量** — 代码默认假设但没断言/没文档化的前提

**不看**:风格、命名(除非误导)、micro-perf、测试覆盖率。这些交给 reviewer agent。

## 用户的范围声明(必备字段)

接收 review 请求时,要确认这 3 件事,口径如下:

```
scope:    单文件 / 目录 / 调用链描述 / 模块名清单    必填,模糊一律反问,绝不猜
mode:     quick | deep                              缺省时直接采用 quick(向用户口头确认一句即可)
ignore:   low | none | <severity-list>              缺省时直接采用 ignore=low
```

可选 hint:`focus: 正确性 | 认知陷阱 | 架构 | 不变量`(只想看某一维度)。

**统一口径**:**只有 `scope` 是硬反问字段**;`mode` / `ignore` 用默认值并在回复里告诉用户"已采用 mode=quick / ignore=low,要改请说"。这避免对用户三连问。

## 候选 finding 输出格式

```
## Review Findings — <scope> · <mode>, <pass-count> pass

| # | 位置                       | 维度       | severity | 置信度 | 一句话                        | 建议 type |
|---|----------------------------|-----------|----------|-------|-------------------------------|----------|
| 1 | aof.c:1342 / rewriteAppend | 正确性    | high     | high  | fork 失败时 errno 未传播      | bug      |
| 2 | aof.c:892  / rewriteRead   | 认知陷阱  | medium   | medium| 函数名暗示同步,实际异步      | pitfall  |
| 3 | aof.c:430                  | 架构观察  | —        | high  | 隐式依赖 server.lua_caller    | note     |

请回:1,3 / all / none / 详细问 #2 / promote #2 to deep
```

**同一类问题合并**:同一 type+severity+维度,涉及多个位置 → 合并为 **1 条多锚点 entry**(详见 conventions §3 anchor 格式扩展),**不**写多条。

候选展示时如果触及 ≥ 3 个组件关系 / 状态流转 / 时序 → 配一张 mermaid 图。

## review-session 标记 entry(用户拍板后追加)

每次 review 在用户挑完候选后,**额外**追加 1 条 type=note 的 session entry,记录覆盖面:

```
## 2026-04-28-review-aof-quick
type: note
version: redis@7.2.4
status: active
anchor: src/aof.c:rewriteAppendOnlyFile, src/aof-defrag.c:defragKey
last_verified: 2026-04-28
tags: review-session, quick

- scope:    src/aof.c, src/aof-defrag.c
- mode:     quick
- commit:   7a9f3d2
- findings: 2 committed (#1, #3 → ids 2026-04-28-redis-aof-fork-errno, 2026-04-28-redis-aof-script-coupling), 1 discarded, 1 promoted to deep
- ignored:  low (default)
```

## review-state 跟踪(本地库)

`.experience/review-state.md` 是一个 grep-able 的单文件本地索引(纯 markdown,无二进制)。每次 review 完更新对应区块。**开扫前先读它,跳过 commit 未变的文件**。

格式:每文件/目录一段,如:

```
## src/aof.c
- last_reviewed: 2026-04-28
- last_commit:   7a9f3d2
- mode:          quick
- findings:      2 (id-1, id-2)

## src/cluster/
- last_reviewed: 2026-03-15
- last_commit:   3c1ab9d
- mode:          deep
- findings:      5
```

**加速规则**:开扫时对每个目标文件,如果 `git log -1 --format=%H -- <file>` 等于 `last_commit`,**跳过该文件**,但仍把该文件列入本次 session 的 scope(说明已检查过、未变)。

骨架:[`templates/review-state.template.md`](templates/review-state.template.md)。

## 编辑代码后的反向触发(防止经验失效)

非 review 路径里(用户改代码后),如果编辑触及任何 active `bug` / `pitfall` entry 的 anchor 文件:

1. 编辑完后,**用 grep 找该文件相关的所有 active entries**
2. 逐条提示用户:"这条 entry 的 anchor 在你刚改的文件里,是否更新 status?"
3. 用户选:`fixed`(已修复) / `stale`(已不适用) / 跳过
4. 不擅自改 status

这条规则也写进 SKILL.md 的"全局规则"区。

## Done Contract(每次 review 收尾必须输出)

候选拍板完成、entry 写入 log.md 之后,**在最终回复末尾固定输出六段**。这是 path E 的硬性收尾,缺则视为未完成:

```
## Review Done Contract

1. Committed       : <写入 log.md 的 entry id 列表;无则写 "(none)">
2. AGENT.md        : <updated / not touched>
3. review-state.md : <updated for: <file 列表 + commit hash>>
4. Coverage        : <本次 scope 内已扫文件 / 跳过(未变)文件 / 升级到 Deep 的区域>
5. Uncovered risks : <本次 review 没覆盖但建议后续做的方向;无则写 "(none)">
6. Next            : <integrate / Deep follow-up <area> / 整理 / 不需要后续>
```

作用:
- 让用户一眼看清"这次 review 实际产出了什么、改动了哪些文件、还有什么没做"
- 防止 review 收尾松散("好像扫完了但说不清做了什么")
- 给整理路径(C)提供后续触发依据
- 与 review-session 标记 entry 一起,构成可追溯的 review 历史

**不允许**:省略任何一段;用"看代码就知道"代替具体 id 列表;把"无"留空(必须显式写 "(none)")。

## 反模式

- ❌ AI 自己决定 review 范围("我看一眼整个项目")
- ❌ Quick 模式里悄悄展开成 Deep
- ❌ 输出 low severity 但没 `include-low`
- ❌ 同类问题写 N 条 entry,不合并多锚点
- ❌ review 完不写 session 标记 entry → 下次重复扫
- ❌ review-state.md 不更新 → 跳过逻辑失效
- ❌ 输出 finding 但不标置信度
