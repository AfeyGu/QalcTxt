"""
文件管理器单元测试
"""

import unittest
import tempfile
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.file_manager import FileManager
from core.result_manager import ResultManager, ResultData

class TestFileManager(unittest.TestCase):
    """测试文件管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.file_manager = FileManager()
        self.temp_dir = tempfile.mkdtemp()
        
        # 准备测试数据
        self.test_content = "2 + 3\n5 * 4\nsolve(x^2 - 1, x)"
        self.test_results = {}
        
        # 创建测试结果
        result1 = ResultData(1, "2 + 3", 5, "single", False)
        result2 = ResultData(2, "5 * 4", 20, "single", False)
        result3 = ResultData(3, "solve(x^2 - 1, x)", "x[0] = -1, x[1] = 1", "multiple", True)
        result3.solutions = [-1.0, 1.0]
        
        self.test_results[1] = result1
        self.test_results[2] = result2
        self.test_results[3] = result3
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_qalc_document(self):
        """测试保存和加载QalcTxt文档"""
        # 测试文件路径
        test_file = os.path.join(self.temp_dir, "test.qalc")
        
        # 保存文档
        success = self.file_manager.save_calculator_document(
            test_file, self.test_content, self.test_results
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))
        
        # 加载文档
        loaded_data = self.file_manager.load_calculator_document(test_file)
        
        # 验证内容
        self.assertEqual(loaded_data["content"], self.test_content)
        self.assertEqual(len(loaded_data["results"]), 3)
        
        # 验证结果数据
        self.assertEqual(loaded_data["results"][1].result, 5)
        self.assertEqual(loaded_data["results"][2].result, 20)
        self.assertEqual(loaded_data["results"][3].is_equation, True)
    
    def test_save_and_load_text_file(self):
        """测试保存和加载文本文件"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_content = "Hello, World!\nThis is a test."
        
        # 保存文本文件
        success = self.file_manager.save_text_file(test_file, test_content)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))
        
        # 加载文本文件
        loaded_content = self.file_manager.load_text_file(test_file)
        self.assertEqual(loaded_content, test_content)
    
    def test_export_to_text(self):
        """测试导出为文本格式"""
        exported_text = self.file_manager.export_to_text(self.test_content, self.test_results)
        
        lines = exported_text.split('\n')
        self.assertEqual(len(lines), 3)
        
        # 检查结果是否正确添加
        self.assertIn("= 5", lines[0])
        self.assertIn("= 20", lines[1])
        self.assertIn("x[0] = -1, x[1] = 1", lines[2])
    
    def test_file_extension_handling(self):
        """测试文件扩展名处理"""
        test_file = os.path.join(self.temp_dir, "test")
        
        # 保存时应自动添加扩展名
        success = self.file_manager.save_calculator_document(
            test_file, self.test_content, self.test_results
        )
        self.assertTrue(success)
        
        # 检查是否创建了正确扩展名的文件
        expected_file = test_file + ".qalc"
        self.assertTrue(os.path.exists(expected_file))
    
    def test_document_validation(self):
        """测试文档格式验证"""
        test_file = os.path.join(self.temp_dir, "invalid.qalc")
        
        # 创建无效的文档格式
        invalid_data = {"invalid": "format"}
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_data, f)
        
        # 尝试加载应该失败
        with self.assertRaises(Exception) as context:
            self.file_manager.load_calculator_document(test_file)
        
        self.assertIn("文档格式错误", str(context.exception))
    
    def test_file_not_exists(self):
        """测试文件不存在的情况"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.qalc")
        
        # 尝试加载不存在的文件应该失败
        with self.assertRaises(Exception) as context:
            self.file_manager.load_calculator_document(non_existent_file)
        
        self.assertIn("文件不存在", str(context.exception))
    
    def test_get_file_info(self):
        """测试获取文件信息"""
        test_file = os.path.join(self.temp_dir, "test.qalc")
        
        # 保存文件
        self.file_manager.save_calculator_document(
            test_file, self.test_content, self.test_results
        )
        
        # 获取文件信息
        file_info = self.file_manager.get_file_info(test_file)
        
        self.assertIsNotNone(file_info)
        self.assertTrue(file_info["is_qalc_file"])
        self.assertGreater(file_info["size"], 0)
        self.assertIsInstance(file_info["modified"], datetime)
    
    def test_default_settings(self):
        """测试默认设置"""
        default_settings = self.file_manager._get_default_settings()
        
        required_keys = ["precision", "angle_unit", "number_format", "font_size", "auto_save"]
        for key in required_keys:
            self.assertIn(key, default_settings)

if __name__ == '__main__':
    unittest.main()