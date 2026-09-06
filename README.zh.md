# Mantoz

在真人看到之前，先让生成的人群把产品走一遍。

[English](README.md) · [Русский](README.ru.md)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Stars](https://img.shields.io/github/stars/zarubinvibe/mantoz?style=flat&color=C9A87A)](https://github.com/zarubinvibe/mantoz/stargazers) [![Status](https://img.shields.io/badge/status-working-brightgreen.svg)](https://github.com/zarubinvibe/mantoz) [![Olympuz](https://img.shields.io/badge/olympuz-family-B8D6EA.svg)](https://github.com/zarubinvibe/athena#olympuz-family)

<p align="center"><img src="docs/assets/pantheon/hero.png" alt="白色大理石的曼托手托占卜浅盘，旁边是一小群大理石人像；蓝色细线沿地面进入盘中，三条金色带子从盘中通向石板，右侧立着家族的古典石柱" width="100%"></p>

<!-- owner-welcome:start -->

> 你好。我是律师，有两个女儿，还做咖啡生意，所以只能在晚上写代码，也没法为每个想法都做一轮调研。
>
> Mantoz 就是这么来的。它让我在花掉别人（也包括我自己）的时间之前，先听到一群人的第一反应。它不会告诉你客户在想什么。它会告诉你，你的哪个想法一被一百个不同的人碰到就散了。
>
> 它属于 Olympuz 工具家族：https://github.com/zarubinvibe/athena#olympuz-family
>
> — Filipp Zarubin

<!-- owner-welcome:end -->

## 目录

- [这是什么](#这是什么)
- [它解决什么问题](#它解决什么问题)
- [最大的优势](#最大的优势)
- [工作流程](#工作流程)
- [快速开始](#快速开始)
- [简单对比](#简单对比)
- [简单词汇](#简单词汇)
- [安全与隐私](#安全与隐私)
- [局限](#局限)
- [点亮星标与参与](#点亮星标与参与)

<!-- beginner-readme:start -->

## 这是什么

Mantoz 生成一群虚构的人，让每个人做同一件任务，然后告诉你每个群体是怎么答的。这些人是生成出来的：年龄、收入、城市、习惯、在意什么。任务却是真的：问卷、客服对话、网页、桌面应用。除非你自己打开付费模型，数据不会离开你的机器。

## 它解决什么问题

你可以先上线一个表单，一个月后才发现五十岁以上的人没有一个填完。去问真实用户要花几周时间和一笔预算，这个阶段往往还没有。生成的人群替代不了他们，但能早点抓住那些明显的毛病：没人看懂的问题、有一群人始终没点到的按钮、你觉得清楚而别人看不懂的说法。

## 最大的优势

**最大的优势：** 判分由任务自带的检查程序给出，而且反复给很多次，不是只给一次。

**为什么这样更好：** 一个智能体跑一次，说明不了整个人群的情况。Mantoz 让每个人物把任务跑好几遍，每个任务带自己的检查程序，开放式回答交给两个评审：它们的分歧会被量出来，和原始回答一起存着。你读到的是分布，不是一次运气好的回答。

## 工作流程

五个步骤。每一步都在磁盘上留下文件，所以中断的运行可以从已经写下的地方继续。

<!-- workflow-diagram:start -->

<p align="center"><img src="docs/assets/pantheon/takt-zh.png" alt="五块大理石板排成一行，每块刻着一个步骤，一条金色带子从左边穿过它们的后面" width="100%"></p>

<!-- workflow-diagram:end -->

| 阶段 | 会发生什么 |
|---|---|
| 1. 人群 | 按照一套结构生成一群人物 |
| 2. 统计 | 用真实统计把人群往现实上拉 |
| 3. 跑任务 | 所有人跑同一个任务 |
| 4. 判分 | 任务自己判断这次回答算不算通过 |
| 5. 报告 | 把多次运行汇总，并按群体拆开 |

### 第 1 步：生成人群

你说明要多少人、用哪个随机种子。Mantoz 按四大类共四十个维度生成他们：出身、心理、能力、行为。一张依赖图让这些属性彼此自洽，不会出现十九岁的人却有三十年管理经验。

**你会得到：** 磁盘上一群可复现的人：同一个种子永远给出同一批人。

### 第 2 步：对齐真实统计

凭空抽出来的人群过于平滑，真实人口不是这样的。从公开统计来源导入边际分布，采样器就按这些占比走，而不是自己的默认值。随项目一起提供的，只有允许商业使用的来源。

**你会得到：** 各项占比与公开统计吻合的人群，旁边写着来源和它的许可证。

### 第 3 步：让所有人跑任务

任务放在四个环境之一：问卷表单、客服对话、网页、桌面应用。每个人物都要跑好几遍，因为一个智能体跑一次只能算轶事。执行通过 Harbor 完成，沙箱后端是配置里的一个开关：默认 Docker，愿意付费就用 Modal。

**你会得到：** 每次运行留下一条完整的记录，包括没通过的回答。

### 第 4 步：任务自己判分

每个任务带自己的检查程序，不会交给一个没见过评分标准的通用审阅者。开放式回答交给两个评审。它们的分歧会被量出来，两份原始文本都写进判定结果，这样奇怪的分数可以读出来，而不用猜。

**你会得到：** 每次运行一份判定，评审的原始输出被保留，不做压缩概括。

### 第 5 步：按群体读结果

单次运行会被汇总到整个人群和每个子群体的层面，聚合方法直接写进报告，而不是让人去猜。轻量查看器把这份报告变成一个 HTML 页面。没有第二个前端，没有构建步骤，也没有服务器。

**你会得到：** 一个页面，看得到每个群体怎么答，以及群体之间在哪里分歧。

## 快速开始

需要 macOS 或 Linux、Python 3.12 和 `uv`。想用沙箱环境还需要 Docker。下面三扇门，任选一扇。

```bash
git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz
cd ~/mantoz
python3 --version          # 3.12 or newer; the installer says so if yours is older
bash install.sh

claude                     # in Claude Code, then type /mantoz-setup
code .                     # or just open the project in your editor

uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json
uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html
```

没有 Git？下载 [ZIP 包](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip)，解压后在里面运行同样的 `bash install.sh`。不想 clone？`uv pip install git+https://github.com/zarubinvibe/mantoz.git` 直接从仓库安装这个包。 第一次用？在 Claude Code 里打开这个项目，运行 `/mantoz-setup`：安装以对话方式进行，一次问一个问题，没有你的同意不会安装任何东西。已经装过了？`/mantoz-update` 会更新到当前版本，并在动手之前先给你看有哪些改动。

第一次做这件事？[上手引导](docs/ONBOARDING.zh.md) 会一步一步带你走完第一次运行，并写清楚每条命令之后你会看到什么。

**你会得到：** 磁盘上的一份人群报告，以及一个可以用浏览器打开的 HTML 页面，按群体的拆分已经算好了。

## 简单对比

| 方案 | 适合什么时候 | 你会得到 | 代价是什么 | 在哪里运行 | 取舍 |
|---|---|---|---|---|---|
| **Mantoz** | 需要一整个人群回答，而人群还不存在 | 生成的人群、任务自带的判分、按群体拆分 | 免费；只有在线 LLM 评审要花钱 | 你自己的机器 | 生成的人不是真人：明显的问题会露出来，细微的可能不会 |
| 真实用户调研 | 这个决定很贵，必须找真人 | 真实客户的真实行为，连同所有意外 | 几周时间，加上调研公司或样本库的预算 | 现实世界里 | 太慢也太贵，没法对每个想法都跑一次 |
| 线上 A/B 测试 | 功能已经上线，流量也够大 | 真实规模上的真实行为 | 研发时间，外加放出一个坏版本的代价 | 你的生产服务器 | 等你知道的时候，用户已经先撞上了这个错误 |
| 问一个聊天机器人 | 只想快速判断措辞行不行 | 十秒钟就有答案 | 免费或者几分钱 | 别人的服务器 | 只有一个声音，没有分布，也没人反对 |
| MatrAIx-Persona-8B | 你要的就是那套已发表的研究装置 | 原始方法和一个非常大的公开语料 | 阅读免费；语料是研究许可 | 你的机器或集群 | 人物语料仅限研究使用，没有商业授权 |
| 手动问朋友和同事 | 今天需要一个基本判断，仅此而已 | 认识你的人给出的诚实反应 | 别人一个小时的好意 | 一个聊天窗口或者厨房 | 五个彼此相像的人构不成一个人群 |

## 简单词汇

| 词 | 简单解释 |
|---|---|
| Repository | 仓库：Git 保存并记录版本的项目文件夹 |
| Terminal | 终端：你输入命令的窗口 |
| Command | 命令：给电脑的一条指令 |
| Branch | 分支：不影响 `main` 的另一条修改线 |
| Pull Request | 合并请求：请别人审阅并接受你的修改 |
| Persona | 人物：一个生成出来的人，有年龄、收入、城市、习惯和价值观 |
| Population run | 人群运行：同一个任务发给很多人物，每人跑好几遍 |
| Verifier | 检查程序：属于任务本身的小程序，判断这次回答算不算通过 |
| Marginals | 边际分布：真实统计里各个答案的占比，用来把生成的人群往现实上拉 |

## 安全与隐私

- 全部在你自己的机器上跑。没有 Mantoz 服务器，也不需要注册账号。
- `data/` 不进 git。许可闸门会拒绝任何把调查数据、派生边际分布或模型权重带进去的提交。
- 自带的数据来源只有一个：通过 tochno.st 的俄罗斯统计局数据，CC BY 4.0，书面允许商业使用。
- 禁止转发的来源会被标成 `local_only`，由它派生的东西不会离开这台机器。
- LLM 评审默认关闭。除非你自己传 `--live-provider`，跑的是免费的确定性评审。
- 任务环境跑在 Docker 里。Modal 后端要单独打开，而且要花钱。

推送之前先读 `git diff`，再跑一次 `sh evals/licence_boundary_gate.sh`。

## 局限

状态：MVP 已经收口。十七个工单、四个环境都在跑，对等清单是绿的。

- 生成的人不是真实用户。结果是值得去验证的假设，不是证据。
- 目前的统计基础是俄罗斯数据。换一个国家，需要一个有同样书面许可的来源。
- 四个环境是故意做简单的：一个表单、一段对话、一个页面、一个桌面窗口。它们不是你的产品。
- 命令输出和报错信息是俄语。文档不是。

更深入：[对等清单](docs/PARITY.md) 把 Mantoz 与已发表的研究装置逐条对照，[术语表](docs/CONTEXT.md) 解释项目里用到的词。人物方法是作为研究借用的，并已引用：[arXiv:2608.04205](https://arxiv.org/abs/2608.04205)。智能体执行通过依赖 [Harbor](https://github.com/harbor-framework/harbor)（Apache-2.0）完成，见 [NOTICE](NOTICE)。

## 点亮星标与参与

觉得有用？给 Mantoz 点亮星标：[https://github.com/zarubinvibe/mantoz](https://github.com/zarubinvibe/mantoz)。这只要一秒，却决定别人能不能找到这个项目。

想改点什么？流程很短：先 fork 仓库，建一个分支 branch，提交 commit，推送 push，然后开一个 Pull Request。请不要直接向 `main` 推送，发布闸门会拒绝。

发现问题？到 [https://github.com/zarubinvibe/mantoz/issues](https://github.com/zarubinvibe/mantoz/issues) 开一个 issue，写清楚你运行了什么、发生了什么。

<!-- beginner-readme:end -->

<!-- pantheon-family:start -->
## Olympuz 家族

这是 [Olympuz 家族](https://github.com/zarubinvibe/athena#olympuz-family) 的公开项目之一。表格里的每一行都可以打开仓库，或者直接下载源码压缩包。

| 类型 | 名称 | 做什么 | 获取 |
|---|---|---|---|
| 项目 | Athena | 可携带的智能体操作系统：在新的 Mac 上重建 Claude 与 Codex 的工作环境。 | [仓库](https://github.com/zarubinvibe/athena) · [ZIP](https://github.com/zarubinvibe/athena/archive/refs/heads/main.zip) |
| 项目 | Helioz | 全天候的智能体工作传送带，带可验证的完成标记和按目标做出的夜间决策。 | [仓库](https://github.com/zarubinvibe/helioz) · [ZIP](https://github.com/zarubinvibe/helioz/archive/refs/heads/main.zip) |
| 项目 | Mnemazine | 本地优先的记忆系统：把原始材料变成可复用的、已核验的知识。 | [仓库](https://github.com/zarubinvibe/mnemazine) · [ZIP](https://github.com/zarubinvibe/mnemazine/archive/refs/heads/main.zip) |
| 项目 | Themiz | 面向俄罗斯诉讼的多智能体助手，本地识别扫描件，五位法学家组成合议审阅。 | [仓库](https://github.com/zarubinvibe/themiz) · [ZIP](https://github.com/zarubinvibe/themiz/archive/refs/heads/main.zip) |
| 项目 | Zeuz | 工作流工厂：把一个想法变成带规则、闸门、可观测性和回放的多智能体系统。 | [仓库](https://github.com/zarubinvibe/zeuz) · [ZIP](https://github.com/zarubinvibe/zeuz/archive/refs/heads/main.zip) |
| 项目 | Lynceuz | 以零成本收集公开网页证据；安全路径走完时，它会给出诚实的理由并停下。 | [仓库](https://github.com/zarubinvibe/lynceuz) · [ZIP](https://github.com/zarubinvibe/lynceuz/archive/refs/heads/main.zip) |
| 项目 | Iriz | macOS 菜单栏听写：语音在你自己的 Mac 上解码，键盘布局自动纠正，口述可以直接变成给智能体的任务。 | [仓库](https://github.com/zarubinvibe/iriz) · [ZIP](https://github.com/zarubinvibe/iriz/archive/refs/heads/main.zip) |
<!-- pantheon-family:end -->

## 许可证

MIT。见 [LICENSE](LICENSE)。
