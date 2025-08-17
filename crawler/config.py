#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMGN爬虫配置文件
管理爬虫的各种设置和参数
"""

import os


class Config:
    """爬虫配置类"""

    # 基础配置
    BASE_URL = "https://gmgn.ai/"

    # 设置代理: 需要挂梯子时设置
    PROXY = {"server": "http://localhost:7890"}

    # 运行模式
    HEADLESS = False

    VIEWPORT_WIDTH = 1920

    VIEWPORT_HEIGHT = 1080

    # 浏览器配置
    BROWSER_ARGS = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--disable-gpu",
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        # # 尽量保持接近真实浏览器，避免使用明显的自动化标志
        # "--disable-blink-features=AutomationControlled",
    ]

    # 用户代理
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

    ACCEPT_LANGUAGE = "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"

    LOCALE = "en-US"

    TIMEZONE_ID = "Asia/Shanghai"

    # 文件配置
    DATA_DIR = "data"

    SCREENSHOT_DIR = "screenshots"

    LOG_DIR = "logs"

    # 持久化上下文（使用真实 Chrome 通道）
    USE_PERSISTENT_CONTEXT = False

    USE_CHROME_CHANNEL = True

    CHANNEL = "chrome"  # 使用本机已安装的 Chrome，指纹更自然

    USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".mywd", "playwright", "gmgn")

    @classmethod
    def get_browser_args(cls):
        """获取浏览器启动参数"""
        return cls.BROWSER_ARGS.copy()

    @classmethod
    def get_screenshot_path(cls, filename: str) -> str:
        """获取截图文件路径"""
        return os.path.join(cls.SCREENSHOT_DIR, filename)

    @classmethod
    def get_data_path(cls, filename: str) -> str:
        """获取数据文件路径"""
        return os.path.join(cls.DATA_DIR, filename)

    @classmethod
    def get_log_path(cls, filename: str) -> str:
        """获取日志文件路径"""
        return os.path.join(cls.LOG_DIR, filename)


# 开发环境配置
class DevConfig(Config):
    """开发环境配置"""

    HEADLESS = False


# 生产环境配置
class ProdConfig(Config):
    """生产环境配置"""

    HEADLESS = True


def get_config(env: str = "dev") -> Config:
    """
    根据环境获取配置

    Args:
        env: 环境名称 (dev, prod, test)

    Returns:
        对应的配置类
    """
    configs = {"dev": DevConfig, "prod": ProdConfig}

    return configs.get(env, DevConfig)


# 默认配置
current_config = get_config(os.getenv("CRAWLER_ENV", "dev"))
