# Mantoz

先在五百个并不存在的人身上试一遍你的想法。

[English](README.md) · [Русский](README.ru.md)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Stars](https://img.shields.io/github/stars/zarubinvibe/mantoz?style=flat&color=C9A87A)](https://github.com/zarubinvibe/mantoz/stargazers) [![Status](https://img.shields.io/badge/status-working-brightgreen.svg)](https://github.com/zarubinvibe/mantoz) [![Olympuz](https://img.shields.io/badge/olympuz-family-B8D6EA.svg)](https://github.com/zarubinvibe/athena#olympuz-family)

<p align="center"><img src="docs/assets/pantheon/hero.png" alt="白色大理石的曼托手托占卜浅盘，身旁站着一小排大理石人像，蓝色细线沿地面进入盘中，三条金色带子从盘中通向刻着字的石板，右侧立着家族的古典石柱" width="100%"></p>

<!-- owner-welcome:start -->

> 你好。我叫 Filipp Zarubin。我是律师，业余用 vibe-coding 的方式做产品：点子远比时间多，而且每一个在别人碰到它之前，看上去都很有说服力。
>
> 认真验证它们很贵。我不是研究员也不是市场人员，去下单做一次调研，我会多花钱，还照样问错问题。所以我给自己攒了一支并不存在的焦点小组，每个新想法在我为它花掉一个月之前，都先从这里过一遍。
>
> 它替代不了真实用户，这一点我不打算含糊。它只是把那些一碰就散的想法先筛掉。说实话，看着五百个虚构的人跟你的措辞较劲，本身就挺过瘾的。
>
> Mantoz 属于 [Olympuz 工具家族](https://github.com/zarubinvibe/athena#olympuz-family)，它们遵循同一套规则。
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

Mantoz 给你攒一支并不存在的焦点小组。每个人都有自己的年龄、收入、城市、习惯和在意的东西，而且这些特征彼此挂钩，所以不会冒出一个有三十年管理经验的十九岁的人。接着他们每一个都要走一遍你的任务：填表单、给客服写信、点你的网页、在应用里操作。

## 它解决什么问题

你有了一个想法。拿真人去验证要花几周和一笔钱，而如果你不是做调研出身，还多半会做砸：问错问题、抽错样本、得出错的结论。Mantoz 给你第一轮。它不会告诉你客户在想什么，但会告诉你哪句话站不住、哪个按钮有一群人根本走不到、哪些小城市的四十岁用户的回答跟你预想的完全不一样。

## 最大的优势

**最大的优势：** 判分由任务自带的检查程序给出，你让它判几遍它就判几遍。

**为什么这样更好：** 问模型一次，你得到一个答案，方差为零。这里每个人要把任务跑好几遍，开放式回答交给两个评审，它们之间的分歧会被量出来，原始文本留在判定结果里。你看到的是分布，不是一句运气好的回答。

## 工作流程

五个步骤。每一步都在磁盘上留下文件，所以中断的运行会从停下的地方接着走。

<!-- workflow-diagram:start -->

<p align="center"><img src="docs/assets/pantheon/takt-zh.png" alt="五块大理石板排成一行，每块刻着一个步骤，一条金色带子从左边穿过它们的后面" width="100%"></p>

<!-- workflow-diagram:end -->

| 阶段 | 会发生什么 |
|---|---|
| 1. 造人 | 按一套结构生成五百个虚构的人 |
| 2. 对齐 | 用真实统计让他们像一个国家 |
| 3. 跑任务 | 他们每一个都走一遍你的任务 |
| 4. 判分 | 任务自己判断这次回答算不算通过 |
| 5. 报告 | 把回答汇总，并按群体拆开 |

### 第 1 步：生成这些人

你说明要多少人、用哪个随机种子。Mantoz 按四大类共四十个特征生成他们：出身、心理、能力、行为。一张依赖图让这些特征彼此自洽，不会出现十九岁却有三十年管理经验的人。

<p align="center"><img src="docs/assets/pantheon/stage-1-population.png" alt="长桌上的大理石模具，旁边已经成排站着十二个一模一样的小人像" width="100%"></p>

**你会得到：** 磁盘上一批可复现的人：同一个种子永远给你同样的五百个。

### 第 2 步：对齐真实统计

凭空抽出来的人太平滑了，真实的国家不是这样。从公开统计来源导入各项占比，采样器就按这些走，而不是自己的默认值。随项目提供的，只有允许商业使用的来源。

<p align="center"><img src="docs/assets/pantheon/stage-2-ground.png" alt="五块高低不同的大理石板，每块前面站着一组人像，数量与板的高度相符" width="100%"></p>

**你会得到：** 各项占比与公开统计吻合的人，旁边写着来源和它的许可证。

### 第 3 步：让他们跑任务

任务放在四个环境之一：问卷表单、客服对话、网页、应用窗口。每个人都要跑好几遍，因为一个智能体跑一次只能算轶事。执行通过 Harbor 完成，沙箱是配置里的一个开关：默认 Docker，愿意付费就用 Modal。

<p align="center"><img src="docs/assets/pantheon/stage-3-run.png" alt="一道大理石门，一列一模一样的小人像沿着一条蓝线从左到右穿过它" width="100%"></p>

**你会得到：** 每次运行留下一条完整记录，包括没通过的回答。

### 第 4 步：任务自己判分

每个任务带自己的检查程序，不会交给一个没见过评分标准的通用审阅者。开放式回答交给两个评审。它们的分歧会被量出来，两份原始文本都写进判定结果，这样奇怪的分数可以读出来，而不用猜。

<p align="center"><img src="docs/assets/pantheon/stage-4-verify.png" alt="一架大理石天平，一边是刻着凹槽的石板，另一边是素净的砝码，两侧各立着一枚印章" width="100%"></p>

**你会得到：** 每次运行一份判定，评审的原始输出被保留，不做压缩概括。

### 第 5 步：按群体读结果

单次运行会被汇总到全体和每个群体两个层面，聚合方法直接写进报告，而不是让人去猜。轻量查看器把这份报告变成一个 HTML 页面。没有第二个前端，没有构建步骤，也没有服务器。

<p align="center"><img src="docs/assets/pantheon/stage-5-report.png" alt="九条蓝线在大理石块处汇合，再以三条长短不同的金色带子离开，落成石板上的凹槽" width="100%"></p>

**你会得到：** 一个页面，看得到每个群体怎么答，以及群体之间在哪里分开。

## 快速开始

需要 macOS 或 Linux、Python 3.12 和 `uv`。想跑任务环境本身还需要 Docker。下面三扇门，任选一扇。

```bash
git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz
cd ~/mantoz
python3 --version          # 3.12 или новее; установщик скажет, если у тебя старее
bash install.sh

claude                     # в Claude Code дальше набери /mantoz-setup
code .                     # или просто открой проект в редакторе

uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json
uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html
```

没有 Git？下载 [ZIP 包](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip)，解压后在里面运行同样的 `bash install.sh`。不想 clone？`uv pip install git+https://github.com/zarubinvibe/mantoz.git` 直接从仓库安装。第一次用？在 Claude Code 里打开项目并运行 `/mantoz-setup`：安装以对话方式进行，一次一个问题，没有你的同意不会往磁盘上写任何东西。已经装过了？`/mantoz-update` 会更新到当前版本，并在动手前先给你看改了什么。

第一次做这件事？[上手引导](docs/ONBOARDING.zh.md) 会一步一步带你走完第一次运行，并写清楚每条命令之后你会看到什么。

**你会得到：** 磁盘上的一份报告，以及一个 HTML 页面：每个群体怎么答、群体之间在哪里分开，都看得见。

## 简单对比

| 验证方式 | 适合什么时候 | 你会得到 | 代价是什么 | 在哪里运行 | 取舍 |
|---|---|---|---|---|---|
| **Mantoz** | 想法还只是想法，你需要第一轮反馈 | 五百份回答，按年龄、收入和城市拆开 | 免费，除非你自己打开在线评审 | 你自己的机器 | 这些人是虚构的：明显的问题会露出来，细微的可能不会 |
| 请调研公司 | 这个决定很贵，还要拿去说服投资人 | 真实客户的真实行为，由懂行的人收集 | 几周时间，每一轮都要预算 | 现实世界里 | 对一个你周五可能就放弃的想法来说，太慢也太贵 |
| 线上 A/B 测试 | 功能已经做好，流量也够 | 真实规模上的真实行为，不用猜 | 研发时间，加上一个坏版本的代价 | 你的生产服务器 | 等你知道的时候，用户已经先撞上了这个错误 |
| 问模型一次 | 只想凭感觉判断某一句话 | 十秒钟就有答案 | 免费或者几分钱 | 别人的服务器 | 只有一个声音，没有分布，屋里没人反对你 |
| MatrAIx-Persona-8B | 你要的就是那套已发表的研究装置 | 原始方法和一个非常大的公开语料 | 阅读免费，使用受研究许可限制 | 你的机器或集群 | 人物语料仅限研究使用，没有商业授权 |
| 问朋友和同事 | 今天需要一个基本判断，仅此而已 | 认识你的人给出的诚实反应 | 别人一个小时的好意 | 一个聊天窗口或者厨房 | 五个彼此相像的人，没法彼此不同意 |

## 简单词汇

| 词 | 简单解释 |
|---|---|
| Repository | 仓库：Git 保存并记录版本的项目文件夹 |
| Terminal | 终端：你输入命令的窗口 |
| Command | 命令：给电脑的一条指令 |
| Branch | 分支：不影响 `main` 的另一条修改线 |
| Pull Request | 合并请求：请别人审阅并接受你的修改 |
| Persona | 人物：一个虚构的人，年龄、收入、城市、习惯、价值观彼此挂钩，不会自相矛盾 |
| Population run | 人群运行：同一个任务发给几百个这样的人，每人跑好几遍 |
| Verifier | 检查程序：属于任务本身的小程序，判断这次回答算不算通过 |
| Marginals | 边际分布：真实统计里各个答案的占比，用它让虚构的人看起来像一个国家 |

## 安全与隐私

- 全部在你自己的机器上跑。没有 Mantoz 服务器，也不需要注册账号。
- `data/` 不进 git。许可闸门会拒绝任何把调查数据、派生数字或模型权重带进去的提交。
- 随项目提供的统计来源只有一个：通过 tochno.st 的俄罗斯统计局数据，CC BY 4.0，书面允许商业使用。
- 禁止再转交数据的来源会被标成 `local_only`，由它派生的东西不会离开你的机器。
- 在线 LLM 评审默认关闭。除非你自己传 `--live-provider`，判分由免费的确定性评审完成。
- 任务环境跑在 Docker 里。Modal 后端要单独打开，而且要花钱。

推送之前先读 `git diff`，再跑一次 `sh evals/licence_boundary_gate.sh`。

## 局限

状态：MVP 已经收口。十七个工单、四个环境都在跑，对等清单是绿的。

- 这些人是虚构的。结果是值得去验证的假设，不是可以引用的证据。
- 他们背后的统计是俄罗斯数据。换一个国家，需要一个有同样书面许可的来源。
- 四个环境是故意做简单的：一个表单、一段对话、一个页面、一个应用窗口。它们不是你的产品。
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
| 项目 | Mantoz | 把一个想法摆到五百个并不存在的人面前，然后告诉你每个群体是怎么答的。 | [仓库](https://github.com/zarubinvibe/mantoz) · [ZIP](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip) |
| 项目 | Koiz | 所有项目共用一份教训库。每次失败都追到原因，原因不被钩子、闸门或测试关掉，就一直挂在那里。 | [仓库](https://github.com/zarubinvibe/koiz) · [ZIP](https://github.com/zarubinvibe/koiz/archive/refs/heads/main.zip) |
<!-- pantheon-family:end -->

## 许可证

MIT。见 [LICENSE](LICENSE)。
