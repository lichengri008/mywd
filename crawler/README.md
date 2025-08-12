# Playwright 实现爬虫
 
## 📁 项目结构

```
crawler/
├── config.py            # 配置文件（可以忽略）
├── setup.py             # 环境安装脚本（可以单独运行，可以仔细看下）
├── gmgn_crawler.py      # 主要爬虫类
├── requirements.txt     # Python依赖
└── README.md            # 详细使用说明
```
 
## 使用方法

#### 1.安装vscode 插件: python相关插件都装一下

<img src="../docs/images/pyallext.png" alt="Extensions" width="400px">


- setup.py    初始化环境（可以单独运行，可以仔细看下）
  1. 检查是否安装Python，以及版本
  2. 安装项目依赖， playwright  
  3. 安装Chromium
  4. 创建必要目录: data, logs, screenshots

#### 2. 避免被 Cloudflare 拦截的建议

- 使用本机 Chrome 通道与持久化用户数据目录，指纹更贴近真实用户。
- 设置 `CRAWLER_PROXY` 环境变量以使用住宅代理，如：

```bash
export CRAWLER_PROXY="http://user:pass@host:port"
```

- 可自定义指纹相关环境变量：

```bash
export CRAWLER_USER_AGENT="Mozilla/5.0 ... Chrome/126.0.0.0 Safari/537.36"
export CRAWLER_ACCEPT_LANGUAGE="en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
export CRAWLER_LOCALE="en-US"
export CRAWLER_TZ="Asia/Shanghai"
```

- 首次运行建议手动通过一次验证，后续将复用 `~/.mywd/playwright/gmgn` 的持久化状态。
