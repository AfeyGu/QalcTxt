"""
表达式解析器单元测试
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.parser import ExpressionParser
from core.result_manager import ResultManager

class TestExpressionParser(unittest.TestCase):
    """测试表达式解析器"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = ExpressionParser()
        self.result_manager = ResultManager()
        
        # 准备一些测试数据
        self.result_manager.store_result(1, "2 + 3", 5, False)
        self.result_manager.store_result(2, "solve(x^2 - 5*x + 6, x)", "x[0] = 2, x[1] = 3", True)
    
    def test_remove_comments(self):
        """测试注释移除"""
        # 基本注释
        result = self.parser.remove_comments("2 + 3 # 这是注释")
        self.assertEqual(result, "2 + 3 ")
        
        # 纯注释行
        result = self.parser.remove_comments("# 这是纯注释")
        self.assertEqual(result, "")
        
        # 无注释
        result = self.parser.remove_comments("2 + 3")
        self.assertEqual(result, "2 + 3")
        
        # 注释符号在开头
        result = self.parser.remove_comments("#开头注释")
        self.assertEqual(result, "")
    
    def test_parse_expression_empty_lines(self):
        """测试空行和注释行解析"""
        # 空行
        expr, is_empty, original = self.parser.parse_expression("")
        self.assertTrue(is_empty)
        
        # 只有空格
        expr, is_empty, original = self.parser.parse_expression("   ")
        self.assertTrue(is_empty)
        
        # 纯注释行
        expr, is_empty, original = self.parser.parse_expression("# 这是注释")
        self.assertTrue(is_empty)
        
        # 有效表达式
        expr, is_empty, original = self.parser.parse_expression("2 + 3")
        self.assertFalse(is_empty)
        self.assertEqual(expr, "2 + 3")
    
    def test_parse_expression_with_comments(self):
        """测试带注释的表达式解析"""
        expr, is_empty, original = self.parser.parse_expression("2 + 3 # 这是计算")
        self.assertFalse(is_empty)
        self.assertEqual(expr.strip(), "2 + 3")  # 去除空格进行比较
        self.assertEqual(original, "2 + 3 # 这是计算")
    
    def test_line_reference_extraction(self):
        """测试行引用提取"""
        # 单个引用
        refs = self.parser.extract_line_references("@1 + 5")
        self.assertEqual(refs, [(1, None)])
        
        # 带索引的引用
        refs = self.parser.extract_line_references("@2.0 + @2.1")
        self.assertEqual(refs, [(2, 0), (2, 1)])
        
        # 多个引用
        refs = self.parser.extract_line_references("@1 + @2 * @3")
        self.assertEqual(refs, [(1, None), (2, None), (3, None)])
        
        # 无引用
        refs = self.parser.extract_line_references("2 + 3")
        self.assertEqual(refs, [])
    
    def test_resolve_line_references(self):
        """测试行引用解析"""
        # 简单引用
        result = self.parser.resolve_line_references("@1 + 5", self.result_manager)
        self.assertEqual(result, "5 + 5")
        
        # 带索引的引用（方程解）
        # 先为第2行设置一个有数值解的结果
        from core.result_manager import ResultData
        result_data = ResultData(2, "test", "x[0] = 2, x[1] = 3", "multiple", True)
        result_data.solutions = [2.0, 3.0]
        self.result_manager.results[2] = result_data
        
        result = self.parser.resolve_line_references("@2.0 + @2.1", self.result_manager)
        self.assertEqual(result, "2.0 + 3.0")
    
    def test_is_comment_line(self):
        """测试注释行判断"""
        self.assertTrue(self.parser.is_comment_line("# 这是注释"))
        self.assertTrue(self.parser.is_comment_line(""))
        self.assertTrue(self.parser.is_comment_line("   "))
        self.assertFalse(self.parser.is_comment_line("2 + 3"))
        self.assertFalse(self.parser.is_comment_line("2 + 3 # 注释"))
    
    def test_get_expression_type(self):
        """测试表达式类型判断"""
        # 空表达式
        self.assertEqual(self.parser.get_expression_type(""), "empty")
        
        # 数值计算
        self.assertEqual(self.parser.get_expression_type("2 + 3"), "numeric")
        
        # 方程
        self.assertEqual(self.parser.get_expression_type("x^2 = 4"), "equation")
        self.assertEqual(self.parser.get_expression_type("solve(x^2 - 1, x)"), "equation")
    
    def test_validate_syntax(self):
        """测试语法验证"""
        # 有效表达式
        valid, msg = self.parser.validate_syntax("2 + 3")
        self.assertTrue(valid)
        
        valid, msg = self.parser.validate_syntax("sin(pi/2)")
        self.assertTrue(valid)
        
        # 无效表达式
        valid, msg = self.parser.validate_syntax("2 +")
        self.assertFalse(valid)
        
        valid, msg = self.parser.validate_syntax("(2 + 3")
        self.assertFalse(valid)
        
        # 空表达式
        valid, msg = self.parser.validate_syntax("")
        self.assertTrue(valid)

if __name__ == '__main__':
    unittest.main()