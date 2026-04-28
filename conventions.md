# Conventions

写入 `.experience/log.md` 与 `AGENT.md` 之前必读。规则全部硬性,违反 = 阻断。

## 1. Entry schema(唯一格式)

每条 entry 在 `log.md` 中以 `## ` 开头。**不允许使用 `---` YAML 分隔符**,所有元数据是纯文本 `key: value` 行。

字段顺序固定如下(按 type 不同字段集略有差异,见 §3 / §3.2 / §6):
`type → version → status → [severity] → anchor → last_verified → supersedes → tags → 空行 → 正文`

**示例 — bug / pitfall(`severity` 必填)**:

```markdown
## 2026-04-28-redis-aof-rewrite-fork
type: bug
version: redis@7.2.4
status: active
severity: high
anchor: src/aof.c:rewriteAppendOnlyFile
last_verified: 2026-04-28
supersedes:
tags: aof, rewrite, fork

- trigger: <一句话:什么场景下出现>
- cause:   <一句话:根因>
- fix:     <一句话:解法>
- details: [details/2026-04-28-redis-aof-rewrite-fork.md](details/2026-04-28-redis-aof-rewrite-fork.md)
```

**示例 — decision(无 `severity`,正文必须含 `alternatives:` + `rationale:`)**:

```markdown
## 2026-04-28-pick-redis-over-memcached
type: decision
version: internal-app@2026-04
status: active
anchor:
last_verified: 2026-04-28
supersedes:
tags: cache, selection

- context:      需要支持排行榜与分布式锁
- alternatives: Memcached(无 sorted set);自研内存层(成本过高)
- rationale:    Redis 数据结构覆盖两个场景且团队已有运维经验
```

**示例 — note(无 `severity`)**:

```markdown
## 2026-04-28-aof-fsync-policy
type: note
version: redis@7.2.4
status: active
anchor: src/aof.c:flushAppendOnlyFile
last_verified: 2026-04-28
supersedes:
tags: aof, fsync

- everysec 策略下 fsync 由后台线程做,主线程仅入队;高负载时存在最长 ~2s 数据风险窗口。
```

`details:` 行仅当展开超过 5 行时出现。完整字段规则见 §3。

## 2. id 与 slug

格式 `YYYY-MM-DD-<slug>`。
- `slug` 只允许 `[a-z0-9-]`,中文/大写字母走 `tags`,不进 id
- **全仓库唯一**。同日同主题的次条加 `-2`、`-3` 后缀,例如 `2026-04-28-redis-aof-rewrite-fork-2`
- 一旦写下,**永不重命名**;要"修正" → 写新 entry + supersedes 旧 id

## 3. 字段规约

| 字段 | 必填 | 规则 |
|------|------|------|
| `type` | 是 | `bug` / `pitfall` / `decision` / `note` 四选一 |
| `version` | 是 | 见 §4。允许模糊,**不允许省略** |
| `status` | 是 | `active` / `stale` / `fixed`。流转见 §5 |
| `anchor` | bug/pitfall **必填**;decision/note 可空 | 格式见 §3.1,支持精确行 / 符号锚 / 多锚点 |
| `severity` | bug/pitfall **必填**;decision/note **不允许有** | `critical` / `high` / `medium` / `low` |
| `last_verified` | 是 | `YYYY-MM-DD`,锚点最后一次确认匹配的日期 |
| `supersedes` | 否 | 旧 entry 的 id;空就留空字符串,不要删字段 |
| `tags` | 否 | 逗号分隔,可中文 |

## 3.1 anchor 格式(支持 3 种)

```
path/to/file.ext:42                          精确行号
path/to/file.ext:methodName                  符号锚(抗代码漂移,推荐)
path/to/file.ext:m1, path/other.ext:m2       多锚点(同一类问题多处)
```

- **多锚点上限 3 处**。超过 3 处 → 主锚点放 `anchor`,其余下沉 `details/<id>.md` 列出
- 优先用**符号锚**(方法名/函数名),行号会随版本漂
- 同一类问题(同 type + 同 severity + 同维度)合并为 1 条多锚点 entry,**禁止**写多条

## 3.2 severity(bug / pitfall 必填)

| 档 | 标准 |
|----|------|
| `critical` | 阻断主流程 / 数据丢失 / 安全风险 |
| `high` | 主流程在特定条件下出问题 |
| `medium` | 边角场景影响 / 认知陷阱 |
| `low` | 风格 / 极小概率 / 微优化(默认 review 不输出,人工记可以) |

## 4. version 格式

显式允许模糊,**省略硬阻断**:

```
redis@7.2.4              精确版本
redis@7.2.x              次版本范围
redis@>=7.0,<8.0         范围
internal-app@2026-04     内部项目按月份
unknown                  显式未知(允许,但每季度整理时会被提示回填)
```

## 5. status 流转(单向)

```
active ──┬──> stale     认知更新/版本失效;被新 entry supersede 时由旧条目转入
         └──> fixed     已修复(仅 bug 类)

stale | fixed ──> archived   整理路径搬到 details/archive/,从 log 删除
```

**禁止回流**:`stale` 不能回 `active`;`fixed` 不能回 `active`。
要让一个失效结论重新生效 → **写新 entry**,supersede 那条 stale。

## 6. type 收敛与最小字段

| type | 描述 | 额外要求 |
|------|------|---------|
| `bug` | 已发生的故障/回归 | `anchor` 必填;trigger/cause/fix 三段不可省 |
| `pitfall` | 认知误区、用法陷阱 | `anchor` 必填;trigger/cause/fix 三段不可省 |
| `decision` | 选型/改造/tradeoff 的选择 | 正文必须含 `alternatives:`(至少 1 个被拒方案) + `rationale:`;不满足则降级为 `note` |
| `note` | 架构认知、关键功能锚点、性能观察等 | 正文一段一句话即可;`anchor` 推荐填 |

**`risk` 不是 type**,是 `tags` 标签:任何 `bug` 或 `note` 都可以打 `risk` 标签提醒"这块改动要小心"。

**"一句话总结"不进 log**:它属于 AGENT.md "项目快照"。项目快照里**最多 1 条核心定位 + 3 条次要总结**,溢出的内容必须降级为 type=note 进 log。

## 7. log.md 不可变规则

`log.md` 是 source of truth。已存在 entry 的:

- ✅ 允许修改:`status`、`last_verified`、`supersedes` 三个字段
- ❌ 禁止修改:正文、其他元数据字段、id、type、version、anchor

要"修正一条经验" → 写新 entry,`supersedes: <old-id>`,旧条目状态切 `stale`/`fixed`。

**归档不是删除事实**。在整理路径里,`status` 为 `stale`/`fixed` 且 `version` 字段**不等于当前项目版本**(纯字符串比较,V1 不做范围/顺序推理 —— 详见 scripts-contract §Version + §archive candidates)时,**整条从 log.md 搬入 `details/archive/<id>.md`**(完整保留 entry 全文,包括元数据与正文)。从 log.md 中移除该条 = 从"工作集"移除,不等于丢弃。归档后:
- 历史事实由 `details/archive/` 持有
- 工作集 SoT(`log.md`)只保留 active + 近期未归档历史
- 整个 `.experience/` 目录依然是完整 SoT(见 §8)

这是 log.md **唯一允许的"移除"场景**,仍然不是真删。

新条目**只在 log.md 顶部追加**(最新在上)。**不允许在中间插入**。

### git 合并冲突约定

两人/两 session 同时往顶部 append → merge 必冲突。约定:**保留全部条目**,按 id 时间戳重排(新的在上),不要二选一。

## 8. SoT 范围与文件职责

- **整个 `.experience/` 目录是 SoT**(包括 `log.md` + `details/archive/` + `review-state.md` + `.overrides.md`)
- `log.md` = **工作集 SoT**(active + 近期未归档历史)
- `details/archive/` = **历史事实持有**(归档 entry 完整保留)
- `AGENT.md` = **衍生视图**(导航 + 快照 + active 条目精选)
- `review-state.md` = **review 进度跟踪**(只 path E 写)

**漂移规则**:`AGENT.md` 与 `log.md` 不一致 → 以 `log.md` 为准;AGENT 出错就重新生成。**绝不反向改 log.md** 来"对齐"AGENT。

AGENT.md 硬上限 ~150 行。"active 条目精选"只链 `status: active` 的 id,**绝不链 stale/fixed/archived**。

## 9. 锚点校验

整理路径里逐条校验 `anchor`,执行方式:**用 Read 工具打开 anchor 指向的文件,确认行号附近内容仍与 entry 描述匹配**。这是手动校验,不是脚本。

校验结果:
- 仍匹配 → 更新 `last_verified` 为今天
- 文件存在但行号漂了 → 更新 `anchor` 行号 + `last_verified`
- 文件/内容找不到 → `status` 切 `stale`,在条目末尾追加一行 `- note: anchor lost on YYYY-MM-DD`(这是允许的"末尾追加",不算正文修改)

## 10. details/ 写作守则

不是所有"超过 5 行"的内容都该进 details。判断标准:**下次还会被打开吗?**

- ✅ 应该进 details:复现步骤、调用栈节选、关键代码片段、推导过程、对比表
- ❌ 不该进 details:聊天记录式叙述、可以浓缩成一句话的废话、与 anchor 重复的代码大段粘贴

如果写完发现 details 没有信息密度 → 删掉,把核心一行写回 log 的 trigger/cause/fix。

## 11. `.overrides.md` 项目级覆盖机制

位置:`.experience/.overrides.md`(可选,不存在则纯按通用规则)。

**允许覆盖的范围**:
- 项目专属 `tags` 词表(规范化命名)
- AGENT.md 五块的强调点 / 排序
- review rubric 增减(本项目要不要看并发安全等)
- review 默认 `ignore` severity 阈值
- 高频入口模板的本项目化变体

**禁止覆盖的核心不变量**:
- entry schema(§1)
- 字段必填规则(§3 / §3.1 / §3.2)
- status 单向流转(§5)
- type 收敛 4 选 1(§6)
- log.md 不可变规则(§7)
- log = SoT,AGENT = 衍生视图(§8)

**进化触发**:同一种模式(写法、tag、判定问题)在追加路径里**重复出现 ≥ 3 次**,但 conventions.md 没覆盖 → AI 在回复尾部建议:"考虑在 `.overrides.md` 加一条本项目专属规约"。**AI 不擅自写 overrides**,由用户拍。

每条 path(B/C/E)开始执行前,**先读** `.overrides.md`(若存在),按它覆盖本文件的规则。

## 12. 编辑代码时的反向触发

非 review 路径里编辑代码后,如果触及 active `bug` / `pitfall` entry 的 `anchor` 文件:

1. 编辑完后用 grep 找该文件相关的所有 active entries
2. 逐条提示用户:"这条 entry 的 anchor 在你刚改的文件里,是否更新 status?"
3. 用户拍:`fixed` / `stale` / 跳过
4. AI **不擅自**改 status

避免经验在代码演进里悄悄过时。

## 13. 自我怀疑与认错(输出层规约)

- 不确定的结论必须显式标 `(low confidence)` / `(uncertain)` / `<TBD>`,**不允许装作肯定**
- 任何判断如果建立在某个未验证假设之上 → 显式写"假设 X 成立时,…;若 X 不成立则结论失效"
- 用户指出错误时:**先承认、再修正**,不狡辩、不找补
- 自己事后发现写错的旧 entry → 走"新 entry + supersedes 旧 id + 旧条目改 stale"流程,**不偷偷改正文**

## 14. 反模式(整理时遇到必须修)

- 一条经验同时挂多个 type
- entry 用 `---` YAML 分隔符
- AGENT.md 链了 stale 条目
- log.md 里有空 version 字段
- decision 没有 alternatives
- 多条 entry 共用同一 id
- 锚点是 `path/to/file`(没有 `:line`)
