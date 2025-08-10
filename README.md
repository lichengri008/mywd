# GMGN交易量爬虫项目

这是一个使用Playwright实现的完整爬虫项目，用于从GMGN网站获取加密货币交易对的交易量数据。

## 🚀 项目特性

- **智能爬取**: 使用Playwright自动浏览器控制，支持动态页面
- **多交易对支持**: 可同时获取多个交易对的数据
- **灵活配置**: 支持开发、测试、生产环境配置
- **数据导出**: 自动保存为JSON格式，便于后续分析
- **反爬虫措施**: 内置延迟、用户代理等防护机制
- **调试友好**: 支持截图保存，便于问题排查

## 📁 项目结构

```
crawler/
├── gmgn.py              # 主要爬虫类
├── config.py            # 配置文件
├── run_crawler.py       # 命令行启动脚本
├── quick_start.py       # 快速演示脚本
├── test_crawler.py      # 测试脚本
├── setup.py             # 环境安装脚本
├── requirements.txt     # Python依赖
└── README.md           # 详细使用说明
```

## 🛠️ 快速开始

### 1. 环境准备

```bash
# 进入crawler目录
cd crawler

# 运行自动安装脚本
python setup.py
```

### 2. 基本使用

```bash
# 获取BTC/USDT交易量
python run_crawler.py BTC/USDT

# 获取多个交易对数据
python run_crawler.py BTC/USDT ETH/USDT BNB/USDT

# 使用无头模式（后台运行）
python run_crawler.py BTC/USDT --headless
```

### 3. 交互式演示

```bash
# 运行快速演示
python quick_start.py
```

## 📊 数据格式

爬虫获取的数据包含以下信息：

```json
{
  "symbol": "BTC/USDT",
  "timestamp": "2024-01-01T12:00:00",
  "volume_data": {
    "24h_volume": "1,234,567 BTC",
    "current_price": "$45,000",
    "24h_change": "+2.5%"
  },
  "status": "success"
}
```

## ⚙️ 配置选项

### 环境配置

通过环境变量设置运行环境：

```bash
# 开发环境（显示浏览器，较慢）
export CRAWLER_ENV=dev

# 生产环境（无头模式，较快）
export CRAWLER_ENV=prod

# 测试环境
export CRAWLER_ENV=test
```

### 自定义配置

编辑 `config.py` 文件来自定义：

- 浏览器参数
- 延迟时间
- 选择器配置
- 文件路径等

## 🔧 高级用法

### 编程方式使用

```python
from gmgn import GMGNCrawler
import asyncio

async def main():
    crawler = GMGNCrawler(headless=False)
    await crawler.start_browser()
    
    # 获取单个交易对数据
    data = await crawler.get_trading_volume("BTC/USDT")
    print(data)
    
    # 获取多个交易对数据
    results = await crawler.get_multiple_symbols_volume(["BTC/USDT", "ETH/USDT"])
    
    await crawler.close_browser()

asyncio.run(main())
```

### 批量处理

```python
# 自定义交易对列表
symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT"]
results = await crawler.get_multiple_symbols_volume(symbols)
```

## 🧪 测试

运行测试脚本验证功能：

```bash
# 运行完整测试
python test_crawler.py

# 测试特定功能
python -c "
import asyncio
from test_crawler import test_single_symbol
asyncio.run(test_single_symbol())
"
```

## 📝 日志和调试

### 截图保存

爬虫会自动保存页面截图用于调试：

```
screenshots/
└── gmgn_screenshot_1234567890.png
```

### 数据文件

获取的数据自动保存：

```
data/
├── btc_data_20240101_120000.json
├── batch_data_20240101_120000.json
└── gmgn_trading_data.json
```

## 🚨 注意事项

1. **遵守规则**: 请遵守目标网站的使用条款和robots.txt
2. **频率控制**: 建议设置适当的延迟避免被反爬
3. **数据准确性**: 爬取的数据仅供参考，请以官方数据为准
4. **法律合规**: 仅用于学习和研究目的

## 🐛 故障排除

### 常见问题

1. **浏览器启动失败**
   ```bash
   # 重新安装浏览器
   playwright install chromium
   ```

2. **页面元素找不到**
   - 检查网络连接
   - 查看截图文件
   - 更新选择器配置

3. **数据获取失败**
   - 检查交易对格式
   - 增加等待时间
   - 查看错误日志

### 调试技巧

1. 使用非无头模式观察爬取过程
2. 查看保存的截图文件
3. 检查控制台输出信息
4. 调整配置文件中的延迟参数

## 📚 相关资源

- [Playwright官方文档](https://playwright.dev/python/)
- [Python异步编程](https://docs.python.org/3/library/asyncio.html)
- [Web爬虫最佳实践](https://www.scrapingbee.com/blog/web-scraping-best-practices/)

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

---

**免责声明**: 本工具仅用于技术学习和研究，使用者需自行承担使用风险，开发者不承担任何法律责任。
