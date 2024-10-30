# 钢铁雄心 4 模组管理器

<p style="text-align: left;">
  <a href="LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/Arama0517/hoi4-mods-manager"></a>
  <a href="../../actions/workflows/check.yml"><img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/Arama0517/hoi4-mods-manager/check.yml?label=CI"></a>
  <a href="../../releases/latest"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/Arama0517/hoi4-mods-manager"></a>
</p>

## 使用方式

1. 从[发行版](../../releases/latest)下载最新版本
2. 解压到游戏的根目录
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
  - [ ] 支持大部分 P 社游戏
  - [ ] 弃用官方客户端 (不通过启动 `dowser.exe` 的方式启动客户端, 而是直接运行游戏)
- [ ] 下载类
  - [x] 弃用 `steamcmd`
  - [x] 实现异步下载 Mod
  - [x] 实现实时分配文件
  - [ ] 实现使用类似 `aria2` 的多线程下载文件方式
- [ ] GUI

# 开发

## 环境要求

- [python `3.12.*`](https://www.python.org/downloads/) `nuitka`尚未支持 `3.13.*`
- [pdm](https://pdm-project.org/zh-cn/latest/)
- [VS 2022 Build Tools](https://visualstudio.microsoft.com/zh-hans/downloads/#build-tools-for-visual-studio-2022) `nuitka` 编译 (可选)

## 初始化项目

1. 克隆本项目
2. 在项目根目录创建一个 `launcher-settings.json`, 内容:

```json
{
  "gameId": "hoi4"
}
```

3. 运行 `pdm install`
```
