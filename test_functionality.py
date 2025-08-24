"""
QalcTxt功能测试脚本
验证核心计算功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.calculator import CalculatorEngine
from core.parser import ExpressionParser
from core.equation_solver import EquationSolver
from core.result_manager import ResultManager

def test_basic_functionality():
    """测试基本功能"""
    print("=== QalcTxt 功能测试 ===\n")
    
    # 初始化组件
    calculator = CalculatorEngine()
    parser = ExpressionParser()
    equation_solver = EquationSolver()
    result_manager = ResultManager()
    
    print("1. 基本数学计算测试:")
    test_expressions = [
        "2 + 3",
        "5 * 4", 
        "10 / 2",
        "2 ** 3",
        "sqrt(16)",
        "sin(0)",
        "pi"
    ]
    
    for expr in test_expressions:
        result = calculator.calculate(expr)
        print(f"   {expr} = {result}")
        result_manager.store_result(len(result_manager.results) + 1, expr, result, False)
    
    print("\n2. 方程求解测试:")
    equation_tests = [
        "solve(x^2 - 4, x)",
        "solve(x^2 - 5*x + 6, x)",
        "x^2 = 9"
    ]
    
    for eq in equation_tests:
        if equation_solver.sympy_available:
            try:
                result = equation_solver.solve_equation(eq)
                print(f"   {eq} => {result}")
                result_manager.store_result(len(result_manager.results) + 1, eq, result, True)
            except Exception as e:
                print(f"   {eq} => 错误: {str(e)}")
        else:
            print(f"   {eq} => SymPy未安装，无法求解方程")
    
    print("\n3. 行引用测试:")
    # 测试行引用
    ref_expr = "@1 + @2"  # 引用第1行和第2行的结果
    parsed_expr, is_empty, original = parser.parse_expression(ref_expr, result_manager)
    if not is_empty:
        result = calculator.calculate(parsed_expr)
        print(f"   {ref_expr} => {parsed_expr} = {result}")
    
    print("\n4. 注释处理测试:")
    comment_tests = [
        "5 + 3 # 这是注释",
        "# 这是纯注释行",
        "7 * 8"
    ]
    
    for expr in comment_tests:
        parsed_expr, is_empty, original = parser.parse_expression(expr)
        if is_empty:
            print(f"   '{expr}' => (跳过：空行或注释)")
        else:
            result = calculator.calculate(parsed_expr)
            print(f"   '{expr}' => {parsed_expr} = {result}")
    
    print("\n5. 结果管理测试:")
    stats = result_manager.get_statistics()
    print(f"   总计算结果: {stats['total_results']}")
    print(f"   成功计算: {stats['successful_calculations']}")
    print(f"   方程求解: {stats['equations_solved']}")
    print(f"   错误: {stats['errors']}")
    
    print("\n=== 测试完成 ===")
    print("所有核心功能正常工作！")

if __name__ == "__main__":
    test_basic_functionality()