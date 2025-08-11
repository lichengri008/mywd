#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMGN爬虫配置文件
管理爬虫的各种设置和参数
"""

import os
from typing import List


class Config:
    """爬虫配置类"""
    
    # 基础配置
    BASE_URL = "https://gmgn.ai/"

    HEADLESS = True
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    
    # 确认选择器
    PAGE_LOADED_SEL_TEXT = "Log In"

    # 浏览器配置
    BROWSER_ARGS = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor'
    ]
    
    # 用户代理
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    # 延迟配置
    PAGE_LOAD_WAIT = 3
    ELEMENT_WAIT = 5
    REQUEST_DELAY = 2
    
    # 选择器配置
    SYMBOL_SELECTORS = [
        'text={symbol}',
        '[data-symbol="{symbol}"]',
        '[title*="{symbol}"]',
        '//span[contains(text(), "{symbol}")]',
        '//div[contains(text(), "{symbol}")]'
    ]
    
    VOLUME_SELECTORS = [
        '[data-testid="volume"]',
        '.volume',
        '.trading-volume',
        '[class*="volume"]',
        '//div[contains(@class, "volume")]',
        '//span[contains(text(), "24h成交量")]',
        '//div[contains(text(), "24h成交量")]'
    ]
    
    PRICE_SELECTORS = [
        '[data-testid="price"]',
        '.price',
        '.current-price',
        '[class*="price"]',
        '//div[contains(@class, "price")]'
    ]
    
    CHANGE_SELECTORS = [
        '[data-testid="change"]',
        '.change',
        '.price-change',
        '[class*="change"]',
        '//div[contains(@class, "change")]'
    ]
    
    SEARCH_SELECTORS = [
        'input[type="search"]',
        'input[placeholder*="搜索"]',
        '.search-input',
        '[class*="search"]'
    ]
    
    # 文件配置
    DATA_DIR = "data"
    SCREENSHOT_DIR = "screenshots"
    LOG_DIR = "logs"
    
    # 默认交易对
    DEFAULT_SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    @classmethod
    def get_browser_args(cls):
        """获取浏览器启动参数"""
        return cls.BROWSER_ARGS.copy()
    
    @classmethod
    def get_symbol_selectors(cls, symbol: str) -> List[str]:
        """获取交易对选择器列表"""
        return [selector.format(symbol=symbol) for selector in cls.SYMBOL_SELECTORS]
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        for directory in [cls.DATA_DIR, cls.SCREENSHOT_DIR, cls.LOG_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
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
    PAGE_LOAD_WAIT = 5
    ELEMENT_WAIT = 10
    REQUEST_DELAY = 3


# 生产环境配置
class ProdConfig(Config):
    """生产环境配置"""
    HEADLESS = True
    PAGE_LOAD_WAIT = 2
    ELEMENT_WAIT = 3
    REQUEST_DELAY = 1


# 测试环境配置
class TestConfig(Config):
    """测试环境配置"""
    HEADLESS = False
    PAGE_LOAD_WAIT = 3
    ELEMENT_WAIT = 5
    REQUEST_DELAY = 2


def get_config(env: str = "dev") -> Config:
    """
    根据环境获取配置
    
    Args:
        env: 环境名称 (dev, prod, test)
        
    Returns:
        对应的配置类
    """
    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig
    }
    
    return configs.get(env, DevConfig)


# 默认配置
current_config = get_config(os.getenv("CRAWLER_ENV", "dev"))
