"""
方程求解器模块
使用SymPy库进行符号计算和方程求解
"""

import re
from typing import Union, List, Any
try:
    import sympy as sp
    from sympy import symbols, solve, Eq, sympify
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

class EquationSolver:
    """方程求解器类"""
    
    def __init__(self):
        """初始化求解器"""
        self.sympy_available = SYMPY_AVAILABLE
        if not self.sympy_available:
            print("警告: SymPy库未安装，方程求解功能将不可用")
    
    def solve_equation(self, equation_str: str) -> Union[str, List[str]]:
        """
        求解方程
        
        Args:
            equation_str: 方程字符串
            
        Returns:
            求解结果或错误信息
        """
        if not self.sympy_available:
            return "错误: 需要安装SymPy库才能使用方程求解功能"
        
        try:
            # 检查是否为方程组格式
            if ':' in equation_str and ',' in equation_str:
                parts = equation_str.split(':', 1)
                if len(parts) == 2:
                    var_part = parts[0].strip()
                    eq_part = parts[1].strip()
                    if ',' in var_part and '=' in eq_part:
                        return self._solve_equation_system(var_part, eq_part)
            
            # 预处理方程字符串
            processed_eq = self._preprocess_equation(equation_str)
            
            # 解析并求解方程
            solutions = self._solve_with_sympy(processed_eq)
            
            # 格式化输出
            return self._format_solutions(solutions)
            
        except Exception as e:
            return f"错误: 方程求解失败 - {str(e)}"
    
    def _solve_equation_system(self, var_part: str, eq_part: str) -> str:
        """
        求解方程组格式: x,y:x+y=1,x-y=1
        
        Args:
            var_part: 变量部分，如 "x,y"
            eq_part: 方程部分，如 "x+y=1,x-y=1"
            
        Returns:
            格式化的解
        """
        try:
            # 解析变量
            variables = [v.strip() for v in var_part.split(',')]
            
            # 解析方程
            equation_strs = [eq.strip() for eq in eq_part.split(',')]
            
            # 创建符号变量
            symbols_dict = {}
            for var in variables:
                symbols_dict[var] = sp.Symbol(var)
            
            # 解析每个方程
            equations = []
            for eq_str in equation_strs:
                if '=' not in eq_str:
                    raise ValueError(f"方程 '{eq_str}' 缺少等号")
                
                left, right = eq_str.split('=', 1)
                left = left.strip().replace('^', '**')
                right = right.strip().replace('^', '**')
                
                # 使用符号变量解析表达式
                left_expr = sp.sympify(left, locals=symbols_dict)
                right_expr = sp.sympify(right, locals=symbols_dict)
                
                # 创建等式
                equation = sp.Eq(left_expr, right_expr)
                equations.append(equation)
            
            # 求解方程组
            symbol_vars = [symbols_dict[var] for var in variables]
            solutions = solve(equations, symbol_vars)
            
            # 格式化结果
            if isinstance(solutions, dict):
                # 单解情况
                result_parts = []
                for var in variables:
                    if symbols_dict[var] in solutions:
                        value = solutions[symbols_dict[var]]
                        try:
                            numeric_value = float(value.evalf())
                            if numeric_value.is_integer():
                                result_parts.append(f"{var} = {int(numeric_value)}")
                            else:
                                result_parts.append(f"{var} = {numeric_value}")
                        except:
                            result_parts.append(f"{var} = {value}")
                return ", ".join(result_parts)
            elif isinstance(solutions, list):
                if not solutions:
                    return "无解"
                elif len(solutions) == 1 and isinstance(solutions[0], dict):
                    # 单解情况
                    solution = solutions[0]
                    result_parts = []
                    for var in variables:
                        if symbols_dict[var] in solution:
                            value = solution[symbols_dict[var]]
                            try:
                                numeric_value = float(value.evalf())
                                if numeric_value.is_integer():
                                    result_parts.append(f"{var} = {int(numeric_value)}")
                                else:
                                    result_parts.append(f"{var} = {numeric_value}")
                            except:
                                result_parts.append(f"{var} = {value}")
                    return ", ".join(result_parts)
                else:
                    # 多解情况 - 使用新的格式化方法
                    return self._format_multi_solution_system(solutions, variables, symbols_dict)
            else:
                return str(solutions)
                
        except Exception as e:
            raise ValueError(f"方程组求解失败: {str(e)}")
    
    def _format_multi_solution_system(self, solutions, variables, symbols_dict):
        """
        格式化多解方程组结果，支持复杂引用
        
        Args:
            solutions: 解的列表
            variables: 变量列表
            symbols_dict: 符号字典
            
        Returns:
            格式化的结果字符串
        """
        try:
            result_parts = []
            
            # 为每个变量格式化结果
            for var_idx, var in enumerate(variables):
                var_solutions = []
                
                # 提取该变量在所有解中的值
                for sol_idx, solution in enumerate(solutions):
                    if isinstance(solution, tuple) and len(solution) == len(variables):
                        # 元组格式的解
                        value = solution[var_idx]
                    elif isinstance(solution, dict) and symbols_dict[var] in solution:
                        # 字典格式的解
                        value = solution[symbols_dict[var]]
                    else:
                        continue
                    
                    try:
                        # 尝试转换为数值
                        if hasattr(value, 'evalf'):
                            numeric_value = float(value.evalf())
                            if abs(numeric_value - round(numeric_value)) < 1e-10:
                                var_solutions.append(str(int(round(numeric_value))))
                            else:
                                var_solutions.append(f"{numeric_value:.10g}")
                        else:
                            var_solutions.append(str(value))
                    except:
                        var_solutions.append(str(value))
                
                # 格式化该变量的所有解
                if var_solutions:
                    if len(var_solutions) == 1:
                        result_parts.append(f"{var} = {var_solutions[0]}")
                    else:
                        # 多解格式: var[0] = val1, var[1] = val2
                        var_results = []
                        for i, val in enumerate(var_solutions):
                            var_results.append(f"{var}[{i}] = {val}")
                        result_parts.append(", ".join(var_results))
            
            return "; ".join(result_parts)
            
        except Exception as e:
            # 如果格式化失败，返回原始结果
            return str(solutions)
    
    def _preprocess_equation(self, equation_str: str) -> str:
        """
        预处理方程字符串
        
        Args:
            equation_str: 原始方程字符串
            
        Returns:
            处理后的方程字符串
        """
        # 移除空格
        eq = equation_str.strip()
        
        # 对于solve函数调用，只替换幂运算符
        if 'solve(' in eq.lower():
            eq = eq.replace('^', '**')
            return eq
        
        # 替换数学符号
        replacements = {
            '^': '**',  # 幂运算
            '×': '*',   # 乘法
            '÷': '/',   # 除法
        }
        
        for old, new in replacements.items():
            eq = eq.replace(old, new)
        
        # 处理隐式乘法 (但不影响函数调用)
        # 防止 solve( 被替换为 solve*(
        eq = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq)
        eq = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', eq)
        eq = re.sub(r'\)([a-zA-Z\d])', r')*\1', eq)
        # 修改这行以避免影响函数调用
        eq = re.sub(r'([a-zA-Z\d])\((?![a-zA-Z_])', r'\1*(', eq)
        
        return eq
    
    def _solve_with_sympy(self, equation_str: str) -> List[Any]:
        """
        使用SymPy求解方程
        
        Args:
            equation_str: 方程字符串
            
        Returns:
            解的列表
        """
        # 如果包含solve函数调用
        if 'solve(' in equation_str.lower():
            return self._handle_solve_function(equation_str)
        
        # 如果包含等号，处理为等式方程
        if '=' in equation_str:
            return self._handle_equation_with_equals(equation_str)
        
        # 其他情况，直接抛出错误
        raise ValueError(f"无法识别的表达式格式: {equation_str}")
    
    def _handle_solve_function(self, equation_str: str) -> List[Any]:
        """
        处理包含solve函数的字符串
        
        Args:
            equation_str: 包含solve的字符串
            
        Returns:
            解的列表
        """
        # 创建安全的命名空间
        namespace = {
            'solve': solve,
            'symbols': symbols,
            'Symbol': sp.Symbol,
            'Eq': Eq,
            'x': sp.Symbol('x'),
            'y': sp.Symbol('y'),
            'z': sp.Symbol('z'),
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
            'pi': sp.pi, 'E': sp.E,
            # 添加支持
            'sympify': sp.sympify,
            '**': lambda x, y: x**y,  # 幂运算
        }
        
        # 处理^符号
        equation_str = equation_str.replace('^', '**')
        
        try:
            # 执行solve函数
            # 直接调用手动解析，避免 eval 的问题
            return self._parse_solve_manually(equation_str)
        except Exception as e:
            # 如果手动解析也失败，抛出错误
            raise ValueError(f"solve函数执行失败: {str(e)}")
    
    def _parse_solve_manually(self, equation_str: str) -> List[Any]:
        """
        手动解析solve函数调用
        
        Args:
            equation_str: solve函数调用字符串
            
        Returns:
            解的列表
        """
        import re
        
        # 匹配 solve(表达式, 变量) 的格式
        match = re.match(r'solve\(([^,]+),\s*([^)]+)\)', equation_str.strip())
        if match:
            expr_str = match.group(1).strip()
            var_str = match.group(2).strip()
            
            try:
                # 处理表达式
                expr_str = expr_str.replace('^', '**')
                
                # 创建符号变量
                var_symbol = sp.Symbol(var_str)
                
                # 解析表达式，传入正确的变量映射
                local_vars = {var_str: var_symbol}
                expr = sp.sympify(expr_str, locals=local_vars)
                
                # 求解
                solutions = solve(expr, var_symbol)
                
                return solutions if isinstance(solutions, list) else [solutions]
                
            except Exception as e:
                raise ValueError(f"solve函数解析失败: {str(e)} [表达式: '{expr_str}', 变量: '{var_str}']")
        else:
            raise ValueError(f"无法解析solve函数调用格式: {equation_str}")
    
    def _handle_equation_with_equals(self, equation_str: str) -> List[Any]:
        """
        处理包含等号的方程
        
        Args:
            equation_str: 包含等号的方程字符串
            
        Returns:
            解的列表
        """
        # 分割等式
        parts = equation_str.split('=')
        if len(parts) != 2:
            raise ValueError("方程格式错误，应包含一个等号")
        
        left_expr = sympify(parts[0].strip())
        right_expr = sympify(parts[1].strip())
        
        # 创建方程
        equation = Eq(left_expr, right_expr)
        
        # 自动检测变量
        variables = list(equation.free_symbols)
        if not variables:
            # 如果没有变量，直接计算等式是否成立
            return [equation]
        
        # 求解方程
        if len(variables) == 1:
            solutions = solve(equation, variables[0])
        else:
            # 多变量方程，求解第一个变量
            solutions = solve(equation, variables[0])
        
        return solutions if isinstance(solutions, list) else [solutions]
    
    def _format_solutions(self, solutions: List[Any]) -> str:
        """
        格式化求解结果
        
        Args:
            solutions: 解的列表
            
        Returns:
            格式化的结果字符串
        """
        if not solutions:
            return "无解"
        
        # 单个解的情况
        if len(solutions) == 1:
            solution = solutions[0]
            if hasattr(solution, 'free_symbols') and solution.free_symbols:
                # 包含符号的表达式
                return str(solution)
            else:
                # 数值解
                try:
                    numeric_value = float(solution.evalf())
                    if numeric_value.is_integer():
                        return f"x = {int(numeric_value)}"
                    else:
                        return f"x = {numeric_value}"
                except:
                    return f"x = {solution}"
        
        # 多个解的情况
        result_parts = []
        for i, solution in enumerate(solutions):
            try:
                if hasattr(solution, 'free_symbols') and solution.free_symbols:
                    # 包含符号的表达式
                    result_parts.append(f"x[{i}] = {solution}")
                else:
                    # 数值解
                    numeric_value = float(solution.evalf())
                    if numeric_value.is_integer():
                        result_parts.append(f"x[{i}] = {int(numeric_value)}")
                    else:
                        result_parts.append(f"x[{i}] = {numeric_value}")
            except:
                result_parts.append(f"x[{i}] = {solution}")
        
        return ", ".join(result_parts)
    
    def is_equation(self, expression: str) -> bool:
        """
        判断表达式是否为方程
        
        Args:
            expression: 表达式字符串
            
        Returns:
            是否为方程
        """
        # 检查是否为方程组格式: x,y:expr1=val1,expr2=val2
        if ':' in expression and ',' in expression:
            parts = expression.split(':', 1)
            if len(parts) == 2:
                var_part = parts[0].strip()
                eq_part = parts[1].strip()
                if ',' in var_part and '=' in eq_part:
                    return True
        
        return ('=' in expression and 'solve' not in expression.lower()) or \
               'solve(' in expression.lower()
    
    def extract_solutions_for_reference(self, formatted_result: str) -> List[float]:
        """
        从格式化结果中提取数值解，用于行引用
        
        Args:
            formatted_result: 格式化的结果字符串
            
        Returns:
            数值解的列表
        """
        solutions = []
        
        # 匹配 x[i] = 数值 的模式
        pattern = r'x\[\d+\]\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)'
        matches = re.findall(pattern, formatted_result)
        
        for match in matches:
            try:
                solutions.append(float(match))
            except ValueError:
                continue
        
        # 如果没有找到多解格式，尝试匹配单解格式 x = 数值
        if not solutions:
            pattern = r'x\s*=\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)'
            match = re.search(pattern, formatted_result)
            if match:
                try:
                    solutions.append(float(match.group(1)))
                except ValueError:
                    pass
        
        return solutions