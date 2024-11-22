# P社游戏模组管理器

<p style="text-align: left;">
  <a href="LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/Arama0517/hoi4-mods-manager"></a>
  <a href="../../actions/workflows/check.yml"><img alt="GitHub Actions Workflow Status" src="https://github.com/Arama0517/paradox-game-mod-manager/actions/workflows/check.yml/badge.svg"></a>
  <a href="../../releases/latest"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/Arama0517/hoi4-mods-manager"></a>
</p>

## 使用方式

1. 从[发行版](../../releases/latest)下载最新版本
2. 将文件解压到 `dowser.exe` 文件的同一目录内
3. 运行

## 常见问题

### 登录错误

- 内置账号不一定可用, 请添加一个自己的账号或稍后再试

### 什么是创意工坊 ID?

- 例如:
- 创意工坊链接为 `https://steamcommunity.com/sharedfiles/filedetails/?id=123456789`
- 则创意工坊 ID 为 `123456789`

### 下载失败

- 如果启动了加速器请尝试更换节点或重启加速器

### 其他错误

- 请提出 [issue](../../issues)

## 完成的功能

- [ ] 功能类
  - [x] 模组管理
  - [x] 生成模组定位文件
  - [x] 设置页
  - [ ] 弃用官方客户端 (不通过启动 `dowser.exe` 的方式启动客户端, 而是直接运行游戏)
- [ ] 支持的P社游戏
  - [x] 钢铁雄心4
  - [x] 维多利亚3
  - [ ] ...
- [ ] 下载类
  - [x] 弃用 `steamcmd`
  - [x] 实现异步下载 Mod
  - [x] 实现实时分配文件
  - [ ] 实现使用类似 `aria2` 的多线程下载文件方式
- [ ] GUI

# 开发

## 环境要求

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [VS 2022 Build Tools](https://visualstudio.microsoft.com/zh-hans/downloads/#build-tools-for-visual-studio-2022) `nuitka` 编译需要 _可选_
- [task](https://taskfile.dev/installation/) 类似 `make` _可选, 但是建议安装_

## 初始化项目

1. 克隆本项目
2. 运行 `uv sync`
3. 运行 `uv run -m tools.setup_project`

## uv 换源
### 下载 `python`
1. 设置环境变量: `UV_PYTHON_INSTALL_MIRROR` 为 `https://ghp.ci/https://github.com/indygreg/python-build-standalone/releases/download`

### 下载依赖
1. 进入 `~\AppData\Roaming\uv` _如果没有这个目录就新建一个_
2. 新建并打开 `uv.toml` 文件, 内容:
```toml
index-url = "https://mirrors.aliyun.com/pypi/simple"
```