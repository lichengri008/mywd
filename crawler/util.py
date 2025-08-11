#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
