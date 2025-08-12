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
from playwright.async_api import async_playwright, Browser, Page, expect
from util import change_dir
import os
from config import current_config

class GMGNCrawler:
    """GMGN交易量爬虫类"""

    # __init__ 是python中特殊方法， 创建类实例时自动调用，主要用于初始化对象的属性。
    def __init__(self, headless: bool = None):
        self.headless = headless if headless is not None else current_config.HEADLESS
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.base_url = current_config.BASE_URL

    async def start_browser(self):
        """启动浏览器，尽量贴近真实环境，降低被 Cloudflare 识别概率"""
        playwright = await async_playwright().start()

        launch_kwargs = {
            "headless": self.headless,
            "args": current_config.get_browser_args(),
        }

        context = None
        # 优先尝试 Chrome 持久化上下文，失败则回退到普通 Chromium
        if current_config.USE_PERSISTENT_CONTEXT:
            user_data_dir = current_config.USER_DATA_DIR
            os.makedirs(user_data_dir, exist_ok=True)
            try:
                if current_config.USE_CHROME_CHANNEL:
                    launch_kwargs_with_channel = {**launch_kwargs, "channel": current_config.CHANNEL}
                else:
                    launch_kwargs_with_channel = dict(launch_kwargs)
                context = await playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    locale=current_config.LOCALE,
                    timezone_id=current_config.TIMEZONE_ID,
                    viewport={
                        "width": current_config.VIEWPORT_WIDTH,
                        "height": current_config.VIEWPORT_HEIGHT,
                    },
                    user_agent=current_config.USER_AGENT,
                    **launch_kwargs_with_channel,
                )
                self.browser = context.browser
            except Exception as e:
                print(f"持久化 Chrome 启动失败，将回退到无痕 Chromium。原因: {e}")
        if context is None:
            self.browser = await playwright.chromium.launch(**launch_kwargs)
            context = await self.browser.new_context(
                locale=current_config.LOCALE,
                timezone_id=current_config.TIMEZONE_ID,
                viewport={
                    "width": current_config.VIEWPORT_WIDTH,
                    "height": current_config.VIEWPORT_HEIGHT,
                },
                user_agent=current_config.USER_AGENT,
            )

        # 创建新页面
        self.page = await context.new_page()
        await self.page.set_extra_http_headers({
            "Accept-Language": current_config.ACCEPT_LANGUAGE,
        })

        # 伪装：隐藏 webdriver 痕迹
        await self.page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            // 伪造插件数量
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            // 伪造语言
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'zh-CN'] });
            // 修复 iframe 的 webdriver 暴露
            const patch = () => {
              const getDescriptor = (o, prop) => Object.getOwnPropertyDescriptor(o, prop);
              const newProto = navigator.__proto__;
              const old = getDescriptor(newProto, 'webdriver');
              if (old && old.get) {
                Object.defineProperty(newProto, 'webdriver', { get: () => undefined });
              }
            };
            try { patch(); } catch (e) {}
            """
        )

    async def go_to_home_page(self):
        try:
            url = self.base_url
            print(f"正在访问 {url}...")
            await self.page.goto(url, wait_until="domcontentloaded")

            # 判断某个元素是否出现 来确认页面加载完毕
            text = current_config.PAGE_LOADED_SEL_TEXT
            await expect(self.page.get_by_text(text)).to_be_visible()
            print(f"✅ 找到元素 {text}, 页面加载完毕")
            await self.snapshot()
        except Exception as e:
            print(f"访问 {url} 时出错: {e}")
            await self.snapshot()

    async def snapshot(self):
        print("尝试获取页面截图...")
        screenshot_path = f"{current_config.SCREENSHOT_DIR}/gmgn_{int(time.time())}.png"
        await self.page.screenshot(path=screenshot_path)
        print(f"✅ 页面截图已保存到: {screenshot_path}")

    async def start_work(self, token: str = "") -> Dict:
        data_crawled = {}
        try:

            chain = "bsc"
            url = f"{self.base_url}/{chain}/token/{token}"

            await self.go_to_home_page()

            await asyncio.sleep(3)  # 等待页面加载

            # 如果首页出现登陆弹窗，关闭弹窗
            
            try:
                emailInput = await self.page.get_by_placeholder("Enter Email", timeout=5000)
                if emailInput:
                    print("✅ 找到登录弹窗，尝试关闭")
            except Exception:
                pass

            popup = None
            try:
                popup = await self.page.wait_for_selector(
                    ".pi-modal-mask", timeout=5000
                )
            except Exception:
                pass

            if popup:
                popupWrap = await self.page.wait_for_selector(
                    ".pi-modal-wrap.pi-modal-centered", timeout=5000
                )
                if popupWrap:
                    popupWrap.click()
                else:
                    print("关闭弹窗失败")
            else:
                print("无弹窗需要关闭")

            # 截图
            await self.snapshot()

            try:
                el = await self.page.wait_for_selector("input[name='search_tips']", timeout=5000)
                await el.click()
            except Exception:
                pass

            print("✅ 点击了搜索框")

            # 查找 id为 MainDomId的<main> 中，内容为"24h Vol"的span，对应的父元素的父元素的，最后一个子元素div内的内容
            # try:
            #     # 首先找到包含"24h Vol"文本的span元素
            #     vol_span = await self.page.wait_for_selector('main#MainDomId span:has-text("24h Vol")', timeout=5000)
            #     if vol_span:
            #         print("找到24h Vol span元素")

            #         # 获取span的父元素
            #         parent_element = await vol_span.query_selector('xpath=..')
            #         if parent_element:
            #             print("找到父元素")

            #             # 获取父元素的父元素
            #             grandparent_element = await parent_element.query_selector('xpath=..')
            #             if grandparent_element:
            #                 print("找到祖父元素")

            #                 # 获取祖父元素的最后一个子元素div
            #                 last_div = await grandparent_element.query_selector('div:last-child')
            #                 if last_div:
            #                     print("找到最后一个子元素div")

            #                     # 获取div内的内容
            #                     div_content = await last_div.text_content()
            #                     print(f"最后一个子元素div的内容: {div_content}")

            #                     # 也可以获取HTML内容
            #                     div_html = await last_div.inner_html()
            #                     print(f"最后一个子元素div的HTML: {div_html}")
            #                 else:
            #                     print("未找到最后一个子元素div")
            #             else:
            #                 print("未找到祖父元素")
            #         else:
            #             print("未找到父元素")
            #     else:
            #         print("未找到24h Vol span元素")
            # except Exception as e:
            #     print(f"查找24h Vol元素时出错: {e}")
            # # 24h Vol

        except Exception as e:
            print(f"❌ 出错: {e}")
            await self.snapshot()
            return {
                "symbol": token,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error",
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
            # 访问页面
            print(f"正在访问 {self.base_url}...")

            # 打开浏览器
            await self.go_to_home_page()

            # 查找并点击交易对
            print(f"正在查找交易对: {symbol}")
        except Exception as e:
            print(f"获取交易量数据时出错: {e}")
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error",
            }

    async def close_browser(self):
        """关闭浏览器"""
        try:
            if self.page:
                await self.page.context.storage_state(path=f"{current_config.DATA_DIR}/gmgn_storage_state.json")
        except Exception:
            pass
        if self.browser:
            await self.browser.close()


async def main():
    """主函数"""
    change_dir()  # 切换执行目录

    crawler = GMGNCrawler(headless=False)  # 设置为False以便观察爬取过程

    try:
        await crawler.start_browser()

        data = await crawler.start_work("0xe6df05ce8c8301223373cf5b969afcb1498c5528")

        print(json.dumps(data, ensure_ascii=False, indent=2))

        # 保存数据到文件
        data_path = f"{current_config.DATA_DIR}/gmgn_trading_data.json"
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(
                {"timestamp": datetime.now().isoformat(), "data": data},
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"\n数据已保存到: {data_path}")

    except Exception as e:
        print(f"程序执行出错: {e}")

    finally:
        await crawler.close_browser()


if __name__ == "__main__":
    asyncio.run(main())
