# experience-summary

一个给项目做经验沉淀的 skill。

它会帮助 AI 在项目根目录维护一套 `.experience/` 结构,用于记录:

- 踩坑
- BUG 回顾
- 技术决策
- 架构/功能认知
- 代码 review 发现

生成后的核心目录:

```text
.experience/
├── AGENT.md
├── log.md
├── review-state.md
└── details/
    └── archive/
```

## 适合谁

适合这几类项目:

- 源码阅读项目: Redis / ES / MySQL / Kafka / React 等
- 源码改造项目: fork 上游后二开
- 应用项目: 公司内部系统 / SaaS / 网站 / 后端服务
- 工具项目: CLI / 脚本 / 运维工具 / 数据处理工具

## 安装

先 clone 这个仓库,再进入仓库目录:

```bash
git clone <your-repo-url> experience-summary
cd experience-summary
```

### Claude Code

复制到 Claude Code skills 目录:

```bash
mkdir -p ~/.claude/skills/experience-summary
cp -R . ~/.claude/skills/experience-summary/
```

安装后目录应为:

```text
~/.claude/skills/experience-summary/
```

### Codex

复制到 Codex skills 目录:

```bash
mkdir -p ~/.agents/skills/experience-summary
cp -R . ~/.agents/skills/experience-summary/
```

安装后目录应为:

```text
~/.agents/skills/experience-summary/
```

## 怎么用

在你的目标项目里,直接对 AI 说这些话即可:

### 1. 初始化经验目录

```text
请用 experience-summary skill 为这个项目初始化经验目录
```

或:

```text
帮我给这个项目建立 .experience 目录
```

### 2. 追加一条经验

```text
记一条踩坑: Redis AOF rewrite 时 fork 失败,根因是内存峰值过高
```

```text
记一条 BUG: 支付回调重复消费导致订单状态回退
```

```text
记一条 decision: 这里选 Redis 不选 Memcached
```

### 3. 整理经验库

```text
整理一下这个项目的经验目录
```

```text
校验一下 .experience 里的锚点和过期条目
```

### 4. 阅读经验

```text
看下这个项目之前踩过哪些坑
```

```text
先读这个项目的经验目录,再继续分析代码
```

### 5. 做 review

```text
用 experience-summary skill quick review 一下 src/order/service.go
```

```text
deep review 一下 Redis AOF 相关调用链
```

## 使用后的效果

这个 skill 不会把经验拆成很多散文件,而是以条目为中心:

- `log.md` 记录经验事实
- `AGENT.md` 提供导航入口
- `details/` 放长内容
- `review-state.md` 避免重复 review

## 你真正需要知道的 3 条规则

1. `log.md` 是当前工作集事实源,新经验只往顶部追加。
2. `AGENT.md` 是导航页,不是事实源。
3. 修正旧结论时,写新条目,不要回头改旧正文。

## 规则文件

如果你后面要深入看规则,按这个顺序读:

1. [SKILL.md](SKILL.md)
2. [conventions.md](conventions.md)
3. [review.md](review.md)
4. [categories.md](categories.md)
5. [validation.md](validation.md)
