#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys

def check_excel_structure():
    try:
        # 读取Excel文件
        file_path = "../日本东京酒店v2.xlsx"
        print(f"正在读取Excel文件: {file_path}")
        
        # 读取第一个工作表
        df = pd.read_excel(file_path, sheet_name=0)
        
        print(f"Excel文件读取成功！")
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        
        print("\n前5行数据:")
        print(df.head())
        
        print("\n数据类型:")
        print(df.dtypes)
        
        # 检查是否有空值
        print("\n空值统计:")
        print(df.isnull().sum())
        
        return True
        
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return False

if __name__ == "__main__":
    check_excel_structure() 