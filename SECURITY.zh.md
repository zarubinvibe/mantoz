# 安全与隐私

<p align="center"><img src="docs/assets/pantheon/doc-security.png" alt="一道没有缺口的大理石界墙，近侧放着一只合上的大理石箱，五条蓝色细线在墙脚就停住了" width="100%"></p>

## 如何报告漏洞

请不要开公开 issue。通过
[GitHub 安全公告](https://github.com/zarubinvibe/mantoz/security/advisories/new)
写给作者。说明你运行了什么、看到了什么、攻击者能利用它做什么。通常几天内会有第一次回复。

## Mantoz 会碰到什么

| 面 | 实际发生的事 |
|---|---|
| 文件 | 读取仓库，并写到你用 `--out` 指定的路径。别的都不碰。 |
| 网络 | 默认路径上完全不发请求。只有你传了 `--live-provider`，在线评审才会连它的服务商。只有你选了 Modal，才会连 Modal。 |
| Shell | 任务的检查程序是 `application/tasks/*/tests/` 里的 shell 脚本。它们在任务环境里跑，不在你的主机上跑。 |
| 沙箱 | 任务环境跑在 Docker 容器里，镜像来自任务自己的 `Dockerfile`。默认 Docker，Modal 需要单独打开而且要花钱。 |
| 密钥 | 从环境变量或 `.env` 读取，不会进 git。`.gitignore` 挡住 `.env`、`*secret*`、`*credential*`、`*.pem` 和私钥。 |
| 遥测 | 没有。没有 Mantoz 服务器，没有账号，也没有使用上报。 |
| 回滚 | 每次运行只往你指定的路径写一个 JSON 报告。删掉文件就什么都不剩。 |

## 数据边界

这一段值得读两遍。

Mantoz 会用真实统计来校准生成的人物。不同来源的条款差别很大，其中一个禁止以**任何形式**转交数据，包括派生出来的数字。所以这条边界做成了闸门，而不是一句承诺：

- `data/` 在 `.gitignore` 里，不进版本控制。
- `config/grounding.json` 逐个来源记录：是否允许商业使用，是否允许转发。没有商业授权的来源会被标成 `local_only: true`。
- 一旦有数据、派生边际分布或模型权重进入 git，或者 `data/` 不再被忽略，或者受限来源丢了标记，`evals/licence_boundary_gate.sh` 就会让构建失败。
- 作为生产数据基础发布的来源只有一个：通过 tochno.st 的俄罗斯统计局与央行数据，CC BY 4.0，书面允许商业使用。

每次推送前先跑闸门：

```bash
sh evals/licence_boundary_gate.sh
```

## Mantoz 不能替你挡住的

- 你自己写的任务环境。它的 `Dockerfile` 和检查程序里放了什么，就会跑什么。
- 你自己打开的在线 LLM 服务商。提示词和回答按它的条款发给它。
- 把模拟出来的人当成真实用户来下结论。
