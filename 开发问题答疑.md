# Git 协作常见问题答疑

> 写给初次参与 GitHub 团队协作的开发者。

---

## Q1：`git commit` 是把代码上传到 GitHub 吗？

**不是。** `git commit` 只是把改动**保存到你本地电脑的 git 历史里**，完全不影响远端仓库和其他人。

真正上传到 GitHub 的命令是 `git push`。

```
git commit  →  本地保存（只在你电脑上）
git push    →  上传到 GitHub（其他人才能看到）
```

所以你可以放心地频繁 commit，随时记录进度，不会影响任何人。

---

## Q2：我是被邀请的共创者，不是仓库创建者，我有权限 push 吗？

**大概率有。** GitHub 的 Collaborator（共创者）角色通常可以 push 到**非保护分支**。

- `main` 分支可能受保护，不能直接 push（需要通过 Pull Request 合并）
- 你自己负责的功能分支（例如 `feature-streamlit-ui`）通常可以直接 push

如果 push 时提示权限不足，联系仓库创建者确认你的权限设置即可。

---

## Q3：我 push 的时候，代码会不会上传到 main 分支，影响别人？

**不会。** git push 只会上传到你当前所在的分支对应的远端分支。

本项目的 worktree 分支 `claude/amazing-satoshi-053fa2` 追踪的是 `origin/feature-streamlit-ui`，所以执行 push 时代码只会上传到 GitHub 上的 `feature-streamlit-ui`，完全不会动 `main`。

```
你的本地分支                   GitHub 远端
claude/amazing-satoshi-053fa2  →  feature-streamlit-ui  ✅
                               →  main                  ❌ 不会动
```

---

## Q4：之前提到我的设备缺少某个软件，会影响开发吗？

缺少的是 **`gh`（GitHub CLI）**，这个工具只用来在终端里**创建 Pull Request**。

它对日常开发完全没有影响：

| 操作 | 需要什么 | 状态 |
|------|---------|------|
| `git commit`（本地保存） | git（系统自带） | ✅ 可用 |
| `git push`（上传到 GitHub） | git + GitHub 账号认证 | ✅ 可用 |
| 创建 Pull Request | `gh` CLI 或浏览器 | 用浏览器即可 |

创建 PR 时，直接打开 GitHub 网页，点击 **"Compare & pull request"** 按钮，填写标题和描述提交即可，完全不需要安装 `gh`。

---

## Q5：整个开发流程里，git 命令的顺序是什么？

```bash
# 1. 写完一个文件后，保存到本地
git add <文件名>
git commit -m "描述你做了什么"

# 2. 上传到 GitHub 的 feature-streamlit-ui 分支
git push

# 3. 所有功能完成后，去 GitHub 网页创建 Pull Request
#    请求把 feature-streamlit-ui 合并到 main
```

---

*本文档由 K-Read Coach 项目前端开发窗口 1 生成，2026-05-09。*
