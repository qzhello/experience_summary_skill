<!--
  log.md — 标准化经验条目流。Source of truth for .experience/.

  写入规则(摘要,完整规则见 skill 的 conventions.md):
  - 只在文件顶部追加新 entry(最新在上)。
  - 已存在 entry 的正文不可修改。只允许改三个字段:status / last_verified / supersedes。
  - 修正旧结论 → 写新 entry,supersedes: <old-id>;旧条目 status 切 stale 或 fixed。
  - 删除 entry 仅在整理路径中、status=stale|fixed 且 version 已超出当前使用范围时,搬入 details/archive/<id>.md。
  - id 全仓库唯一,格式 YYYY-MM-DD-<kebab-slug>;同日同主题次条加 -2、-3 后缀。
  - type 4 选 1:bug / pitfall / decision / note。risk 是 tag,不是 type。
  - version 必填,允许模糊但不允许省略(unknown 是合法显式值)。
  - bug / pitfall 必须填 anchor (path:line / path:symbol / 多锚点),并必须填 severity。
  - decision / note 不允许填 severity 字段。
  - 展开超 5 行 → 写 details/<id>.md,本文件正文只留 trigger/cause/fix + details 链接。
  - git merge 冲突时:保留全部条目,按 id 时间戳重排,不二选一。

  Entry 模板 — bug / pitfall(整段复制到顶部,填值):

  ## YYYY-MM-DD-kebab-slug
  type: bug | pitfall
  version: <e.g. redis@7.2.4 | redis@7.2.x | internal-app@2026-04 | unknown>
  status: active
  severity: critical | high | medium | low
  anchor: path/to/file.ext:line       # 或 path:symbol;多锚点逗号分隔(≤3 处)
  last_verified: YYYY-MM-DD
  supersedes:
  tags:

  - trigger: <一句话:什么场景下出现>
  - cause:   <一句话:根因>
  - fix:     <一句话:解法>
  - details: [details/YYYY-MM-DD-kebab-slug.md](details/YYYY-MM-DD-kebab-slug.md)   <!-- 仅当展开超 5 行时 -->

  Entry 模板 — decision(无 severity,正文必须含 alternatives + rationale):

  ## YYYY-MM-DD-kebab-slug
  type: decision
  version: ...
  status: active
  anchor:                             # 可空
  last_verified: YYYY-MM-DD
  supersedes:
  tags:

  - context:      <为什么要做这个选择>
  - alternatives: <被拒方案 1>; <被拒方案 2>
  - rationale:    <选这个的理由>
  - details: [...]                     <!-- 可选 -->

  Entry 模板 — note(无 severity):

  ## YYYY-MM-DD-kebab-slug
  type: note
  version: ...
  status: active
  anchor: path/to/file.ext:symbol     # 可空,推荐填
  last_verified: YYYY-MM-DD
  supersedes:
  tags:

  - <一段一句话观察 / 架构认知 / 性能记录>
  - details: [...]                     <!-- 可选 -->
-->

# <项目名> · 经验日志

<!-- 新 entry 追加在下面这一行之下,保持最新在上。第一条之前不要插入文字。 -->
