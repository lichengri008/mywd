#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫环境安装脚本
自动安装所需的依赖和浏览器
"""

import subprocess
import sys
import os


def get_working_path():
    # 获取当前文件所在目录
    file_dir = os.path.dirname(os.path.abspath(__file__))
    return file_dir

def change_dir():
    file_dir = get_working_path()
    current_dir = os.getcwd()
    if current_dir != file_dir:
        print(f"ℹ️  切换到文件所在目录: {file_dir}")
        os.chdir(file_dir)

def run_command(command, description):
    """运行命令并显示进度"""
    print(f"🔄 {description}...")
    
    file_dir = get_working_path()
    
    try:
        # 明确指定在文件所在目录中运行命令
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=file_dir)
        print(f"✅ {description}完成")
        result = True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        result = False

    return result


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
    
    # 根据requirements.txt安装依赖
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
        from gmgn_crawler import GMGNCrawler
        print("✅ 爬虫类导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入测试失败: {e}")
        return False


def main():
    """主安装函数"""
    print("🚀 爬虫环境安装程序")
    print("=" * 50)
    
    # 切换路径
    change_dir()

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

if __name__ == "__main__":
    main()
