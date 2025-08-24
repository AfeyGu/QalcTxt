"""
计算引擎模块
提供安全的数学表达式计算功能
"""

import math
import cmath
import re
from typing import Union, Any

class CalculatorEngine:
    """计算引擎类，封装Python数学计算功能"""
    
    def __init__(self):
        """初始化计算引擎"""
        # 创建安全的计算命名空间
        self.safe_dict = {
            '__builtins__': {},
            # 基本函数
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow, 'divmod': divmod,
            
            # 数学函数
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'atan2': math.atan2,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
            
            # 指数和对数函数
            'exp': math.exp, 'log': math.log, 'log10': math.log10,
            'log2': math.log2, 'sqrt': math.sqrt,
            
            # 其他数学函数
            'ceil': math.ceil, 'floor': math.floor, 'trunc': math.trunc,
            'factorial': math.factorial, 'gcd': math.gcd,
            'degrees': math.degrees, 'radians': math.radians,
            
            # 常数
            'pi': math.pi, 'e': math.e, 'tau': math.tau,
            
            # 复数
            'j': 1j, 'complex': complex,
            
            # 类型转换
            'int': int, 'float': float, 'bool': bool,
        }
    
    def calculate(self, expression: str) -> Union[float, int, complex, str]:
        """
        计算数学表达式
        
        Args:
            expression: 要计算的数学表达式
            
        Returns:
            计算结果或错误信息
        """
        try:
            # 预处理表达式
            processed_expr = self._preprocess_expression(expression)
            
            # 安全计算
            result = eval(processed_expr, {"__builtins__": {}}, self.safe_dict)
            
            # 格式化结果
            return self._format_result(result)
            
        except ZeroDivisionError:
            return "错误: 除零错误"
        except ValueError as e:
            return f"错误: 数值错误 - {str(e)}"
        except SyntaxError as e:
            return f"错误: 语法错误 - {str(e)}"
        except NameError as e:
            return f"错误: 未知函数或变量 - {str(e)}"
        except Exception as e:
            return f"错误: {str(e)}"
    
    def _preprocess_expression(self, expression: str) -> str:
        """
        预处理表达式，进行必要的替换和清理
        
        Args:
            expression: 原始表达式
            
        Returns:
            处理后的表达式
        """
        # 移除多余空格
        expr = expression.strip()
        
        # 替换一些常见的数学符号
        replacements = {
            '^': '**',  # 幂运算
            '×': '*',   # 乘法
            '÷': '/',   # 除法
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        # 处理隐式乘法 (如 2pi -> 2*pi)
        expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        expr = re.sub(r'\)(\d)', r')*\1', expr)
        expr = re.sub(r'(\d)\(', r'\1*(', expr)
        
        return expr
    
    def _format_result(self, result: Any) -> Union[str, float, int, complex]:
        """
        格式化计算结果
        
        Args:
            result: 原始计算结果
            
        Returns:
            格式化后的结果
        """
        if isinstance(result, (int, float)):
            # 对于浮点数，如果接近整数则显示为整数
            if isinstance(result, float) and result.is_integer():
                return int(result)
            # 限制小数位数
            elif isinstance(result, float):
                return round(result, 10)
            return result
        elif isinstance(result, complex):
            # 复数格式化
            if result.imag == 0:
                return self._format_result(result.real)
            elif result.real == 0:
                if result.imag == 1:
                    return "j"
                elif result.imag == -1:
                    return "-j"
                else:
                    return f"{self._format_result(result.imag)}j"
            else:
                real_part = self._format_result(result.real)
                imag_part = self._format_result(abs(result.imag))
                sign = '+' if result.imag >= 0 else '-'
                if imag_part == 1:
                    return f"{real_part}{sign}j"
                else:
                    return f"{real_part}{sign}{imag_part}j"
        else:
            return result
    
    def is_valid_expression(self, expression: str) -> bool:
        """
        检查表达式是否有效
        
        Args:
            expression: 要检查的表达式
            
        Returns:
            是否有效
        """
        try:
            processed_expr = self._preprocess_expression(expression)
            compile(processed_expr, '<string>', 'eval')
            return True
        except:
            return False