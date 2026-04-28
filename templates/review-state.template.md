<!--
  review-state.md — 本地 review 跟踪库,纯 markdown,无二进制。
  Source of truth for "哪些文件 review 过了、commit 是什么、产出了哪些 entry"。

  使用规则(摘要,完整规则见 review.md):
  - 开 review 前先读本文件
  - 对每个目标,若当前 commit == last_commit → 跳过扫描,仍列入 session scope
  - 完成 review 后更新对应区块的 last_reviewed / last_commit / mode / findings
  - 同一文件多次 review,只保留最近一次记录(覆盖式更新)
  - 整个文件可被任何路径读;仅 path E(review)写
-->

# Review State — <项目名>

<!-- 每文件 / 每目录一段。新条目追加在文件末尾。覆盖更新已有条目。 -->

<!-- 示例:
## src/aof.c
- last_reviewed: 2026-04-28
- last_commit:   7a9f3d2
- mode:          quick
- findings:      2 (2026-04-28-redis-aof-fork-errno, 2026-04-28-redis-aof-script-coupling)
-->
