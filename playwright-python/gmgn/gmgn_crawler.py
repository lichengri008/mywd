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
from typing import Dict
from playwright.async_api import async_playwright, expect
from utils.util import change_dir
import os
from config import current_config


class GMGNCrawler:
    """GMGN交易量爬虫类"""

    # __init__ 是python中特殊方法， 创建类实例时自动调用，主要用于初始化对象的属性。
    def __init__(self, headless: bool = None):
        self.headless = headless if headless is not None else current_config.HEADLESS
        self.browser = None
        self.page = None
        self.base_url = current_config.BASE_URL

    # 代码稍微复杂(需要处理 cloudflare 反爬机制)，可以暂时忽略。
    async def start_browser(self):
        """启动浏览器"""
        playwright = await async_playwright().start()

        launch_args = {
            "headless": self.headless,
            "args": current_config.get_browser_args(),
        }

        if current_config.PROXY:
            launch_args["proxy"] = current_config.PROXY

        context = None

        # 优先尝试 Chrome 持久化上下文，失败则回退到普通 Chromium
        if current_config.USE_PERSISTENT_CONTEXT:
            user_data_dir = current_config.USER_DATA_DIR
            os.makedirs(user_data_dir, exist_ok=True)
            try:
                if current_config.USE_CHROME_CHANNEL:
                    launch_kwargs_with_channel = {
                        **launch_args,
                        "channel": current_config.CHANNEL,
                    }
                else:
                    launch_kwargs_with_channel = dict(launch_args)

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
            self.browser = await playwright.chromium.launch(**launch_args)
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

        # 给所有后续的 网络请求 自动带上指定的 HTTP header。
        await self.page.set_extra_http_headers(
            {
                "Accept-Language": current_config.ACCEPT_LANGUAGE,
            }
        )

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

    # 截屏方法
    async def snapshot(self, _fileName: str = ""):
        print("尝试获取页面截图...")
        fileName = f"gmgn_{int(time.time())}.png"
        if _fileName:
            fileName = f"{ _fileName}.png"
        screenshot_path = f"{current_config.SCREENSHOT_DIR}/{fileName}"
        await self.page.screenshot(path=screenshot_path)
        print(f"✅ 页面截图已保存到: {screenshot_path}")

    # 访问首页
    async def go_to_home_page(self):
        try:
            url = self.base_url
            print(f"正在访问 {url}...")
            await self.page.goto(url, wait_until="domcontentloaded")

            # 判断某个元素是否出现 来确认页面加载完毕
            text = "Log In"
            await expect(self.page.get_by_text(text)).to_be_visible()
            print(f"✅ 找到元素 {text}, 页面加载完毕")
            await self.snapshot()
        except Exception as e:
            print(f"❌ 访问 {url} 时出错: {e}")
            await self.snapshot()

    # 关闭各种弹窗
    async def skip_popups(self):
        # 1. 检查是否出现 登陆弹窗，如果发现就关闭
        try:
            # 查找登陆弹窗上的， 邮箱输入框
            emailInput = self.page.get_by_placeholder("Enter Email")
            await expect(emailInput).to_be_visible()
            await self.snapshot("2.1-login-popup-found")
            # 通过邮箱输入框，查找对应的弹窗
            dialog = emailInput.locator("xpath=ancestor::*[@role='dialog'][1]")
            # 弹窗内搜索关闭按钮
            closeIcon = dialog.locator("header > div > svg")
            await closeIcon.click()
            print("✅ 找到登录弹窗，尝试关闭")
            await self.snapshot("2.2-login-popup-closed")
        except Exception as e:
            print(f"❌ 没有发现弹窗，或关闭弹窗失败: {e}")
            await self.snapshot("2.2-login-popup-closed-failed")
            pass

        # 2. 检查是否出现 介绍弹窗，如果发现就关闭
        try:
            nextButton = self.page.locator("div.pi-modal span", has_text="Next")
            await expect(nextButton).to_be_visible()
            await self.snapshot("3.1-intro-popup-found")
            modalMask = nextButton.locator(
                "xpath=ancestor::div[contains(@class,'pi-modal-mask')][1]"
            )
            await expect(modalMask).to_have_class("pi-modal-mask")
            await modalMask.click()
            print("✅ 关闭介绍弹窗")
            await self.snapshot("3.2-intro-popup-closed")
        except Exception as e:
            print(f"❌ 没有发现介绍弹窗，或关闭弹窗失败: {e}")
            await self.snapshot("3.2-intro-popup-closed-failed")
            pass

    async def start_work(self, token: str = "") -> Dict:
        data_crawled = {}
        try:

            chain = "bsc"
            url = f"{self.base_url}/{chain}/token/{token}"

            # 1. 访问首页
            await self.go_to_home_page()

            # 2. 关闭弹窗
            await self.skip_popups()

            try:
                searchInput = await self.page.wait_for_selector(
                    "input[name='search_tips']", timeout=5000
                )
                await searchInput.click()
                await self.snapshot()
                await searchInput.fill(token)
                await self.snapshot()
            except Exception:
                pass

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
        if self.browser:
            await self.browser.close()


async def main():
    """主函数"""
    change_dir()  # 切换执行目录

    crawler = GMGNCrawler(headless=False)  # 设置为False以便观察爬取过程

    try:
        await crawler.start_browser()

        data = await crawler.start_work("USDT")

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
