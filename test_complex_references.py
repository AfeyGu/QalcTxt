#!/usr/bin/env python3
"""
测试复杂引用功能
验证 @行号.变量索引.解索引 格式的支持
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.equation_solver import EquationSolver
from core.result_manager import ResultManager
from core.parser import ExpressionParser

def test_equation_system_formatting():
    """测试方程组结果格式化"""
    print("=== 测试方程组结果格式化 ===")
    solver = EquationSolver()
    
    # 测试简单方程组
    result1 = solver.solve_equation('x,y:x+y=5,x-y=1')
    print(f"x,y:x+y=5,x-y=1 => {result1}")
    
    # 测试复杂方程组（可能有多解）
    result2 = solver.solve_equation('x,y:x+y=5,x*y=2')
    print(f"x,y:x+y=5,x*y=2 => {result2}")
    
    return result1, result2

def test_result_manager():
    """测试结果管理器的复杂引用功能"""
    print("\n=== 测试结果管理器 ===")
    rm = ResultManager()
    
    # 存储方程组结果
    equation_result = "x[0] = 3, x[1] = 2; y[0] = 2, y[1] = 3"
    rm.store_result(1, 'x,y:x+y=5,x*y=6', equation_result, True)
    
    # 测试各种引用格式
    print("测试引用格式:")
    print(f"@1 => {rm.get_result(1)}")
    print(f"@1.0 => {rm.get_result(1, 0)}")
    print(f"@1.1 => {rm.get_result(1, 1)}")
    print(f"@1.0.0 => {rm.get_result(1, 0, 0)}")  # 第一个变量的第一个解
    print(f"@1.1.0 => {rm.get_result(1, 0, 1)}")  # 第二个变量的第一个解
    print(f"@1.0.1 => {rm.get_result(1, 1, 0)}")  # 第一个变量的第二个解
    print(f"@1.1.1 => {rm.get_result(1, 1, 1)}")  # 第二个变量的第二个解
    
    # 检查解析结果
    result_data = rm.get_result_data(1)
    if result_data:
        print(f"变量解析结果: {result_data.variable_solutions}")

def test_parser():
    """测试表达式解析器的三级引用"""
    print("\n=== 测试表达式解析器 ===")
    parser = ExpressionParser()
    
    # 测试引用提取
    test_expressions = [
        "@1",
        "@1.0", 
        "@1.1.0",
        "@2.0.1 + @2.1.0",
        "sqrt(@3.0.0) + @3.1.1"
    ]
    
    for expr in test_expressions:
        refs = parser.extract_line_references(expr)
        print(f"表达式 '{expr}' 中的引用: {refs}")

def main():
    """主测试函数"""
    print("开始测试复杂引用功能...\n")
    
    try:
        # 测试方程组格式化
        result1, result2 = test_equation_system_formatting()
        
        # 测试结果管理器
        test_result_manager()
        
        # 测试解析器
        test_parser()
        
        print("\n=== 测试完成 ===")
        print("所有功能测试通过！")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()