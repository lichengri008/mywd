#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMGN交易量爬虫
使用Playwright获取指定币种的交易量数据
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Optional, List
from playwright.async_api import async_playwright, Browser, Page


from config import current_config

class GMGNCrawler:
    #语法解释: """...""" 是文档字符串， 用来描述这个类的功能。
    """GMGN交易量爬虫类"""
    
    def __init__(self, headless: bool = None):
        self.headless = headless if headless is not None else current_config.HEADLESS
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.base_url = current_config.BASE_URL
        
    async def start_browser(self):
        """启动浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=current_config.get_browser_args()
        )
        
        # 创建新页面
        self.page = await self.browser.new_page()
        
        # 设置用户代理
        await self.page.set_extra_http_headers({
            'User-Agent': current_config.USER_AGENT
        })
        
        # 设置视口大小
        await self.page.set_viewport_size({
            "width": current_config.VIEWPORT_WIDTH, 
            "height": current_config.VIEWPORT_HEIGHT
        })    

    async def get_volume_by_token(self, token: str = "") -> Dict:

        try:
            chain = "bsc"
            url = f"{self.base_url}/{chain}/token/{token}" 
            # 访问GMGN主页
            print(f"正在访问 {url}...")

            # 打开浏览器
            await self.page.goto(url)

            await asyncio.sleep(3)
            
            # 查找 id为 MainDomId的<main> 中，内容为"24h Vol"的span，对应的父元素的父元素的，最后一个子元素div内的内容
            try:
                # 首先找到包含"24h Vol"文本的span元素
                vol_span = await self.page.wait_for_selector('main#MainDomId span:has-text("24h Vol")', timeout=5000)
                if vol_span:
                    print("找到24h Vol span元素")
                    
                    # 获取span的父元素
                    parent_element = await vol_span.query_selector('xpath=..')
                    if parent_element:
                        print("找到父元素")
                        
                        # 获取父元素的父元素
                        grandparent_element = await parent_element.query_selector('xpath=..')
                        if grandparent_element:
                            print("找到祖父元素")
                            
                            # 获取祖父元素的最后一个子元素div
                            last_div = await grandparent_element.query_selector('div:last-child')
                            if last_div:
                                print("找到最后一个子元素div")
                                
                                # 获取div内的内容
                                div_content = await last_div.text_content()
                                print(f"最后一个子元素div的内容: {div_content}")
                                
                                # 也可以获取HTML内容
                                div_html = await last_div.inner_html()
                                print(f"最后一个子元素div的HTML: {div_html}")
                            else:
                                print("未找到最后一个子元素div")
                        else:
                            print("未找到祖父元素")
                    else:
                        print("未找到父元素")
                else:
                    print("未找到24h Vol span元素")
            except Exception as e:
                print(f"查找24h Vol元素时出错: {e}")
            # 24h Vol
            
        except Exception as e:
            print(f"获取交易量数据时出错: {e}")
            return {
                "symbol": token,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }

    async def get_trading_volume(self, symbol: str = "BTC/USDT") -> Dict:
        """
        获取指定币种的交易量数据
        
        Args:
            symbol: 交易对符号，如 "BTC/USDT"
            
        Returns:
            包含交易量信息的字典
        """

        try:
            # 访问GMGN主页
            print(f"正在访问 {self.base_url}...")

            # 打开浏览器
            await self.page.goto(self.base_url)

            await asyncio.sleep(3)
            
            # 等待页面加载 - 等待header中的Log In按钮出现
            print("等待 Log In按钮已出现")
            await self.page.wait_for_selector('header button#loginBtn', timeout=5000)
            print("页面加载完成，Log In按钮已出现")
            
            # 查找登陆弹窗的关闭按钮
            try:
                target_selector = 'div.chakra-portal header div:first-child svg:last-child'
                target_element = await self.page.wait_for_selector(target_selector, timeout=5000)
                breakpoint()  # 调试断点
                if target_element:
                    print("找到目标元素,关闭窗口...")
                    await target_element.click()
                    print("成功关闭窗口")
                    await asyncio.sleep(5)
                else:
                    print("未找到目标元素 关闭窗口")
            except Exception as e:
                print(f"点击目标元素时出错: {e}")

            breakpoint()  # 调试断点
                
            # 查找并点击交易对
            print(f"正在查找交易对: {symbol}")
        except Exception as e:
            print(f"获取交易量数据时出错: {e}")
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
    
    async def extract_volume_data(self) -> Dict:
        """
        提取页面中的交易量数据
        
        Returns:
            包含交易量数据的字典
        """
        volume_data = {}
        
        try:
            # 尝试多种选择器来获取交易量数据
            volume_selectors = [
                '[data-testid="volume"]',
                '.volume',
                '.trading-volume',
                '[class*="volume"]',
                '//div[contains(@class, "volume")]',
                '//span[contains(text(), "24h成交量")]',
                '//div[contains(text(), "24h成交量")]'
            ]
            
            for selector in volume_selectors:
                try:
                    if selector.startswith('//'):
                        element = await self.page.wait_for_selector(f'xpath={selector}', timeout=3000)
                    else:
                        element = await self.page.wait_for_selector(selector, timeout=3000)
                    
                    if element:
                        volume_text = await element.text_content()
                        if volume_text:
                            volume_data["24h_volume"] = volume_text.strip()
                            break
                except Exception:
                    continue
            
            # 获取价格数据
            price_selectors = [
                '[data-testid="price"]',
                '.price',
                '.current-price',
                '[class*="price"]',
                '//div[contains(@class, "price")]'
            ]
            
            for selector in price_selectors:
                try:
                    if selector.startswith('//'):
                        element = await self.page.wait_for_selector(f'xpath={selector}', timeout=3000)
                    else:
                        element = await self.page.wait_for_selector(selector, timeout=3000)
                    
                    if element:
                        price_text = await element.text_content()
                        if price_text:
                            volume_data["current_price"] = price_text.strip()
                            break
                except Exception:
                    continue
            
            # 获取涨跌幅数据
            change_selectors = [
                '[data-testid="change"]',
                '.change',
                '.price-change',
                '[class*="change"]',
                '//div[contains(@class, "change")]'
            ]
            
            for selector in change_selectors:
                try:
                    if selector.startswith('//'):
                        element = await self.page.wait_for_selector(f'xpath={selector}', timeout=3000)
                    else:
                        element = await self.page.wait_for_selector(selector, timeout=3000)
                    
                    if element:
                        change_text = await element.text_content()
                        if change_text:
                            volume_data["24h_change"] = change_text.strip()
                            break
                except Exception:
                    continue
            
            # 如果上述选择器都没有找到，尝试获取页面截图进行分析
            if not volume_data:
                print("未找到标准数据元素，尝试获取页面截图...")
                screenshot_path = f"gmgn_screenshot_{int(time.time())}.png"
                await self.page.screenshot(path=screenshot_path)
                print(f"页面截图已保存到: {screenshot_path}")
                
                # 获取页面文本内容进行分析
                page_text = await self.page.text_content('body')
                volume_data["page_text_sample"] = page_text[:1000] if page_text else "无内容"
            
        except Exception as e:
            print(f"提取交易量数据时出错: {e}")
            volume_data["error"] = str(e)
        
        return volume_data
    
    async def get_multiple_symbols_volume(self, symbols: List[str]) -> List[Dict]:
        """
        获取多个交易对的交易量数据
        
        Args:
            symbols: 交易对列表
            
        Returns:
            包含所有交易对数据的列表
        """
        results = []
        
        for symbol in symbols:
            print(f"\n正在获取 {symbol} 的交易量数据...")
            result = await self.get_trading_volume(symbol)
            results.append(result)
            
            # 在请求之间添加延迟，避免被反爬
            await asyncio.sleep(2)
        
        return results

    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()


async def main():
    """主函数"""
    crawler = GMGNCrawler(headless=False)  # 设置为False以便观察爬取过程
    
    try:
        await crawler.start_browser()
        
        await crawler.get_volume_by_token("0xe6df05ce8c8301223373cf5b969afcb1498c5528")
        # # 获取单个交易对的数据
        # print("=== 获取BTC/USDT交易量数据 ===")
        # btc_data = await crawler.get_trading_volume("BTC/USDT")
        # print(json.dumps(btc_data, ensure_ascii=False, indent=2))
        
        # # 获取多个交易对的数据
        # print("\n=== 获取多个交易对数据 ===")
        # symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
        # multi_data = await crawler.get_multiple_symbols_volume(symbols)
        
        # for data in multi_data:
        #     print(f"\n{data['symbol']}:")
        #     print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # # 保存数据到文件
        # with open("gmgn_trading_data.json", "w", encoding="utf-8") as f:
        #     json.dump({
        #         "timestamp": datetime.now().isoformat(),
        #         "data": multi_data
        #     }, f, ensure_ascii=False, indent=2)
        
        # print(f"\n数据已保存到: gmgn_trading_data.json")
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        
    finally:
        await crawler.close_browser()


# 这句话很常见， 就用来判断是直接运行的( python gmgn.py ) 还是被导入的( from gmgn import GMGNCrawler ).
# 如果是直接运行的，就执行if里的代码， 不然就忽略。
if __name__ == "__main__":
    asyncio.run(main())
