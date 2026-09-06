# 上手引导：你的第一次 Mantoz 运行

<p align="center"><img src="assets/pantheon/doc-onboarding.png" alt="日光下低台上的大理石浅盘，前面站着一个小小的大理石人像，地面上有一条蓝色细线，右侧是家族石柱" width="100%"></p>

写给从没做过这件事的人。每一步都写清楚要敲什么、敲完之后屏幕上会出现什么。整个过程大约十五分钟，大部分时间在等下载。

做完你会得到：一份报告，里面是几百个生成出来的人填同一份问卷的结果；还有一个 HTML 页面，看得到每个群体是怎么答的。

---

## 第 1 步：打开终端

macOS 上按 `Cmd + 空格`，输入 `Terminal`，回车。Linux 上打开你的终端程序。

**屏幕上：** 一个窗口，提示符以 `$` 或 `%` 结尾。命令就敲在那里。

## 第 2 步：确认有 Python

```bash
python3 --version
```

**屏幕上：** 类似 `Python 3.12.4`。如果版本低于 3.12，也不要停，第 4 步会装上合适的版本，而且不会动你系统里的 Python。如果这条命令根本找不到，先去 [python.org](https://www.python.org/downloads/) 装 Python。

## 第 3 步：把代码拿下来

```bash
git clone https://github.com/zarubinvibe/mantoz.git ~/mantoz
cd ~/mantoz
```

**屏幕上：** 几行数对象的输出，最后是 `Resolving deltas: 100%`。`cd` 之后提示符里一般会出现 `mantoz`。

机器上没有 Git？下载 [ZIP 包](https://github.com/zarubinvibe/mantoz/archive/refs/heads/main.zip)，解压后 `cd` 进解压出来的文件夹。

## 第 4 步：安装 uv

`uv` 负责搭环境、拉 Harbor。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**屏幕上：** 一行进度，然后是 `installed uv`。关掉终端重新打开，或者运行 `source ~/.bashrc`，让 shell 找得到这条新命令。用 `uv --version` 确认。

## 第 5 步：运行安装脚本

```bash
bash install.sh
```

**屏幕上：** 它找到的 Python 版本，然后是 `dependencies installed, Harbor included`，接着是一串以 `ok` 开头的检查，最后是 `all 21 checks passed`。

以 `!!` 开头的行要读完：安装脚本会直接说缺什么、用哪条命令补上。现在缺 Docker 没关系。

## 第 6 步：生成一群人，看一眼

```bash
uv run python -m mantoz.persona sample --n 200 --seed 7 --dag --out runs/people.json
```

**屏幕上：** 什么都没有，这说明成功了。`runs/people.json` 里现在有两百个生成的人。打开它，或者数一下：

```bash
python3 -c "import json;print(len(json.load(open('runs/people.json'))))"
```

**屏幕上：** `200`。

`--seed 7` 这部分很关键：同一条命令再跑一次，得到的还是那两百个人。换个种子，就是另一群人。

## 第 7 步：让这群人做一份问卷

```bash
uv run python -m mantoz.population run --n-runs 3 --seed 7 --task survey --out runs/first.json
```

**屏幕上：** 运行过程中的进度行，然后命令结束。`--n-runs 3` 表示每个人物答三次，因为一次回答说明不了一个人，更说明不了一群人。

**如果因为 Docker 报错停下：** 问卷环境需要 Docker。安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)，启动它，再跑一次这条命令。

## 第 8 步：把报告变成页面

```bash
uv run python -m mantoz.viewer render --report runs/first.json --out runs/first.html
open runs/first.html
```

Linux 上把 `open` 换成 `xdg-open runs/first.html`。

**屏幕上：** 浏览器里的一个页面，有总体结果、按群体的拆分，以及写明白的聚合方法，而不是让你去猜。

## 第 9 步：提交任何东西之前，先检查许可边界

```bash
sh evals/licence_boundary_gate.sh
```

**屏幕上：** `лицензионная граница: цела`（许可边界完好）。这道闸门不让调查数据、派生的边际分布和模型权重进入 git。每次推送前都跑一次，尤其是你自己加了数据来源之后。

## 第 10 步：换一个环境试试

问卷只是四个环境之一。换个任务，同一群人就会去走客服对话、网页或者桌面应用：

```bash
uv run python -m mantoz.population run --n-runs 3 --seed 7 --task chat --out runs/chat.json
```

**屏幕上：** 同样形状的输出，只是来自另一个环境。

---

## 怎么更新

新版本会不时发布。在 Claude Code 里运行 `/mantoz-update`：它会先给你看有哪些改动，再动手；只做快进式拉取；不碰你的 `data/`、运行结果和 `.env`；更新完再把两项检查重跑一遍。没有智能体的话，手动做同样的事：

```bash
cd ~/mantoz
git pull --ff-only origin main
uv pip install -e .
bash scripts/mantoz-selfcheck.sh --selftest
```

**屏幕上：** 拉下来的提交列表，然后检查再次全部通过。

## 接下来看什么

- [对等清单](PARITY.md)：Mantoz 逐条有什么，以及有意不做什么。
- [决定记录](DECISIONS.md)：为什么沙箱可切换，为什么 Harbor 是依赖，为什么有一个数据源在条款被认真读过之后被剔除了。
- [术语表](CONTEXT.md)：项目里用到的词。

## 如果这些对你有用

给项目点亮星标：[https://github.com/zarubinvibe/mantoz](https://github.com/zarubinvibe/mantoz)。这只要一秒，却决定别人能不能找到它。

想改点什么？流程很短：先 fork 仓库，建一个分支 branch，提交 commit，推送 push，然后开一个 Pull Request。请不要直接向 `main` 推送，发布闸门会拒绝。细节见 [CONTRIBUTING.zh.md](../CONTRIBUTING.zh.md)。

发现问题？到 [https://github.com/zarubinvibe/mantoz/issues](https://github.com/zarubinvibe/mantoz/issues) 开一个 issue，写清楚你运行了什么、发生了什么。
