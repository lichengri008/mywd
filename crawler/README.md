# GMGN交易量爬虫

这是一个使用Playwright实现的爬虫，用于从GMGN网站获取加密货币交易对的交易量数据。

## 功能特性

- 支持获取单个或多个交易对的交易量数据
- 自动处理页面元素查找和数据提取
- 支持截图保存，便于调试
- 数据保存为JSON格式
- 内置反爬虫措施（延迟、用户代理等）

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

## 使用方法

### 基本使用

```python
from gmgn import GMGNCrawler
import asyncio

async def main():
    crawler = GMGNCrawler(headless=False)
    await crawler.start_browser()
    
    # 获取BTC/USDT交易量
    data = await crawler.get_trading_volume("BTC/USDT")
    print(data)
    
    await crawler.close_browser()

asyncio.run(main())
```

### 获取多个交易对数据

```python
async def main():
    crawler = GMGNCrawler()
    await crawler.start_browser()
    
    symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    results = await crawler.get_multiple_symbols_volume(symbols)
    
    for result in results:
        print(f"{result['symbol']}: {result['volume_data']}")
    
    await crawler.close_browser()
```

### 直接运行脚本

```bash
python gmgn.py
```

## 输出数据格式

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

## 配置选项

- `headless`: 是否使用无头模式（默认True）
- `base_url`: GMGN网站地址
- 浏览器参数：已优化以避免检测

## 注意事项

1. 首次运行需要安装Playwright浏览器
2. 建议设置适当的延迟避免被反爬
3. 如果页面结构变化，可能需要更新选择器
4. 程序会自动保存截图用于调试

## 故障排除

如果遇到问题：

1. 检查网络连接
2. 查看控制台输出的错误信息
3. 检查保存的截图文件
4. 尝试调整等待时间
5. 更新CSS选择器或XPath

## 法律声明

请确保遵守目标网站的使用条款和robots.txt文件。本工具仅用于学习和研究目的。
