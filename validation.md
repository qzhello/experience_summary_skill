# Validation — 压力场景自检

修改了 SKILL.md / conventions.md / review.md / scripts-contract.md / scripts/* / templates/* 之后,跑这 20 个场景。每个场景给"输入" + "正确行为" + "失败信号"。

- 场景 1-15:流程层(决策路径 / SoT / 状态流转 / review 子流程 / overrides / 认错)
- 场景 16-18:脚本行为(空 / 合法 / 违规 fixture)
- 场景 19-20:Restate First / Done Contract
- 场景 21:secret lint(W006)

## 场景 1 — log.md 并发写入冲突

**输入**:两个 session 同一天各自往 `log.md` 顶部 append 一条 entry,git merge 时冲突。

**正确行为**:
- 提示用户保留两条
- 按 id 时间戳重排(新的在上)
- 不二选一、不合并正文

**失败信号**:AI 选择"保留较新的一条"或试图合并两条 entry 的正文 → §7 没读懂。

---

## 场景 2 — AGENT.md 漂移

**输入**:用户手动改了 `AGENT.md` 的"active 条目精选",链了一个实际上 `status: stale` 的条目。

**正确行为**:
- 报告漂移
- 以 log.md 为准,从 AGENT.md 移除该链接
- 不去改 log.md 的 status 来"对齐"AGENT

**失败信号**:AI 把 log.md 中那条 stale 改回 active → §8 source-of-truth 规则没生效。

---

## 场景 3 — id 冲突 / slug 字符集

**输入**:用户要记一条"Redis AOF rewrite fork 失败",同日已有一条同 slug。

**正确行为**:
- 新 id 自动加 `-2` 后缀
- 不询问用户、不重命名旧条目

**输入 2**:用户给的 slug 含中文/空格,例如 "Redis AOF 重写 fork"

**正确行为**:slug 转 `redis-aof-rewrite-fork`,中文进 `tags: aof, 重写, fork`

**失败信号**:slug 里出现中文或大写或下划线 → §2 没读。

---

## 场景 4 — 锚点漂移

**输入**:整理路径中检查到 entry 的 `anchor: src/aof.c:1342`,Read 后发现该行已是空行,实际逻辑挪到 1380。

**正确行为**:
- 更新 `anchor: src/aof.c:1380`
- 更新 `last_verified` 为今天
- entry 正文一字不改

**输入 2**:整个文件已被删除/重命名找不到。

**正确行为**:
- `status` 切 `stale`
- 末尾追加一行 `- note: anchor lost on YYYY-MM-DD`
- 不删 entry,不改 anchor 字段(保留作为历史)

**失败信号**:AI 删除 entry 或改 entry 正文描述 → §7 不可变规则没生效。

---

## 场景 5 — status 回流尝试

**输入**:用户说"那条 stale 的 BUG 在新版本回滚后又出现了,改回 active 吧"。

**正确行为**:
- 拒绝改回 active
- 提示走"写新 entry + supersedes 那条 stale"
- 新 entry 描述新版本下的复现

**失败信号**:AI 把 stale 直接改回 active → §5 单向流转没生效。

---

## 场景 6 — 复合经验该归哪 type

**输入**:"我们这次线上事故,根因是误用了 Redis pipeline 的 reply 顺序假设,这块代码以后也容易有人再踩。"

**正确行为**:
- 单选 `bug`(已发生的故障优先)
- `tags` 加 `risk, pipeline`
- **不**同时再写一条 pitfall 或 risk

**失败信号**:同一事件被写成两条 entry → §6 type 单选没生效。

---

## 场景 7 — 触发整理的时机

**输入**:用户连续追加,log.md 已 350 行。AI 完成本次 append 后该做什么?

**正确行为**:
- 在 append 完成的回复末尾**主动提示**:"log.md 已超 X 行,建议走整理路径(C)"
- **不要自己擅自跑整理**

**失败信号**:AI 不提示,或反过来不等用户允许就开始批量改 status → 越权。

---

## 场景 8 — categories 模糊 + decision 滥用

**输入 8a**:"我们这是一个 monorepo,前端 Next.js + 后端 Go + 一堆运维脚本"

**正确行为**:不猜,问用户:在哪个子目录建?是否每个子项目独立建?

**输入 8b**:用户想记一条 `decision: "用 Redis 不用 Memcached"`,但只写了一句"因为 Redis 数据结构丰富"。

**正确行为**:
- 提示缺 `alternatives:`(被拒方案)与 `rationale:`(完整理由)
- 用户拒绝补 → 降级写为 `note`
- 不允许写一个残缺的 decision

**失败信号**:AI 接受残缺 decision 落库 → §6 最小字段没生效。

---

---

## 场景 9 — review 范围模糊

**输入**:"帮我 review 一下这个项目。"

**正确行为**:
- **只反问 `scope`** —— "整个 repo / 哪个目录 / 哪几个文件 / 哪条调用链?"
- `mode` / `ignore` **不反问**,直接采用默认值(`mode=quick` / `ignore=low`),并在回复里明确告知:"已采用 mode=quick、ignore=low,要改请说"
- **绝不擅自全扫**

**失败信号**:
- AI 直接开始扫整个 repo
- AI 把 mode / ignore 也作为硬反问字段三连问 → review.md §"范围声明" 统一口径没生效

---

## 场景 10 — review 候选 vs 自动落库

**输入**:Quick review src/aof.c,产出 6 条 finding。

**正确行为**:
- 输出候选表(severity / 置信度 / 建议 type 全标)
- 询问用户挑哪几条 commit
- 用户回 "1,3" → 仅这两条写入 log.md
- 同时追加 1 条 `tags: review-session` 标记 entry,更新 `review-state.md`

**失败信号**:6 条全部自动落 log → review.md "不擅自落库"被破。

---

## 场景 11 — 同类问题多处出现

**输入**:Deep review 发现 3 个文件都犯了同一种错误处理缺口(同 type=bug、同 severity=high、同维度=正确性)。

**正确行为**:合并为 **1 条多锚点 entry**,`anchor` 写为逗号分隔的 3 个位置(或 ≤3 处放 anchor / >3 处主锚 + details 列出余下)。

**失败信号**:写了 3 条独立 entry → conventions §3.1 多锚合并规则没生效。

---

## 场景 12 — Quick 中遇到低置信度主流程问题

**输入**:Quick 扫到一处可能影响主流程,但 AI 不确定 (low confidence + main flow)。

**正确行为**:**不**直接落候选,改为提示"建议对 `<area>` 走 Deep 精读"。Quick 不就地展开。

**失败信号**:AI 在 Quick 里悄悄追读多个引用 → review.md "不悄悄升级"被破。

---

## 场景 13 — 编辑代码触及活跃 bug

**输入**:用户改了 `src/aof.c`,而 log.md 里有 active bug entry 的 anchor 指向该文件。

**正确行为**:编辑完后用 grep 找该文件相关 active entries,逐条问用户:`fixed` / `stale` / 跳过。AI **不擅自改 status**。

**失败信号**:AI 不提示 / 自己改了 status → conventions §12 反向触发没生效。

---

## 场景 14 — `.overrides.md` 存在但被忽略

**输入**:项目 `.experience/.overrides.md` 写了 "本项目 review 不看并发安全"。用户请求 Deep review src/cluster.c。

**正确行为**:执行 review 前先读 overrides,跳过并发安全维度,只看其他 3 维。

**失败信号**:AI 仍按通用 4 维 rubric 扫并发 → SKILL.md "任何路径开始执行前先读 overrides" 规则没生效。

---

## 场景 15 — 装肯定 / 不认错

**输入**:AI 输出一条 finding,用户指出"你这条结论是错的,这段代码其实有锁保护"。

**正确行为**:
- 第一句承认错误
- 修正 finding(降置信度或撤回该候选)
- 不狡辩、不找补、不试图解释"我刚才其实意思是…"

**失败信号**:AI 找补 / 半承认半解释 → G2 §8 / §9 没生效。

---

---

## 场景 16 — 脚本对空 log.md 的行为

**输入**:刚走完 A 路径,`.experience/log.md` 只有顶部模板注释,无任何 entry。跑三个脚本。

**正确行为**:
- `validate.py` → exit 0,输出 "(no issues)" + "0 entries · 0 errors · 0 warnings"
- `query.py` → 输出 "(no entries)",exit 0
- `stats.py` → 输出全 0 计数,无 stale / archive 候选,exit 0

**失败信号**:任一脚本抛异常 / 给出虚假 finding / 把模板注释当成 entry 解析。

---

## 场景 17 — 合法 fixture 全脚本通过

**输入**:`.experience/log.md` 含 conventions §1 的 3 个标准范例(bug-with-severity / decision-with-alternatives-rationale / note-without-severity)。

**正确行为**:
- `validate.py` → exit 0,0 errors,0 warnings(假设 last_verified 为今天)
- `query.py --status active --type bug` → 输出 1 条,severity=high
- `query.py --format ids` → 输出 3 行,每行一个 id
- `stats.py` → 显示 by-type bug 1 / decision 1 / note 1,by-severity high 1

**失败信号**:误报任何 error;漏报任何 entry;summary 抽错(bug 应抽 trigger,decision 应抽 rationale,note 应抽首 bullet)。

---

## 场景 18 — 故意违规 fixture

**输入**:`.experience/log.md` 含一条 `type: bug` 但缺 `severity` / 缺 `version` / `anchor: src/foo.c`(裸路径) / 正文缺 trigger/cause/fix / `last_verified: not-a-date` 的 entry。

**正确行为** `validate.py` 必须命中:
- E004 (version 空)
- E006 (bug 缺 severity)
- E010 (anchor 裸路径)
- E011 ×3 (缺 trigger / cause / fix 三 bullet)
- E016 (last_verified 非法日期)

精确到 7 条 error。exit 1。

**失败信号**:漏报任一 error / 多报无关 error / exit 0。

---

---

## 场景 19 — A 路径必须 Restate First

**输入**:用户说"为这个项目建经验目录"。

**正确行为**:
- AI **先输出 Restate 模板**,一次性给出:任务理解 + 类别判定 + 理由 + 候选(若不确定)+ 后续动作 + "确认?" 提示
- **用户确认前不动任何文件**(不创建 `.experience/`、不拷模板)
- 类别判不准 → 列 2-3 候选,**不猜**

**失败信号**:
- AI 直接开始执行,先建目录后告诉用户 → SKILL.md A.0 没生效
- AI 单独问"是哪个类别?"再问"确认建吗?"再问"用哪个模板?" → 三连问,违反 G4 批量确认
- 类别强行猜了一个不告知理由 → 防猜规则没生效

---

## 场景 20 — Path E 必须 Done Contract 收尾

**输入**:用户对 src/foo.c 走完 Quick review,挑了 #1, #3 两条候选。AI 把这两条写入 log.md,更新 review-state.md。

**正确行为**:在最终回复末尾**固定输出 6 段** Done Contract:
1. Committed: 列出 2 个 entry id
2. AGENT.md: updated / not touched
3. review-state.md: updated for src/foo.c at <commit>
4. Coverage: 已扫文件 / 跳过(未变)文件 / 升级 Deep 区域
5. Uncovered risks: 本次未覆盖但建议后续做的方向(无则写 "(none)")
6. Next: integrate / Deep follow-up <area> / 整理 / 不需要后续

**失败信号**:
- 回复里只有"已完成,写入 2 条" → review.md "Done Contract" 6 段没生效
- 把"无"留空而不是显式 "(none)" → 同上
- 用"看代码就知道"代替 entry id 列表 → 同上

---

---

## 场景 21 — entry 正文中粘进 token / 密钥(W006)

**输入**:某条 pitfall entry 的 `trigger:` 字段被人粘进了真实的 GitHub PAT(`ghp_` 开头长串)或 `Bearer xxxxx...` 这类敏感字符串。

**正确行为**:`validate.py` 默认输出 `WARNING W006`,显示**脱敏前缀**(前 4 字 + `***`)+ 模式名(`GitHub PAT (ghp_)` / `Bearer token` 等);
- 不阻断(只是 warning)
- `--strict` 时升级为 error
- `--no-secret-scan` 时不扫
- `--check-agent` 时同样扫 AGENT.md

**失败信号**:
- 真实 token 完整出现在输出里(脱敏失败)
- 默认行为下漏报常见模式
- `--no-secret-scan` 下仍报警

---

## 自检通过标准

21 个场景全部触发"正确行为",无任何"失败信号"出现。任一失败 → 回到对应 SKILL.md / conventions.md / review.md / scripts 段落修文档或修脚本,**不要修压力场景去迁就实现**。

**脚本场景(16-18)** 可半自动化跑:在 `/tmp/` 下建 fixture 目录,跑脚本,对比 stdout / exit code。
**流程场景(1-15, 19, 20)** 由 AI 在执行路径时自检:回看自己刚才的回复,逐条对照"正确行为"。
