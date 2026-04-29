---
description: Route a request into the experience-summary workflow
---

# /exp

Use the `experience-summary` workflow for the user's request:

`$ARGUMENTS`

## Intent Routing

Interpret the user's request after `/exp` and route it into one path:

1. **初始化**
   Trigger when the user wants to create `.experience/` for the first time.

2. **追加**
   Trigger when the user wants to record a bug, pitfall, decision, or note.

3. **整理**
   Trigger when the user wants to clean up, verify anchors, archive stale items, or reorganize the experience log.

4. **阅读**
   Trigger when the user wants to read the existing experience directory before analysis.

5. **Review**
   Trigger when the user wants code review / quick review / deep review for a scope.

## Rules

- Treat `/exp <自然语言>` as if the user had directly asked to use the `experience-summary` skill for that task.
- If the request is already specific, do **not** ask redundant questions.
- If the request is empty or too vague, ask one short routing question:

```text
你要我用 /exp 做哪一类? 初始化 / 记经验 / 整理 / 阅读 / review
```

- For review requests:
  - only `scope` is a hard follow-up field
  - `mode` defaults to `quick`
  - `ignore` defaults to `low`

- Follow the existing `experience-summary` rules for entry schema, archive semantics, review flow, and user confirmation.
