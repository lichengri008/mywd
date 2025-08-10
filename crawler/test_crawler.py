#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMGN爬虫测试脚本
用于测试爬虫的基本功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gmgn import GMGNCrawler


async def test_single_symbol():
    """测试获取单个交易对数据"""
    print("=== 测试单个交易对数据获取 ===")
    
    crawler = GMGNCrawler(headless=False)
    
    try:
        await crawler.start_browser()
        
        # 测试获取BTC/USDT数据
        result = await crawler.get_trading_volume("BTC/USDT")
        
        print(f"结果: {result}")
        
        if result['status'] == 'success':
            print("✅ 测试通过：成功获取数据")
        else:
            print("❌ 测试失败：无法获取数据")
            print(f"错误信息: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        
    finally:
        await crawler.close_browser()


async def test_multiple_symbols():
    """测试获取多个交易对数据"""
    print("\n=== 测试多个交易对数据获取 ===")
    
    crawler = GMGNCrawler(headless=False)
    
    try:
        await crawler.start_browser()
        
        # 测试获取多个交易对数据
        symbols = ["BTC/USDT", "ETH/USDT"]
        results = await crawler.get_multiple_symbols_volume(symbols)
        
        print(f"获取到 {len(results)} 个交易对的数据:")
        for result in results:
            print(f"  {result['symbol']}: {result['status']}")
            
        success_count = sum(1 for r in results if r['status'] == 'success')
        print(f"成功获取: {success_count}/{len(results)}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        
    finally:
        await crawler.close_browser()


async def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    crawler = GMGNCrawler(headless=False)
    
    try:
        await crawler.start_browser()
        
        # 测试不存在的交易对
        result = await crawler.get_trading_volume("INVALID/PAIR")
        
        print(f"无效交易对测试结果: {result}")
        
        if result['status'] == 'error':
            print("✅ 错误处理测试通过")
        else:
            print("⚠️ 错误处理可能需要改进")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        
    finally:
        await crawler.close_browser()


async def main():
    """主测试函数"""
    print("开始GMGN爬虫测试...")
    
    # 运行各项测试
    await test_single_symbol()
    await test_multiple_symbols()
    await test_error_handling()
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
