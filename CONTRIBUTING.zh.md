# 参与 Mantoz

<p align="center"><img src="docs/assets/pantheon/doc-contributing.png" alt="低台上的两块大理石板，左边刻着三条线，右边还是空白等待着，前面放着一条金色带子" width="100%"></p>

感谢你来看。小而具体的改动合并得最快。

## 安装

```bash
git clone https://github.com/zarubinvibe/mantoz.git
cd mantoz
bash install.sh
uv run pytest
uv run ruff check .
```

`install.sh` 会把没能完成的事情说出来，而不是悄悄失败。如果它说缺 uv 或 Docker，离线检查仍然会跑，并告诉你这棵树是否完整。

## 一次改动的流程

1. Fork 这个仓库。
2. 建一个分支：`git checkout -b fix-survey-timeout`。
3. 做改动，并为它加一个测试。
4. 跑 `uv run pytest`、`uv run ruff check .` 和 `bash scripts/mantoz-selfcheck.sh --selftest`。
5. 如果动过 `config/` 或数据基础，再跑 `sh evals/licence_boundary_gate.sh`。
6. 按 `<type>: <描述>` 写提交信息：`fix: survey 环境在 30 秒后停止等待`。
7. 推送分支，开一个 Pull Request。

不要直接向 `main` 推送，发布闸门会拒绝。

## 会被合并的

最容易合并的改动是修一个 bug，并附上一个改动前失败、改动后通过的测试。测试比描述更有说服力，因为它把问题固定住了，以后谁也没法悄悄把它改回去。

新增任务同样受欢迎，前提是它自带检查程序：任务自己知道什么算通过，这是这个项目的基本约定。沙箱后端也可以加，加在 Harbor 的 `BaseEnvironment` 之后，与已有的并列，而不是替换掉其中一个。

纠正错误内容的文档改动一律欢迎，哪怕只改一个词。

## 不会被合并的

数据来源必须有书面的商业授权。条款要在真正给出文件的那个页面上读，而不是项目介绍页，并且在 Pull Request 里引用原文。这一条踩过坑：有一个来源的限制就写在下载表单后面，描述页上一个字都没有。

任何把数据、派生边际分布或模型权重纳入版本控制的改动都会被拒绝，许可闸门也会自动挡住它。

Harbor 保持为声明的依赖，并在 `NOTICE` 中署名，不会被复制进仓库。验证也不会被缩减成一两个审阅智能体：它故意属于任务本身，并且在人群规模上运行，这正是这个项目和随手问一个模型的区别。

规划只有一套。需求在 `queue/GOAL.md`，决定在 `docs/DECISIONS.md`，不会再开第二个。

## 报告问题

开一个 issue，写清楚你运行了什么、期望什么、实际发生了什么。附上命令和报错的前几行。一次运行在某个环境失败而在另一个环境正常，本身就是有用的线索，所以请说明你用的是四个环境中的哪一个。

安全问题请走 [SECURITY.md](SECURITY.md)，不要开公开 issue。
