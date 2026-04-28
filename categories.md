# Categories — 项目类型判定

4 类。判定结果决定 `templates/AGENT.<category>.md` 选哪一份。**`log.md` / `conventions.md` 在所有类别下完全一致**,只有 AGENT.md 导航重点不同。

## 判定决策树

```
项目里大部分文件是不是你/你团队写的?
├─ 否 ── 读官方源码 / 看明白别人怎么实现的 ─────► source-read
└─ 是
   ├─ fork 自上游 / 在外部源码上加 patch ──────► source-fork
   ├─ 给最终用户跑的服务、APP、网站、内部系统 ──► application
   └─ 一次性脚本、CLI、构建工具、运维小工具 ────► tool
```

## 4 类速查

| category | 典型项目 | AGENT.md 导航重点 | log.md 高频 type |
|----------|---------|-----------------|----------------|
| `source-read` | 阅读 Redis / ES / MySQL / Kafka / Linux / React 源码 | 主链路 / 模块边界 / 关键算法 / 调用图 | `note`(架构) `decision`(理解作者选择) |
| `source-fork` | fork 上游 + 二开补丁、定制版 | 改动点清单 / 兼容性风险 / 与上游 diff / 升级痛点 | `decision`(改造选型) `bug` `pitfall` |
| `application` | 公司内部业务系统、SaaS、网站、APP 后端 | 业务入口 / 上下游依赖 / 配置项 / 线上事故 | `bug`(线上故障) `pitfall`(配置/依赖) |
| `tool` | CLI、构建脚本、运维工具、一次性数据处理 | 用法示例 / 边界条件 / 失败案例 / 退出码语义 | `pitfall`(用法) `note`(边界) |

## 判定示例

| 输入 | 判定 | 理由 |
|------|------|------|
| 我在读 Redis 7 源码学网络模型 | `source-read` | 不修改,纯学习 |
| 我们 fork 了 Redis 加了一个新命令 | `source-fork` | 在上游源码上加 patch |
| 公司订单服务,Spring Boot | `application` | 内部业务系统 |
| 一个 Python 脚本批量处理 CSV | `tool` | 一次性工具 |
| Next.js 个人博客 | `application` | 给最终用户跑 |
| 维护 fork 的 Vim 配置 | `tool` | 配置/工具 |

## Fallback(判不准时)

如果出现以下情况,**先问用户**而不是猜:

- 是 fork 但已经面目全非,基本只剩业务逻辑 → 问"按 source-fork 还是 application?"
- monorepo 里同时有多种性质的子项目 → 问"在哪个子目录建 `.experience/`?是否每个子项目独立建?"
- 文档站、配置仓、数据集仓等不在 4 类内 → 默认走 **application**(它是兜底类)

兜底原则:**判不准走 application**。application 模板的导航最通用,后续真要换可以重写 AGENT.md(log.md 不动)。

## 一个项目可不可以是多类?

不可以。**一个 `.experience/` 只对应一个 category**。
如果同一仓库既做源码改造又承担应用职能(罕见),按 **主要价值产出** 选 —— 你/团队主要写的是 patch 还是业务?
真分不开 → monorepo 拆子目录,各自建独立 `.experience/`。
