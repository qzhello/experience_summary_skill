---
name: experience-summary
description: Use when the user asks to set up, append to, curate, or read a per-project experience log under .experience/. Triggers on phrases like 初始化经验目录 / 沉淀经验 / 记一条踩坑 / 记一条 BUG / 看下这个项目踩过什么坑 / 整理经验.
---

# Experience Summary Skill

为当前项目维护 `.experience/` 经验沉淀目录。组织单位是**条目(entry)**,不是文件。

```
.experience/
├── AGENT.md      # AI 首读入口 + 人类导航页,~150 行硬上限
├── log.md        # 标准化条目流,顶部追加,正文不可改
└── details/      # 仅当 entry 需要展开时建文件
    └── archive/  # stale/fixed 满阈值后归档
```

**核心不变量**:
- **整个 `.experience/` 目录是 source of truth**(包括 `log.md` + `details/archive/` + `review-state.md`)。
  - `log.md` 是**当前工作集**(active + 尚未归档的近期历史)的 SoT。
  - `details/archive/` 持有归档历史事实,**归档不是删除事实**,只是从工作集搬到长期存档。
  - `AGENT.md` 是**衍生视图**,与 `log.md` 不一致时以 `log.md` 为准,**绝不反向改 log.md 来"对齐"AGENT**。
- 每个用户请求**只触发一条路径**(A / B / C / D / E),不要混合执行。
- 本 skill 处理**单个项目**的经验沉淀,**不处理跨项目共享**。同一坑在多个项目都遇到 → 在每个项目各自记一条,靠 AI 检索多个 `.experience/` 串联。

**写入前必读** [`conventions.md`](conventions.md) —— entry schema、version 格式、不可变规则都在那里。
**判定项目类别** 用 [`categories.md`](categories.md) —— 决定拷哪份 AGENT.md 模板。

## 决策流程

按用户意图选一条路径,**不要混合**:

| 用户意图 | 路径 |
|---------|------|
| 初始化 / 第一次建 | [A. 初始化](#a-初始化) |
| 记一条经验 | [B. 追加](#b-追加) |
| 整理 / 校验 / 归档 | [C. 整理](#c-整理) |
| 查阅 | [D. 阅读](#d-阅读) |
| review 代码 | [E. Review](#e-review)(详见 [`review.md`](review.md)) |

**任何路径开始执行前**:若 `.experience/.overrides.md` 存在,**先读它**,按它覆盖通用规则(只在 conventions §11 允许的覆盖范围内)。

---

## A. 初始化

0. **Restate First & 类别判定**(批量确认,per G4 — 在任何文件操作之前):
   一次性给用户(模板,缺省值用 `<>` 标):
   ```
   我理解的任务:为 <项目名(从 cwd 或用户消息推断)> 建立 .experience/ 目录。
   类别判定:<source-read | source-fork | application | tool>
   理由:<一句话:看到 README / package.json / 目录结构里的什么信号>
   不确定时,候选:<列 2-3 个>。
   后续动作:从 templates/ 拷 4 文件 + 建 2 目录,只用 README/构建文件/入口推断快照,业务逻辑一律 <TBD>。
   确认?(yes / 改为 X / 选候选 #N)
   ```
   **类别绝不允许猜**。判不准就给候选让用户选,不要走到 step 3 才发现错。
   用户确认前不动任何文件。

1. 检查 `.experience/` 是否已存在 → **存在则切到 C**,禁止覆盖
2. 创建目录,从 `templates/` 拷:
   - `templates/AGENT.<category>.md` → `.experience/AGENT.md`
   - `templates/log.template.md` → `.experience/log.md`
   - `templates/review-state.template.md` → `.experience/review-state.md`
   - 创建空 `details/` 与 `details/archive/`
   - `.experience/.overrides.md` **不**自动创建,按需才建
3. **填充硬边界(防幻觉)**:初始化只能从这些来源推断 AGENT.md 的"项目快照":
   - `README*` / `CHANGELOG*` / `docs/`
   - 构建文件(`package.json` / `pom.xml` / `go.mod` / `Cargo.toml` / `requirements.txt` / `CMakeLists.txt`)
   - 目录结构本身
   - 入口文件第一屏代码(`main.*` / `index.*` / `Application.*`)
   - 用户在对话中提供的信息

   **禁止**:扫描业务代码后编造"模块职责"、推测"设计意图"、复述未读源码的行为。
   不确定的字段一律写 `<TBD>`,留给用户后续补。

4. 完成后告诉用户:**"骨架已建。后续记经验请说'记一条…',我走追加路径。"**

---

## B. 追加

1. **判定 type**(单选):

   | 表征 | type |
   |------|------|
   | 已发生的故障 / 回归 | `bug` |
   | 认知误区 / 用法陷阱 | `pitfall` |
   | 做过的选择 + 理由(选型、改造、tradeoff) | `decision` |
   | 其他认知(架构、关键功能锚点、性能观察) | `note` |

   `risk` 不是 type,是 `tags` 里的标签。"一句话总结"不进 log,放 AGENT.md 项目快照。

2. **检查必填字段**(任一缺失则**阻断**,问用户):
   - `id`(`YYYY-MM-DD-<kebab-slug>`)
   - `type`、`version`、`status`、`last_verified`
   - `anchor`:`bug` / `pitfall` 必填;`decision` / `note` 可空
   - `severity`:`bug` / `pitfall` **必填**(`critical` / `high` / `medium` / `low` 之一);`decision` / `note` **不允许有**
   - `decision` 还需正文含 `alternatives:` + `rationale:`,缺则降级 `note`

   `version` 允许模糊但必须显式(`redis@7.2.x` / `unknown` 都行,**省略不行**)。

3. 按 `conventions.md` 的 entry 模板,在 `log.md` **顶部**追加。

4. 正文超过 5 行 → 在 `details/<id>.md` 写展开,log 里只留 `details:` 链接。

5. 如果是对旧条目的修正/更新:
   - 新 entry 写 `supersedes: <old-id>`
   - 找到旧 entry,**只改** `status` 字段为 `stale`(认知更新)或 `fixed`(已修复)
   - 旧 entry 正文一字不动
   - **status 单向流转**:`stale`/`fixed` **不能**改回 `active`。失效结论想重新生效 → 写新 entry supersede 那条 stale,不要改回。

6. 同步 AGENT.md 的"当前 active 条目精选":
   - 新 active 条目链上去
   - 被 supersede 掉的旧 id 摘掉(AGENT 只链 active)

7. **追加完成后的尾部检查**(强制):读一次 `log.md` 行数与 entry 数。命中以下任一阈值 → 在回复末尾**主动提示用户走整理路径**(不要自己擅自跑整理):
   - log.md 行数 > 300
   - entry 数 > 20
   - AGENT.md 行数 ≥ 140(接近 150 上限)

---

## C. 整理

每累计 ~20 条 / 用户主动要求 / AGENT.md 接近上限时:

1. **锚点校验**:**用 Read 工具逐条打开** `anchor: path:line` 指向的文件,确认行号附近内容仍与 entry 描述匹配。这是手动校验,不是脚本。
   - 仍匹配 → 更新 `last_verified` 为今天
   - 文件存在但行号漂了 → 更新 `anchor` 行号 + `last_verified`
   - 文件 / 内容找不到 → `status` 改 `stale`,在条目末尾追加一行 `- note: anchor lost on YYYY-MM-DD`(末尾追加是 conventions §9 允许的写法)

2. **状态批处理**:对每条 `status: stale` 或 `fixed` 的 entry,如果其 version 已超出当前项目使用版本范围 → 整条从 `log.md` **搬入** `details/archive/<id>.md`(完整保留 entry 全文)。这是从工作集移除,**不是丢弃事实** —— 历史由 archive 持有。详见 conventions §7、§8。

3. **AGENT.md 收敛**:
   - "active 条目精选"按 type 分组重排,把高频/高价值的前置
   - 行数仍超 150 → 把次要分组下沉成 `details/agent-<topic>.md` 链接

4. 整理结束后报告:校验了多少条、归档了多少条、AGENT.md 当前行数。

---

## D. 阅读

打开 `.experience/AGENT.md`,跟随其五块结构。具体细节按 AGENT.md 里的链接展开。**不要直接通读 log.md**,那是数据流,不是阅读视图。

---

## E. Review

阅读源码时顺手做轻量代码审视。**完整规则、流程、口径全部在** [`review.md`](review.md),本文件不重复叙述以避免双源漂移。

入门点(够你决定要不要进 review.md):
- 只 `scope` 硬反问;`mode` 默认 quick、`ignore` 默认 low
- 候选 finding 清单 → 用户拍板 → 才落 log.md
- 同类问题合并多锚点,不写多条
- 追加 `tags: review-session` 标记 entry,更新 `review-state.md`

---

## 全局规则(所有路径必守)

### G1. 编辑代码后反向触发

非 E 路径里编辑代码后,若触及 active `bug` / `pitfall` 的 `anchor` 文件 → grep 出相关 entries → 逐条提示用户更新 status (`fixed` / `stale` / 跳过)。AI **不擅自改**。详见 conventions §12。

### G2. 输出风格(给用户看的回复)

1. **结论先行**:第一行就是结论,不是过程独白
2. **表格 / 列表 > 段落**:枚举性内容必须表格化
3. **重要度排序**:不按时间序、不按文件序,按"用户最该先看"排
4. **一屏可读**:默认 ≤ 1 屏,展开放 details/ 或追加链接
5. **图表触发**(满足任一):
   - ≥ 3 个组件 / 调用关系 → mermaid graph
   - 状态流转 → mermaid stateDiagram
   - 时序交互 → mermaid sequenceDiagram
   - 数值对比 → 表格,不要图
6. **不写过程独白**:"我先看一下…然后…"全删
7. **置信度显式**:不确定的结论标 `(low confidence)` / `<TBD>`,不允许装作肯定
8. **错则认错**:用户指出错误,先承认再修正,不狡辩、不找补
9. **怀疑自己**:判断若依赖未验证假设,显式写"假设 X 成立时,…;否则结论失效"

### G3. 进化触发

同一模式(写法 / tag / 判定问题)在追加路径里重复 ≥ 3 次但 conventions 没覆盖 → 在回复尾部建议用户在 `.overrides.md` 加规约。AI **不擅自写 overrides**。

### G4. 批量确认 > 多轮反问

**任何路径**需要用户输入时,**一次性把所有待确认项列出来**,让用户简单回 yes / "改 #2" / "全部按默认",**绝不三连问**。

具体形态:

```
我准备这样做,确认吗?(回 yes / 改 #N / 全部默认)
1. <字段或决定>: <推断值或默认值>
2. <字段或决定>: <推断值或默认值>
3. ...
```

各路径的批量确认时机:

| 路径 | 一次性列出 |
|------|-----------|
| A 初始化 | 类别判定 + 项目快照推断字段(定位/技术栈/入口) + 是否首次扫描 |
| B 追加 | type / version / status / severity / anchor / tags 缺哪些一并列出 |
| C 整理 | 即将归档的 entry 清单 + 行数预估 + AGENT.md 重排预览 |
| E Review | scope(已问)+ mode 默认 + ignore 默认 + 是否含 `include-low` 一起报 |

**反例**:先问类别 → 再问技术栈 → 再问入口 → 再问要不要扫描。这是 4 轮交互,折磨用户,禁止。

**例外**:`scope` 在 E 路径里仍是硬反问字段(无法默认),其他都用默认 + 一次确认。

---

## 反模式

- ❌ 编辑 log.md 已存在 entry 的正文(只能改 status / last_verified / supersedes)
- ❌ 在 log.md 中间插入条目(只能顶部追加)
- ❌ git merge 冲突时二选一保留(应该按 id 时间戳重排,**保留全部**)
- ❌ 反向修改 log.md 来"对齐" AGENT.md(log 是 SoT,AGENT 错了重生成)
- ❌ 把 `stale` 或 `fixed` 改回 `active`(单向流转,要回流就写新 entry)
- ❌ 同一条经验同时写多个 type
- ❌ 省略 version 字段(模糊可以,缺失不行)
- ❌ AGENT.md 链接历史 / stale / fixed / archived 条目
- ❌ 把规则细节复制进 AGENT.md(规则只在 conventions.md)
- ❌ 初始化时凭目录名编造模块职责
- ❌ 试图引入跨项目共享机制(本 skill 不做,V1 边界)
- ❌ append 完不做尾部阈值检查(B 路径 step 7 是强制的)
- ❌ review 时 AI 自己决定范围 / 悄悄从 Quick 升 Deep / 输出 low 但用户没说 `include-low`
- ❌ review 同类问题写 N 条 entry 不合并多锚点
- ❌ 编辑代码触及 active bug 后不提示 status 更新
- ❌ 装作肯定 / 不认错 / 偷偷改旧 entry 正文来"修正"

## 引用文件

- [`conventions.md`](conventions.md) — entry schema、字段规约、不可变规则(**写入前必读**)
- [`categories.md`](categories.md) — 4 类项目判定
- [`templates/AGENT.template.md`](templates/AGENT.template.md) — 通用 AGENT.md 五块结构
- [`templates/AGENT.source-read.md`](templates/AGENT.source-read.md) — 源码阅读型预设
- [`templates/AGENT.source-fork.md`](templates/AGENT.source-fork.md) — 源码改造型预设
- [`templates/AGENT.application.md`](templates/AGENT.application.md) — 应用项目预设
- [`templates/AGENT.tool.md`](templates/AGENT.tool.md) — 工具/脚本项目预设
- [`templates/log.template.md`](templates/log.template.md) — log.md 初始骨架
- [`templates/review-state.template.md`](templates/review-state.template.md) — review 跟踪本地库骨架
- [`review.md`](review.md) — review 子功能完整规约(rubric / 模式 / severity / 候选流)
- [`validation.md`](validation.md) — 压力场景自检
- [`scripts/`](scripts/) — 可选加速器(详见下节)

## 脚本(可选加速器,不是判官)

`scripts/` 下提供 3 个纯只读 Python 脚本(stdlib only,Python 3.9+)。**非必需**,删了 skill 仍 work。

| 脚本 | 何时用 | 命令示例 |
|------|-------|---------|
| `validate.py` | 写完一批 entry 后 / C 整理路径前 | `python scripts/validate.py [--strict] [--root <path>]` |
| `query.py`    | D 阅读 / B 追加前查重 | `python scripts/query.py --status active --type bug --format table\|ids\|json` |
| `stats.py`    | C 整理路径决策时 / B 路径尾部检查替代手算 | `python scripts/stats.py [--stale-days N] [--agent-cap N]` |

**调用方式**:在项目根目录(含 `.experience/` 的目录)执行,或显式 `--root /path/to/project`。

**根定位行为**:不传 `--root` 时,脚本从 cwd 向上**找到第一个** `.experience/log.md` 就用它。
- monorepo 嵌套场景(子项目自己有 `.experience/`,父仓库也有)从子项目执行 → 命中子项目的(预期)
- 但若子项目**没建** `.experience/`,会**意外命中**父仓库的 → 不报错也不警告。
  防踩坑:在 monorepo 子项目里跑脚本,**显式传** `--root .` 或先 `cd` 到子项目根。

**核心边界(不要破)**:

- 脚本**只读**。不写 `log.md` / `AGENT.md` / `details/` / `review-state.md`。
- 脚本输出**不缓存**。不存 `.cache/`,每次现解析。
- 脚本只验证**格式与规则**,**不验证经验内容真伪**。`validate.py` 通过 ≠ 经验是对的。
- 所有写入仍走 AI + 用户拍板路径,脚本不替代人工判断和 AI 阅读。
- 锚点真伪校验(文件存在、行号准、符号在)仍是 C 整理路径里 AI 用 Read 工具手动做,脚本不做。

**反模式**:
- ❌ 把 `validate.py` 通过当成"经验质量保证"
- ❌ 让脚本去改 entry / 改 status / 自动归档
- ❌ 引入第三方 Python 依赖 / 引入 SQLite / 引入持久化缓存
- ❌ 跳过脚本设计的"现解析"原则,改成读缓存
