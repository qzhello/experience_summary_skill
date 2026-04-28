# Scripts Contract

这份文档定义 `.experience/` 配套只读脚本的**行为契约**。

目标是先锁死语义边界,避免后续实现 `query.py` / `validate.py` / `stats.py` 时与现有 skill 规则分叉。

## 目标

这些脚本是 `.experience/` 的**只读辅助工具**,用于:

- 查询
- 校验
- 统计

它们:

- **不是** source of truth
- **不修改** `.experience/` 任何文件
- **不替代** AI 与人工判断

## 作用范围

- 默认只读 `.experience/log.md`
- 显式开启时可读 `details/archive/`
- 不写 `log.md` / `AGENT.md` / `details/` / `review-state.md`

## 公共调用规则

- 默认在目标项目根目录运行
- 可显式传 `--root <path>`
- 找不到 `.experience/log.md` 时退出码为 `2`

## 解析契约

- 唯一解析器: `scripts/lib/parse.py`
- `parse.py` 实现的是 `conventions.md` 中的 entry schema
- 其他脚本**不得**各自重新实现 markdown 解析逻辑

`parse.py` 返回两类结果:

- `entries`: 成功解析的 entry 列表
- `errors`: 解析级错误列表

每个解析错误至少包含:

- entry 起始行号
- entry id(若能识别)
- 错误原因

## Entry 摘要规则

所有脚本使用统一摘要提取逻辑,由 `parse.py` 提供,不要各自拼接。

- `bug` / `pitfall`: 优先取 `trigger`;没有则取 `fix`
- `decision`: 取 `rationale`
- `note`: 取正文首行

## 过滤语义

- 不同 flag 之间: **AND**
- 同一 flag 内逗号分隔: **OR**

例如:

- `--status active --type bug --tag risk`
  表示 `status=active AND type=bug AND tags contains risk`
- `--severity high,critical`
  表示 `severity in {high, critical}`

## Version 语义

V1 锁死为**简单字符串语义**,不做版本范围推理。

- `--version <value>`: 字符串精确匹配
- `--version-prefix <prefix>`: 前缀匹配
- `unknown`: 视为普通字符串值

V1 **不支持**:

- `redis@7.2.4` 命中 `redis@7.2.x`
- `redis@7.2.4` 命中 `redis@>=7.0,<8.0`
- semver 比较
- 区间相交判断
- "早于" / "晚于" / "更旧" 等任何顺序判断(包括 archive candidates 的判定)

## Archived 语义

- 默认只查询 `log.md`
- 加 `--include-archived` 时,把 `details/archive/*.md` 一并纳入
- 输出中应标识来源:`log` / `archive`

## query.py

用途:过滤和聚合视图。

### 默认输出

- 默认输出精简表格
- 只显示摘要,不显示长正文
- 想看正文时,用户应继续 grep / 打开对应 id

### 建议参数

- `--status <value>`
- `--type <value>`
- `--severity <value[,value...]>`
- `--tag <value>`
- `--version <value>`
- `--version-prefix <prefix>`
- `--group-by type|status|severity|version`
- `--format table|ids`
- `--include-archived`
- `--strict-parse`

### 输出格式

`--format table`:

- `id`
- `type`
- `status`
- `severity`
- `summary`

`--format ids`:

- 每行只输出一个 id

## validate.py

用途:检查 `.experience/` 是否符合 `conventions.md`。

### 默认检查范围

- 默认只检查 `log.md`
- `--check-agent` 时附带检查 `AGENT.md`

### 问题等级

#### error

- 必填字段缺失
- `bug` / `pitfall` 缺 `severity`
- `decision` / `note` 非法出现 `severity`
- `bug` / `pitfall` 缺 `trigger` / `cause` / `fix`
- `decision` 缺 `alternatives` 或 `rationale`
- `version` 为空
- `anchor` 是裸路径(没有 `:line` / `:symbol`)
- id 重复
- id 格式不符 `YYYY-MM-DD-<kebab-slug>`
- entry 使用 `---` YAML 分隔符
- `supersedes` 指向不存在的 id
- `supersedes` 出现环
- `status=fixed` 但 `type != bug`

#### warning

- `version=unknown`
- `last_verified` 过旧
- `AGENT.md` 行数接近上限
- `AGENT.md` 链了非 active 条目(仅 `--check-agent`)

### 模式

- 默认:有 `error` 则失败,`warning` 仅报告
- `--strict`:把 `warning` 也升级为失败

## stats.py

用途:给当前工作集一个总览视图。

### 默认输出

- `log.md` entry 总数
- `log.md` 行数
- 按 `type` 计数
- 按 `status` 计数
- 按 `severity` 计数(仅 `bug` / `pitfall`)
- stale candidates
- archive candidates
- `AGENT.md` 行数与阈值提示

### 建议参数

- `--stale-days <n>`:默认 `90`
- `--agent-cap <n>`:默认 `150`
- `--current-version <value>`
- `--include-archived`
- `--strict-parse`

### stale candidates

定义:

- `status=active`
- `last_verified` 距今大于阈值

### archive candidates

定义(与 V1 "无版本推理" 约束严格一致):

- `status in {stale, fixed}`
- 且 `version` 字段**不等于**当前项目版本(纯字符串比较)
- 且 `version` 字段**不是** `unknown`

**语义说明**:这里是"差异于当前版本",**不是"早于当前版本"**。
V1 不做任何顺序判断 —— 一个 stale/fixed 条目只要 version 和当前不一样,就提示给用户考虑归档。
因此清单里**可能包含并行分支版本、未来版本字符串、命名体系不同的版本**;实际是否归档由人工判断,脚本只负责提候选。

stats.py 输出必须显式带上"差异"语义提示,避免被误读成"更旧"。

当前版本来源顺序:

1. `--current-version`
2. `AGENT.md` 中的"当前版本"行
3. 若仍未知,则**不计算 archive candidates**,只提示 `current version unknown`

## 容错策略

- `validate.py`:有 `error` 就失败
- `query.py` / `stats.py`:默认尽量输出可解析部分,同时向 stderr 报解析错误
- `--strict-parse`:任意解析错误直接失败

## 退出码

- `0`:成功
- `1`:发现违规、解析失败、或严格模式下有 warning
- `2`:参数错误、路径错误、缺少必要文件

## 非目标

这些脚本 V1 **明确不做**:

- 自动修复
- 自动写回
- 缓存
- 数据库
- 版本范围推理
- 自动锚点核验
- 替代 AI / 人工判断经验内容是否正确

## 与 skill 的关系

这些脚本只是加速器,不是 skill 的前提条件。

- 脚本不存在,skill 仍可正常工作
- 脚本失败,skill 仍可继续走 AI + 用户拍板流程
- 所有写入仍由 AI 按 `SKILL.md` / `conventions.md` 执行
