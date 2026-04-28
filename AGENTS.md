# AGENTS.md

This file governs AI agents that **work on this skill repository**(改这个 skill 本身的代码/文档).

It does **not** apply to AI agents that *use* the skill at a user's project site —— that audience is governed by `SKILL.md`. Don't confuse the two.

## 仓库定位

`experience-summary` 是一个**单 skill 仓库**,产出物:

- 一套 markdown 规约 + 4 类项目模板 → 被 AI 加载后在用户项目里维护 `.experience/`
- 3 个 Python 只读脚本(`scripts/`)→ 在用户项目里加速查询/校验/统计

仓库不是产品,不是平台,不是 framework。**任何把它往这三类方向推的改动都要先停一停。**

## 改动前必读

修改本仓库任何文件之前,**至少读完**:

| 改什么 | 必读 |
|-------|------|
| 任何路径流程 | `SKILL.md`(决策流程 + 全局规则) |
| entry / 字段 / status / 不变量 | `conventions.md` |
| review 子功能 | `review.md` |
| `scripts/` 任何文件 | `scripts-contract.md` + `conventions.md` |
| 模板 | 对应 `templates/AGENT.<category>.md` 的现状 + 该类别在 `categories.md` 的定位 |

**没读 contract 就改 scripts 是已知的反复犯过的错。** 不要再犯。

## 改动后必做

| 改了 | 必跑 |
|------|------|
| `scripts/lib/parse.py` 或任何 schema 字段 | scripts 三脚本对 16/17/18 fixture 全跑通 |
| `validate.py` 错误码 / 警告码 | 在 `validation.md` 加对应压力场景 |
| `SKILL.md` 任何路径 | 检查 `validation.md` 现有场景是否仍生效 |
| `conventions.md` 任何字段规约 | `templates/log.template.md` 模板对齐检查 |
| `review.md` 任何流程 | `SKILL.md` E 节指针仍然准确 |

**回归不通过不许 commit**。

## 输出风格(对用户的回复)

适用于本仓库内所有 AI 回复(开发讨论 / review / 修复)。在用户项目里执行 skill 时,SKILL.md G2 也写了相同 9 条 —— 这里是 source,SKILL.md G2 是镜像,**改一处要同步另一处**。

1. **结论先行**:第一行就是结论,不是过程独白
2. **表格 / 列表 > 段落**:枚举性内容必须表格化
3. **重要度排序**:不按时间序、不按文件序,按"用户最该先看"排
4. **一屏可读**:默认 ≤ 1 屏,展开放 details/ 或追加链接
5. **图表触发**:≥ 3 个组件关系 / 状态流转 / 时序 → mermaid;数值对比 → 表格
6. **不写过程独白**:"我先看一下…然后…"全删
7. **置信度显式**:不确定的结论标 `(low confidence)` / `<TBD>`
8. **错则认错**:用户指出错误,先承认再修正,不狡辩、不找补
9. **怀疑自己**:判断若依赖未验证假设,显式写"假设 X 成立时,…;否则结论失效"

## 安全 / Hygiene

### 永不 commit

- secrets / token / api key / 密码(无论是否带 placeholder)
- `.env` / 用户路径绝对值 / 真实业务字段 / PII
- `__pycache__/` / `*.pyc` / `.DS_Store`(已在 `.gitignore`)
- `.experience/` 目录本身(这是用户项目的产物,不该出现在 skill 仓库)

### Token 处理

- 用户在对话里贴 token → **立刻提醒撤销**,不要假装没看见
- push / fetch 用 token → **一次性 URL**,不写 `.git/config`,输出 sed 屏蔽
- 推荐用户 `gh auth login` 而不是反复贴 token
- 哪怕"反正稍后 revoke",也按上面三条做

### 推送前检查

```bash
git diff --stat                          # 看清改了什么
grep -rE "ghp_|sk-|api[_-]?key" .        # 漏网 secret 兜底
git status --short | grep -v '^??'       # 确认 untracked 是有意为之
```

## V1 边界(不要破)

这些是 V1 反复讨论后锁死的边界,任何想突破的改动需要先开新一轮设计讨论,不要直接动手:

- **不做跨项目共享**(每个 `.experience/` 单项目)
- **不做本地数据库 / 缓存 / 索引**(脚本无状态、只读、现解析)
- **不做版本范围推理**(no semver, no "earlier than")
- **不做自动修复**(脚本只报告,不改 entry)
- **不做自动锚点核验**(锚点真伪是 C 整理路径里 AI Read 手动)
- **不做第三方 Python 依赖**(stdlib only,Python 3.9+)

破了任何一条 = V1.5+ 范围,先讨论再做。

## 反模式(改本仓库时常见的)

- ❌ 改一个文件不查跨文件引用(SKILL.md 改了路径名,review.md 还指向旧名)
- ❌ 给 SKILL.md 不停加新区块,从不重构
- ❌ 把 contract 当文档读,不当 schema 读 → 实现漂移
- ❌ 在 conventions.md 里把规则写得比 scripts/ 实现得更强(已发生过一次)
- ❌ 增加 G3 进化触发以外的 AI 自动行为 —— 用户拍板 always wins
- ❌ 复制 `.experience/` 内容回 skill 仓库("看,真实例子!") —— 那是用户项目的隐私

## 维护节奏(防止"会提醒不会沉淀")

G3 进化触发只产生"建议",不产生"晋升"。需要一个最简的人工节奏把高频 `.overrides.md` 内容上升到通用规则,把低价值的清掉。否则 skill 会越用越散。

### 月度(每月一次,~10 分钟)

1. 跑 `python scripts/stats.py` 在每个使用本 skill 的项目,记下 entry 数 / stale candidates / archive candidates
2. 抽查 3-5 个项目的 `.overrides.md`,看是否有同一种 override 在 ≥3 个项目里重复(例如多项目都给 `risk` tag 加同义词)
3. 高频重复 override → 候选上升到 `conventions.md`(正式改 + 同步增 validation 场景)
4. 不结合具体项目的 override 不动

### 季度(每季度一次,~30 分钟)

1. 清过老 entry:跑 `python scripts/stats.py --stale-days 180`,逐条裁决:`fixed` / 新 entry supersede / 暂留
2. 跑 `python scripts/stats.py --current-version <v>`,审视 archive candidates 是否真该归档(per scripts-contract:候选 ≠ 应归档)
3. 检查 `.overrides.md` 总条数:超过 10 条 → 强信号,该收敛上升到通用规则,本项目不该一直背
4. AGENT.md 行数审查:接近 150 行的项目走整理

### 任何大规则变更必带

- `conventions.md` / `scripts-contract.md` 任何字段/规则变更 → 必带 `validation.md` 新场景
- 改了字段必填性 → 必带 `conventions.md` §1 示例同步
- 改了某条字段的语义 → grep 整库找到旧措辞,一并更新(已经因为这条踩过 2 次坑)

### 不做的

- 不做自动化"上升通用规则" —— 这是人类决策点
- 不做"按时间清 entry" —— 经验老不等于错,要看 status 与 last_verified
- 不写"维护工具" —— `stats.py` + grep 已经够用,加 dashboard = 范围膨胀

## 重大决策的痕迹

不要让讨论纪要全留在对话里,**把已锁死的决策写入对应文档**。已经锁的:

- log.md 是工作集 SoT,`.experience/` 整体是事实 SoT(conventions §8)
- type 4 选 1,risk 是 tag(conventions §6)
- `version` 必填,允许 unknown,不允许省略(conventions §4)
- archive candidates 是"差异于当前版本",不是"早于"(scripts-contract §archive)
- review 候选清单 + 用户拍板,不自动落库(review.md)
- 类别判不准走 application 兜底(categories.md)
- 脚本只读 / 无 DB / 无缓存(scripts-contract.md)

新决策落锁时,先找到对应文档增补,再说"已锁定"。
