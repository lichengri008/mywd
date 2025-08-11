#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMGN爬虫快速启动脚本
展示爬虫的基本用法和功能
"""

import asyncio
import json
from datetime import datetime
from gmgn_crawler import GMGNCrawler


async def quick_demo():
    """快速演示爬虫功能"""
    print("🚀 GMGN爬虫快速演示")
    print("=" * 50)
    
    # 创建爬虫实例（非无头模式，便于观察）
    crawler = GMGNCrawler(headless=False)
    
    try:
        # 启动浏览器
        print("🌐 启动浏览器...")
        await crawler.start_browser()
        
        # 获取BTC/USDT交易量数据
        print("\n📊 获取BTC/USDT交易量数据...")
        btc_data = await crawler.get_trading_volume("BTC/USDT")
        
        if btc_data['status'] == 'success':
            print("✅ 成功获取BTC/USDT数据:")
            volume_data = btc_data['volume_data']
            
            if '24h_volume' in volume_data:
                print(f"   24h成交量: {volume_data['24h_volume']}")
            if 'current_price' in volume_data:
                print(f"   当前价格: {volume_data['current_price']}")
            if '24h_change' in volume_data:
                print(f"   24h涨跌: {volume_data['24h_change']}")
                
            # 保存数据
            filename = f"btc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(btc_data, f, ensure_ascii=False, indent=2)
            print(f"💾 数据已保存到: {filename}")
            
        else:
            print(f"❌ 获取数据失败: {btc_data.get('error', '未知错误')}")
            
        # 等待用户查看
        print("\n⏳ 等待5秒后关闭浏览器...")
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"❌ 演示过程中出错: {e}")
        
    finally:
        await crawler.close_browser()
        print("🔚 浏览器已关闭")


def main():
    """主函数"""
    print("🎯 选择演示模式:")
    print("1. 快速演示 (单个交易对)")
    print("2. 批量演示 (多个交易对)")
    print("3. 退出")
    
    while True:
        try:
            choice = input("\n请输入选择 (1-3): ").strip()
            
            if choice == "1":
                asyncio.run(quick_demo())
                break
            elif choice == "2":
                asyncio.run(batch_demo())
                break
            elif choice == "3":
                print("👋 再见!")
                break
            else:
                print("❌ 无效选择，请输入1-3")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
