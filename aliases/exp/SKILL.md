---
name: exp
description: Use when the user explicitly invokes $exp as a shorthand entrypoint for the experience-summary workflow
---

# exp

`$exp` is a thin shorthand alias for `experience-summary`.

Treat any text following `$exp` as the user's intent, then route it into one path:

1. 初始化
2. 追加
3. 整理
4. 阅读
5. Review

## Routing Rules

- `$exp 初始化这个项目的经验目录`
  -> 初始化路径

- `$exp 记一条 BUG: ...`
  -> 追加路径

- `$exp 整理一下经验目录`
  -> 整理路径

- `$exp 看下之前踩过哪些坑`
  -> 阅读路径

- `$exp review src/order/service.go`
  -> Review 路径

## Defaults

- 如果用户表达已经足够明确,不要重复确认路由类别
- 如果请求过于模糊,只问一句:

```text
你要我用 $exp 做哪一类? 初始化 / 记经验 / 整理 / 阅读 / review
```

- review 默认:
  - `mode=quick`
  - `ignore=low`
  - 只有 `scope` 是硬反问字段

## Boundary

This alias does not define a separate experience system.

It exists only so the user can type `$exp ...` instead of naming the full `experience-summary` skill every time.
