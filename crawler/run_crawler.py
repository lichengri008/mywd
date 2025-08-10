#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMGN爬虫启动脚本
简化运行爬虫的流程
"""

import asyncio
import argparse
from gmgn import GMGNCrawler


async def run_crawler(symbols, headless=True, save_file=True):
    """
    运行爬虫
    
    Args:
        symbols: 交易对列表
        headless: 是否使用无头模式
        save_file: 是否保存到文件
    """
    crawler = GMGNCrawler(headless=headless)
    
    try:
        print("🚀 启动GMGN爬虫...")
        await crawler.start_browser()
        
        if len(symbols) == 1:
            # 单个交易对
            print(f"📊 正在获取 {symbols[0]} 的交易量数据...")
            result = await crawler.get_trading_volume(symbols[0])
            
            if result['status'] == 'success':
                print(f"✅ 成功获取 {symbols[0]} 数据:")
                print(f"   24h成交量: {result['volume_data'].get('24h_volume', 'N/A')}")
                print(f"   当前价格: {result['volume_data'].get('current_price', 'N/A')}")
                print(f"   24h涨跌: {result['volume_data'].get('24h_change', 'N/A')}")
            else:
                print(f"❌ 获取 {symbols[0]} 数据失败: {result.get('error', '未知错误')}")
                
        else:
            # 多个交易对
            print(f"📊 正在获取 {len(symbols)} 个交易对的数据...")
            results = await crawler.get_multiple_symbols_volume(symbols)
            
            print("\n📈 获取结果:")
            for result in results:
                status_icon = "✅" if result['status'] == 'success' else "❌"
                print(f"  {status_icon} {result['symbol']}: {result['status']}")
                
                if result['status'] == 'success':
                    volume_data = result['volume_data']
                    print(f"     24h成交量: {volume_data.get('24h_volume', 'N/A')}")
                    print(f"     当前价格: {volume_data.get('current_price', 'N/A')}")
                    print(f"     24h涨跌: {volume_data.get('24h_change', 'N/A')}")
        
        # 保存数据到文件
        if save_file and len(symbols) > 1:
            import json
            from datetime import datetime
            
            filename = f"gmgn_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "symbols": symbols,
                    "data": results if len(symbols) > 1 else [result]
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 数据已保存到: {filename}")
        
    except Exception as e:
        print(f"❌ 爬虫运行出错: {e}")
        
    finally:
        await crawler.close_browser()
        print("🔚 爬虫已关闭")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GMGN交易量爬虫")
    parser.add_argument("symbols", nargs="+", help="交易对符号，如 BTC/USDT ETH/USDT")
    parser.add_argument("--headless", action="store_true", help="使用无头模式")
    parser.add_argument("--no-save", action="store_true", help="不保存到文件")
    
    args = parser.parse_args()
    
    # 验证交易对格式
    for symbol in args.symbols:
        if "/" not in symbol:
            print(f"❌ 无效的交易对格式: {symbol}")
            print("   正确格式: BTC/USDT, ETH/USDT")
            return
    
    print(f"🎯 目标交易对: {', '.join(args.symbols)}")
    print(f"🖥️  无头模式: {'是' if args.headless else '否'}")
    print(f"💾 保存文件: {'否' if args.no_save else '是'}")
    print("-" * 50)
    
    # 运行爬虫
    asyncio.run(run_crawler(
        symbols=args.symbols,
        headless=args.headless,
        save_file=not args.no_save
    ))


if __name__ == "__main__":
    main()
