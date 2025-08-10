#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMGN爬虫环境安装脚本
自动安装所需的依赖和浏览器
"""

import subprocess
import sys
import os


def run_command(command, description):
    """运行命令并显示进度"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("   需要Python 3.8或更高版本")
        return False
    else:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True


def install_dependencies():
    """安装Python依赖"""
    print("\n📦 安装Python依赖...")
    
    # 升级pip
    if not run_command("python -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 安装依赖
    if not run_command("python -m pip install -r requirements.txt", "安装依赖包"):
        return False
    
    return True


def install_browsers():
    """安装Playwright浏览器"""
    print("\n🌐 安装Playwright浏览器...")
    
    if not run_command("playwright install chromium", "安装Chromium浏览器"):
        return False
    
    return True


def create_directories():
    """创建必要的目录"""
    print("\n📁 创建必要的目录...")
    
    directories = ["data", "screenshots", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ 创建目录: {directory}")
        else:
            print(f"ℹ️  目录已存在: {directory}")
    
    return True


def test_installation():
    """测试安装是否成功"""
    print("\n🧪 测试安装...")
    
    try:
        import playwright
        # 尝试获取版本号，如果没有__version__属性则跳过
        try:
            version = playwright.__version__
            print(f"✅ Playwright版本: {version}")
        except AttributeError:
            print("✅ Playwright导入成功")
        
        # 测试导入爬虫类
        from gmgn import GMGNCrawler
        print("✅ 爬虫类导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入测试失败: {e}")
        return False


def main():
    """主安装函数"""
    print("🚀 GMGN爬虫环境安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        print("\n❌ 环境检查失败，请升级Python版本后重试")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("\n❌ 依赖安装失败")
        return
    
    # 安装浏览器
    if not install_browsers():
        print("\n❌ 浏览器安装失败")
        return
    
    # 创建目录
    if not create_directories():
        print("\n❌ 目录创建失败")
        return
    
    # 测试安装
    if not test_installation():
        print("\n❌ 安装测试失败")
        return
    
    print("\n🎉 安装完成！")
    print("\n📖 使用方法:")
    print("  1. 获取单个交易对数据:")
    print("     python run_crawler.py BTC/USDT")
    print("  2. 获取多个交易对数据:")
    print("     python run_crawler.py BTC/USDT ETH/USDT")
    print("  3. 使用无头模式:")
    print("     python run_crawler.py BTC/USDT --headless")
    print("  4. 运行测试:")
    print("     python test_crawler.py")
    print("\n💡 提示: 首次运行建议不使用--headless参数，以便观察爬取过程")


if __name__ == "__main__":
    main()
