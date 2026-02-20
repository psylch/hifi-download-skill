# hifi-download-skill

[English](README.md)

一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能，用于音乐发现和高品质音频下载。结合 Spotify、Last.fm 进行音乐探索，通过 Qobuz、TIDAL 下载无损音频。

| 步骤 | 做了什么 | 使用的服务 |
|------|---------|-----------|
| **发现** | 搜索音乐，查找相似艺人/曲目 | Spotify, Last.fm |
| **推荐** | 基于听歌历史的个性化推荐 | Spotify + Last.fm |
| **搜索** | 在下载平台搜索专辑/曲目 | Qobuz, TIDAL |
| **下载** | 以无损品质下载（FLAC/Hi-Res） | Qobuz, TIDAL |

## 安装

### 通过 skills.sh（推荐）

```bash
npx skills add psylch/hifi-download-skill -g -y
```

### 通过 Claude Code Plugin Marketplace

```shell
/plugin marketplace add psylch/hifi-download-skill
/plugin install hifi-download@psylch-hifi-download-skill
```

安装后需重启 Claude Code。

## 前置条件

- **Python 3** 已安装
- **API 凭证**（至少配置一个发现服务）：
  - Spotify：免费账号 + API 凭证（[developer.spotify.com](https://developer.spotify.com/dashboard)）
  - Last.fm：免费 API Key（[last.fm/api](https://www.last.fm/api/account/create)）
- **订阅**（下载服务，可选）：
  - Qobuz：Studio 或 Sublime 订阅
  - TIDAL：HiFi+ 订阅

## 使用方法

在 Claude Code 中使用以下触发短语：

```
帮我找类似 Radiohead 的音乐
根据我的口味推荐歌曲
下载 OK Computer 的 Hi-Res 版本
搜索 FLAC 专辑
配置音乐服务
```

## 工作原理

1. **环境搭建** — 安装依赖，配置 API 凭证
2. **状态检查** — 确认哪些服务可用
3. **音乐发现** — 搜索 Spotify，通过 Last.fm 查找相似艺人/曲目
4. **个性化推荐** — 结合 Spotify 听歌历史与 Last.fm 全球数据
5. **下载** — 搜索 Qobuz/TIDAL 曲库，以配置的品质下载

## 支持的服务

| 服务 | 类型 | 要求 |
|------|------|------|
| Spotify | 发现 | 免费账号 + API 凭证 |
| Last.fm | 发现 | 免费 API Key |
| Qobuz | 下载 | Studio/Sublime 订阅 |
| TIDAL | 下载 | HiFi+ 订阅 |

## 文件结构

```
hifi-download-skill/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── skills/
│   └── hifi-download/
│       ├── SKILL.md              # 主 Skill 定义
│       ├── run.sh                # 虚拟环境感知的脚本运行器
│       ├── .env.example          # 凭证模板
│       ├── references/
│       │   ├── setup_guide.md    # 详细安装指南
│       │   └── musicmaster.md    # 完整脚本参考
│       └── scripts/
│           ├── setup.sh          # 环境安装
│           ├── setup_config.py   # 凭证配置
│           ├── status.py         # 服务状态检查
│           ├── spotify_*.py      # Spotify 脚本
│           ├── lastfm_*.py       # Last.fm 脚本
│           ├── platform_*.py     # Qobuz/TIDAL 脚本
│           └── lib/              # 共享模块
├── README.md
├── README.zh.md
└── LICENSE
```

## 致谢

本项目依赖以下开源工具：

- **[tiddl](https://github.com/oskvr37/tiddl)** - TIDAL 下载器，作者 [@oskvr37](https://github.com/oskvr37)
- **[qobuz-dl](https://github.com/vitiko98/qobuz-dl)** - Qobuz 下载器，作者 [@vitiko98](https://github.com/vitiko98)

## 免责声明

本工具仅供**个人使用**，出于学习目的创建。

- 本项目**与** TIDAL、Qobuz、Spotify、Last.fm **无关联**
- 用户须确保其使用符合相关服务的使用条款及当地版权法律
- 下载内容仅供个人使用，不得分享或再分发
- 开发者对本工具的任何滥用**不承担责任**

使用本软件即表示同意以上条款。

## 许可证

MIT
