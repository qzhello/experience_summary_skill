# experience-summary

一个给项目做经验沉淀的 skill。

> **它是什么、不是什么**
> ✅ 是:**结构化沉淀工具** —— 帮 AI 把你和它一起踩过的坑、做过的决定、读过的源码记录得**整齐、可追溯、可查询**。
> ❌ 不是:自动学习引擎 —— 它**不会自己**归纳新规律、自己收敛模式、自己改进规则。规则的进化由人类周期性地 review `.overrides.md` → 上升到通用规则。

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
git clone https://github.com/qzhello/experience_summary_skill.git experience_summary_skill
cd experience_summary_skill
```

### 推荐: 一键安装脚本

仓库自带 `install.sh`。

```bash
chmod +x install.sh
./install.sh
```

默认行为:

- 检查 `~/.claude` 和 `~/.codex` 是否存在
- 如果两者都存在,提示你选择安装到 Claude Code / Codex / Both
- 如果只存在一个,默认安装那个

全量更新安装:

```bash
./install.sh -g
```

这会把当前仓库内容同步到所有已存在的目标目录,适合仓库更新后重新执行一次。

也支持非交互定向安装:

```bash
./install.sh --claude
./install.sh --codex
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

如果你还想在 Claude Code 里用统一斜线命令 `/exp`,再额外复制命令文件:

```bash
mkdir -p ~/.claude/commands
cp commands/exp.md ~/.claude/commands/exp.md
```

最短验证步骤:

1. 打开 Claude Code,进入任意项目目录
2. 在 **Claude Code 对话框** 输入:

```text
/exp 初始化这个项目的经验目录
```

3. 如果命令生效,Claude Code 会把它当成 slash command 处理,而不是普通文本

注意:

- `/exp ...` 是 **Claude Code 对话命令**
- `pwd` 是 **shell 命令**
- 不要在 zsh/bash 里执行 `/exp` 或 `/pwd`

例如:

```bash
pwd
```

```text
/exp review src/order/service.go
```

### Codex

复制到 Codex skills 目录:

```bash
mkdir -p ~/.codex/skills/experience-summary
cp -R . ~/.codex/skills/experience-summary/
```

安装后目录应为:

```text
~/.codex/skills/experience-summary/
```

如果你还想在 Codex 里用更短的 `$exp` 入口,再额外复制 alias skill:

```bash
mkdir -p ~/.codex/skills/exp
cp aliases/exp/SKILL.md ~/.codex/skills/exp/SKILL.md
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

## 快捷命令

如果你不想每次都手写 `use experience-summary skill ...`,可以直接用统一入口。

### Claude Code: `/exp`

适合 Claude Code 的统一 slash command:

```text
/exp 初始化这个项目的经验目录
/exp 记一条 BUG: 支付回调重复消费导致订单状态回退
/exp review 一下 src/order/service.go
/exp 看下这个项目之前踩过哪些坑
/exp 整理一下经验目录
```

### Codex: `$exp`

适合 Codex 的统一 skill 入口:

```text
$exp 初始化这个项目的经验目录
$exp 记一条 BUG: 支付回调重复消费导致订单状态回退
$exp review src/order/service.go
$exp 看下之前踩过哪些坑
$exp 整理一下经验目录
```

语义和 Claude Code 的 `/exp` 保持一致:根据你后面的自然语言,自动路由到初始化 / 追加 / 整理 / 阅读 / review 路径。

### 什么时候用快捷命令,什么时候直接说自然语言

- 想快速进入 experience-summary,用 `/exp ...` 或 `$exp ...`
- 想把任务说完整,直接自然语言更方便

例如:

```text
/exp 初始化这个项目的经验目录
```

```text
$exp review src/order/service.go
```

```text
记一条 BUG: 支付回调重复消费导致订单状态回退
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
