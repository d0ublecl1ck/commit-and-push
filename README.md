<div align="center">

# commit-and-push · `cap`

> *「别把一轮工作压成一个说不清的大提交。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blueviolet)](SKILL.md)
[![skills.sh](https://skills.sh/b/d0ublecl1ck/commit-and-push)](https://skills.sh/d0ublecl1ck/commit-and-push)
[![Verify](https://github.com/d0ublecl1ck/commit-and-push/actions/workflows/verify.yml/badge.svg)](https://github.com/d0ublecl1ck/commit-and-push/actions/workflows/verify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**把一轮 Agent 工作拆成可审计的 Conventional Commits，并在推送前挡住秘密、垃圾文件和同步风险。**

[看效果](#效果示例) · [安装](#快速开始) · [触发方式](#触发方式) · [安全边界](#安全边界) · [验证](#验证与测试)

</div>

---

## 它解决什么问题

你让 Agent 改了功能、测试和文档，最后一句“提交并推送”看似简单，实际可能发生：所有变化被塞进一个提交、别人的改动被顺手带上、`.env` 被误提交，或远端领先时直接 push 失败。

`commit-and-push` 不只是生成 commit message。它先识别仓库边界和变更来源，再给出提交计划，逐组检查 staged diff，最后安全同步和推送。

它不需要 API Key，也不调用外部模型；由当前 Agent 使用本地 Git 完成工作。

---

## 效果示例

输入：

```text
cap
```

面对同时包含功能、测试、文档、日志和 `.env` 的脏工作区，它应先给出：

```text
Commit 1 — feat(validation): add URL validation
  src/validation.ts
  tests/validation.test.ts

Commit 2 — docs(readme): document validation behavior
  README.md

Ignored
  debug.log — local runtime artifact

Blocked
  .env — secret-like file; explicit approval required
```

随后仅提交计划内文件，并报告每个 SHA 与 push 结果。完整样例见 [`examples/commit-plan.md`](examples/commit-plan.md)。

---

## 快速开始

```bash
npx skills add d0ublecl1ck/commit-and-push
```

安装后，对 Agent 明确说：

```text
cap
```

或：

```text
提交并推送当前仓库的全部预期改动，不要包含无关文件。
```

> 只有明确要求 `commit and push`、`提交并推送` 或 `cap` 才会触发。仅说“写个 commit message”“提交一下”或“可以了吗”不会触发推送。

---

## 触发方式

会触发：

- `cap`
- `use commit-and-push`
- `commit and push these changes`
- `提交并推送当前改动`
- `把这轮修改按意图拆分后提交并推送`

不会触发：

- `帮我写 commit message`
- `只提交，不推送`
- `实现完帮我收尾`
- `可以了吗？`
- 普通编码、评审、调试或规划请求

---

## 它会交付什么

| 阶段 | 可见产物 |
|---|---|
| 预检 | 仓库、分支、upstream、ahead/behind、脏文件摘要 |
| 规划 | 按对话轮次或变更意图拆分的 commit plan |
| 安全检查 | blocked secrets、ignored junk、歧义文件列表 |
| 提交 | 每个原子提交的 SHA 与 Conventional Commit subject |
| 推送 | 每个仓库的 remote、branch 和 push 结果 |
| 异常 | hook、rebase、冲突或 push 错误及未推送 SHA |

---

## 它和同类有什么不同

| 维度 | 常见 AI commit 工具 | commit-and-push |
|---|---|---|
| 主要目标 | 生成一条提交信息 | 编排完整、安全、可审计的提交与推送 |
| 变更分组 | 通常把 staged diff 当成一组 | 优先按对话轮次，其次按 diff 意图分组 |
| 授权 | 常由模糊提交意图触发 | 严格 opt-in，必须明确要求 commit + push |
| 脏工作区 | 依赖用户先整理 | 主动识别秘密、垃圾和无关修改 |
| 多仓库 | 通常只看当前仓库 | 每个仓库独立预检、提交、同步和汇报 |
| 可验证性 | 依赖演示或模型效果 | 自带离线 Git 状态、安全检测 fixtures 与 CI |

灵感与对标包括 [OpenCommit](https://github.com/di-sukharev/opencommit)、[AI Commits](https://github.com/Nutlope/aicommits)、[Commitizen](https://github.com/commitizen-tools/commitizen) 和 [commitlint](https://github.com/conventional-changelog/commitlint)。本 Skill 聚焦安全编排，不替代这些工具。

---

## 安全边界

它不会：

- 主动触发或把模糊的“ship it”解释为 commit + push 授权；
- 修改全局或仓库 Git 配置；
- 默认使用 `git reset --hard`、`git clean -fd`、交互式 rebase 或 force push；
- 自动提交 `.env`、凭据、私钥、token、cookie、虚拟环境或大二进制；
- 丢弃、覆盖或回滚不属于当前任务的修改；
- 自动解决冲突、创建 PR、merge、tag、release 或部署。

它会在 detached HEAD、冲突、文件归属不清、秘密提交请求或 push 失败时停下来说明情况。

---

## 文件结构

```text
.
├── SKILL.md                         # Agent 执行规则与安全边界
├── README.md                        # 安装、触发、示例与验证入口
├── LICENSE                          # MIT License
├── references/commit_examples.md    # Conventional Commit 扩展示例
├── examples/commit-plan.md          # 可见的提交规划样例
├── examples/install-check.txt       # 公网安装检查记录
├── scripts/verify_skill.py          # 离线 Git fixture 验证器
├── tests/test_skill.py              # 结构和行为契约测试
├── .github/workflows/verify.yml     # 持续验证
└── .claude-plugin/marketplace.json  # Claude Code marketplace 元数据
```

---

## 验证与测试

无需网络或 API Key：

```bash
python3 scripts/verify_skill.py
python3 -m unittest discover -s tests -v
```

验证器在操作系统临时目录创建并自动清理 Git fixtures，验证：

- dirty worktree 状态识别；
- first commit 检测；
- 嵌套、已暂存、常见凭据名及内容型 secret 启发式检测；
- clean worktree 的精确 ahead/behind 计算；
- tracked junk 使用 `git rm --cached` 后仍保留本地文件。

Secret 检测是阻断明显风险的启发式门禁，不替代专用 secret scanner。验证器检查规则依赖的确定性 Git 状态和安全检测，不模拟 Agent 的自然语言分组质量，也不声称覆盖真实 push、hook 或冲突处理。合格标准：所有结构检查和五个 fixture 均显示 `PASS`。

---

## License

[MIT](LICENSE)
