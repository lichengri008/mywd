#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright爬虫
获取Playwright官网信息
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Optional, List
from playwright.async_api import async_playwright, expect
from util import change_dir
from config import current_config


class PlaywrightCrawler:
    """Playwright 爬虫类"""

    # PS: __init__ 是python中特殊方法， 创建类实例时自动调用，主要用于初始化对象的属性。
    def __init__(self, headless: bool = None):
        self.headless = headless if headless is not None else True
        self.browser = None
        self.page = None
        self.base_url = "https://playwright.dev/python/"

    async def start_browser(self):
        """启动浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.headless, args=current_config.get_browser_args()
        )

        # 创建新页面
        self.page = await self.browser.new_page()

        # 设置用户代理
        await self.page.set_extra_http_headers(
            {"User-Agent": current_config.USER_AGENT}
        )

        # 设置视口大小
        await self.page.set_viewport_size(
            {
                "width": current_config.VIEWPORT_WIDTH,
                "height": current_config.VIEWPORT_HEIGHT,
            }
        )

    async def open_home_page(self):

        try:
            url = self.base_url
            print(f"正在访问 {url}...")
            await self.page.goto(url)

            # 通过查询文本 确认页面加载完毕
            text = "Get started"
            expect(self.page.get_by_text(text)).to_be_visible()
            print(f"✅ 找到元素 {text}, 页面加载完毕")

        except Exception as e:
            print(f"访问 {url} 时出错: {e}")

    async def body_content(self):
        # 获取页面文本内容进行分析
        page_text = await self.page.text_content("body")
        data = page_text[:1000] if page_text else "无内容"
        return data

    async def snapshot(self):
        # 截图保存
        print("正在截图...")
        screenshot_path = f"{current_config.LOG_DIR}/playwright_{int(time.time())}.png"
        await self.page.screenshot(path=screenshot_path)
        print(f"页面截图已保存到: {screenshot_path}")

    async def start_work(self) -> Dict:
        data = {}
        try:
            await self.open_home_page()

            # 设置断点
            # breakpoint()

            # 爬取官网首页标题
            heroTitle = await self.page.wait_for_selector("h1.hero__title")
            title = await heroTitle.text_content()
            data["title"] = title

            # 截图保存
            await self.snapshot()

            # 获取页面文件内容
            body_content = await self.body_content()
            data["body_content"] = body_content
            return data

        except Exception as e:
            print(f"❌ 出错: {e}")
            return {
                "error": str(e),
            }

    async def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()


async def main():
    """主函数"""
    change_dir()  # 切换执行目录

    crawler = PlaywrightCrawler(headless=True)  # 设置为False以便观察爬取过程

    try:
        await crawler.start_browser()

        data = await crawler.start_work()

        print(json.dumps(data, ensure_ascii=False, indent=2))

        # 保存数据到文件
        data_path = f"{current_config.DATA_DIR}/playwright_data.json"
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


# PS: 这段代码很常见， 用来判断是直接运行的( python playwright.py ) 还是被导入的( from playwright import PlaywrightCrawler ). 如果是直接运行的，就执行if里的代码， 不然就忽略。
if __name__ == "__main__":
    asyncio.run(main())
