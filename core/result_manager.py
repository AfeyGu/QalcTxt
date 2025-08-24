"""
结果管理器模块
管理计算结果历史，提供结果查询接口
"""

from typing import Union, Dict, List, Any, Optional
from datetime import datetime
import re

class ResultData:
    """结果数据类"""
    
    def __init__(self, line_number: int, expression: str, result: Any, 
                 result_type: str = "single", is_equation: bool = False):
        """
        初始化结果数据
        
        Args:
            line_number: 行号
            expression: 原始表达式
            result: 计算结果
            result_type: 结果类型 ("single", "multiple", "error")
            is_equation: 是否为方程
        """
        self.line_number = line_number
        self.expression = expression
        self.result = result
        self.result_type = result_type
        self.is_equation = is_equation
        self.timestamp = datetime.now()
        self.solutions = []  # 用于存储多解
        
        # 如果是方程结果，提取数值解
        if is_equation and isinstance(result, str):
            self.solutions = self._extract_numeric_solutions(result)
    
    def _extract_numeric_solutions(self, formatted_result: str) -> List[float]:
        """
        从格式化结果中提取数值解
        
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

class ResultManager:
    """结果管理器类"""
    
    def __init__(self):
        """初始化结果管理器"""
        self.results: Dict[int, ResultData] = {}
        self.max_line = 0
    
    def store_result(self, line_number: int, expression: str, result: Any, 
                     is_equation: bool = False) -> None:
        """
        存储计算结果
        
        Args:
            line_number: 行号
            expression: 原始表达式
            result: 计算结果
            is_equation: 是否为方程
        """
        # 确定结果类型
        result_type = self._determine_result_type(result, is_equation)
        
        # 创建结果数据对象
        result_data = ResultData(
            line_number=line_number,
            expression=expression,
            result=result,
            result_type=result_type,
            is_equation=is_equation
        )
        
        # 存储结果
        self.results[line_number] = result_data
        self.max_line = max(self.max_line, line_number)
    
    def get_result(self, line_number: int, solution_index: Optional[int] = None) -> Union[float, int, complex, str, None]:
        """
        获取指定行的结果
        
        Args:
            line_number: 行号
            solution_index: 解的索引（用于多解情况）
            
        Returns:
            计算结果或None
        """
        if line_number not in self.results:
            return None
        
        result_data = self.results[line_number]
        
        # 如果是错误结果，直接返回None
        if result_data.result_type == "error":
            return None
        
        # 如果请求特定解的索引
        if solution_index is not None:
            if result_data.is_equation and result_data.solutions:
                if 0 <= solution_index < len(result_data.solutions):
                    return result_data.solutions[solution_index]
                else:
                    return None
            else:
                # 非方程结果，只有索引0有效
                if solution_index == 0:
                    return result_data.result
                else:
                    return None
        
        # 返回完整结果
        if result_data.is_equation and result_data.solutions:
            # 对于方程，如果只有一个解，返回该解；否则返回第一个解
            if len(result_data.solutions) == 1:
                return result_data.solutions[0]
            else:
                return result_data.solutions[0] if result_data.solutions else None
        else:
            return result_data.result
    
    def get_result_data(self, line_number: int) -> Optional[ResultData]:
        """
        获取指定行的完整结果数据
        
        Args:
            line_number: 行号
            
        Returns:
            结果数据对象或None
        """
        return self.results.get(line_number)
    
    def get_all_results(self) -> Dict[int, ResultData]:
        """
        获取所有结果
        
        Returns:
            所有结果的字典
        """
        return self.results.copy()
    
    def clear_results(self) -> None:
        """清空所有结果"""
        self.results.clear()
        self.max_line = 0
    
    def remove_result(self, line_number: int) -> bool:
        """
        删除指定行的结果
        
        Args:
            line_number: 行号
            
        Returns:
            是否删除成功
        """
        if line_number in self.results:
            del self.results[line_number]
            return True
        return False
    
    def get_formatted_result(self, line_number: int) -> str:
        """
        获取格式化的结果字符串
        
        Args:
            line_number: 行号
            
        Returns:
            格式化的结果字符串
        """
        if line_number not in self.results:
            return ""
        
        result_data = self.results[line_number]
        
        if result_data.result_type == "error":
            return str(result_data.result)
        
        return self.format_result(result_data.result)
    
    def format_result(self, result: Any) -> str:
        """
        格式化结果显示
        
        Args:
            result: 计算结果
            
        Returns:
            格式化的结果字符串
        """
        if isinstance(result, str):
            return result
        elif isinstance(result, (int, float)):
            if isinstance(result, float) and result.is_integer():
                return str(int(result))
            elif isinstance(result, float):
                # 限制小数位数
                return f"{result:.10g}"
            return str(result)
        elif isinstance(result, complex):
            # 复数格式化
            if result.imag == 0:
                return self.format_result(result.real)
            elif result.real == 0:
                if result.imag == 1:
                    return "j"
                elif result.imag == -1:
                    return "-j"
                else:
                    return f"{self.format_result(result.imag)}j"
            else:
                real_part = self.format_result(result.real)
                imag_part = self.format_result(abs(result.imag))
                sign = '+' if result.imag >= 0 else '-'
                if abs(result.imag) == 1:
                    return f"{real_part}{sign}j"
                else:
                    return f"{real_part}{sign}{imag_part}j"
        else:
            return str(result)
    
    def _determine_result_type(self, result: Any, is_equation: bool) -> str:
        """
        确定结果类型
        
        Args:
            result: 计算结果
            is_equation: 是否为方程
            
        Returns:
            结果类型
        """
        if isinstance(result, str) and result.startswith("错误"):
            return "error"
        elif is_equation and isinstance(result, str) and ('[' in result or 'x[' in result):
            return "multiple"
        else:
            return "single"
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取结果统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            'total_results': len(self.results),
            'successful_calculations': 0,
            'equations_solved': 0,
            'errors': 0
        }
        
        for result_data in self.results.values():
            if result_data.result_type == "error":
                stats['errors'] += 1
            else:
                stats['successful_calculations'] += 1
                if result_data.is_equation:
                    stats['equations_solved'] += 1
        
        return stats