"""
表达式解析器模块
处理用户输入的表达式，包括行引用(@3, @3.0)和注释(#)
"""

import re
from typing import Tuple, Optional, Dict, Any

class ExpressionParser:
    """表达式解析器类"""
    
    def __init__(self):
        """初始化解析器"""
        # 行引用正则表达式：匹配 @数字[.数字]
        self.line_ref_pattern = re.compile(r'@(\d+)(?:\.(\d+))?')
        
    def parse_expression(self, text: str, results_manager=None) -> Tuple[str, bool, str]:
        """
        解析表达式
        
        Args:
            text: 原始文本
            results_manager: 结果管理器实例
            
        Returns:
            (处理后的表达式, 是否为空行/注释行, 原始表达式)
        """
        # 移除首尾空白
        original_text = text.strip()
        
        # 检查是否为空行
        if not original_text:
            return "", True, original_text
        
        # 移除注释
        expression = self.remove_comments(original_text)
        
        # 检查移除注释后是否为空
        if not expression.strip():
            return "", True, original_text
        
        # 处理行引用
        if results_manager:
            try:
                expression = self.resolve_line_references(expression, results_manager)
            except Exception as e:
                return f"错误: 行引用解析失败 - {str(e)}", False, original_text
        
        return expression.strip(), False, original_text
    
    def remove_comments(self, text: str) -> str:
        """
        移除注释（#及其后面的内容）
        
        Args:
            text: 原始文本
            
        Returns:
            移除注释后的文本
        """
        # 查找#的位置
        comment_pos = text.find('#')
        if comment_pos >= 0:
            return text[:comment_pos]
        return text
    
    def resolve_line_references(self, expression: str, results_manager) -> str:
        """
        解析行引用，将@行号替换为实际结果
        
        Args:
            expression: 包含行引用的表达式
            results_manager: 结果管理器实例
            
        Returns:
            替换后的表达式
        """
        def replace_reference(match):
            line_num = int(match.group(1))
            solution_index = match.group(2)
            
            if solution_index is not None:
                solution_index = int(solution_index)
            
            # 从结果管理器获取结果
            result = results_manager.get_result(line_num, solution_index)
            
            if result is None:
                raise ValueError(f"第{line_num}行没有结果")
            
            # 如果结果是数值，直接返回
            if isinstance(result, (int, float, complex)):
                if isinstance(result, complex):
                    # 复数需要用括号包围
                    return f"({result})"
                return str(result)
            else:
                # 字符串结果（可能是错误信息）
                raise ValueError(f"第{line_num}行的结果不是数值: {result}")
        
        # 替换所有行引用
        return self.line_ref_pattern.sub(replace_reference, expression)
    
    def extract_line_references(self, expression: str) -> list:
        """
        提取表达式中的所有行引用
        
        Args:
            expression: 表达式
            
        Returns:
            行引用列表，每个元素为(行号, 解索引)的元组
        """
        references = []
        for match in self.line_ref_pattern.finditer(expression):
            line_num = int(match.group(1))
            solution_index = int(match.group(2)) if match.group(2) else None
            references.append((line_num, solution_index))
        return references
    
    def validate_syntax(self, expression: str) -> Tuple[bool, str]:
        """
        验证表达式语法
        
        Args:
            expression: 要验证的表达式
            
        Returns:
            (是否有效, 错误信息)
        """
        if not expression.strip():
            return True, ""
        
        try:
            # 尝试编译表达式
            compile(expression, '<string>', 'eval')
            return True, ""
        except SyntaxError as e:
            return False, f"语法错误: {str(e)}"
        except Exception as e:
            return False, f"表达式错误: {str(e)}"
    
    def is_comment_line(self, text: str) -> bool:
        """
        判断是否为纯注释行
        
        Args:
            text: 文本行
            
        Returns:
            是否为注释行
        """
        stripped = text.strip()
        return stripped.startswith('#') or not stripped
    
    def get_expression_type(self, expression: str) -> str:
        """
        判断表达式类型
        
        Args:
            expression: 表达式
            
        Returns:
            表达式类型：'equation', 'equation_system', 'numeric', 'empty', 'error'
        """
        if not expression.strip():
            return 'empty'
        
        # 检查是否为方程组格式: x,y:expr1=val1,expr2=val2
        if ':' in expression and ',' in expression:
            parts = expression.split(':', 1)
            if len(parts) == 2:
                var_part = parts[0].strip()
                eq_part = parts[1].strip()
                # 检查变量部分是否为用逗号分隔的变量
                if ',' in var_part and '=' in eq_part:
                    return 'equation_system'
        
        # 检查是否包含等号（可能是方程）
        if '=' in expression and 'solve' not in expression.lower():
            return 'equation'
        
        # 检查是否包含solve函数
        if 'solve' in expression.lower():
            return 'equation'
        
        # 其他情况视为数值计算
        return 'numeric'
    
    def parse_equation_system(self, expression: str) -> tuple:
        """
        解析方程组格式: x,y:x+y=1,x-y=1
        
        Args:
            expression: 方程组表达式
            
        Returns:
            (variables, equations) 元组
        """
        if ':' not in expression:
            raise ValueError("方程组格式错误，缺少':'分隔符")
        
        parts = expression.split(':', 1)
        var_part = parts[0].strip()
        eq_part = parts[1].strip()
        
        # 解析变量
        variables = [v.strip() for v in var_part.split(',')]
        
        # 解析方程
        equations = [eq.strip() for eq in eq_part.split(',')]
        
        return variables, equations