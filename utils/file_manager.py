"""
文件管理器模块
处理计算书的保存和加载功能
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class FileManager:
    """文件管理器类"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.file_extension = ".qalc"
        self.version = "1.0"
    
    def save_calculator_document(self, file_path: str, content: str, 
                                results: Dict[int, Any], settings: Dict[str, Any] = None) -> bool:
        """
        保存计算器文档
        
        Args:
            file_path: 文件路径
            content: 文本内容
            results: 计算结果字典
            settings: 设置信息
            
        Returns:
            是否保存成功
        """
        try:
            # 确保文件扩展名正确
            if not file_path.endswith(self.file_extension):
                file_path += self.file_extension
            
            # 准备文档数据
            document_data = {
                "version": self.version,
                "created_at": datetime.now().isoformat(),
                "modified_at": datetime.now().isoformat(),
                "content": self._prepare_content_data(content, results),
                "settings": settings or self._get_default_settings()
            }
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
    
    def load_calculator_document(self, file_path: str) -> Dict[str, Any]:
        """
        加载计算器文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            文档数据字典
        """
        try:
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                document_data = json.load(f)
            
            # 验证文档格式
            self._validate_document(document_data)
            
            # 解析内容和结果
            content, results = self._parse_content_data(document_data["content"])
            
            return {
                "content": content,
                "results": results,
                "settings": document_data.get("settings", self._get_default_settings()),
                "version": document_data.get("version", "1.0"),
                "created_at": document_data.get("created_at"),
                "modified_at": document_data.get("modified_at")
            }
            
        except Exception as e:
            raise Exception(f"加载文件失败: {str(e)}")
    
    def save_text_file(self, file_path: str, content: str) -> bool:
        """
        保存为纯文本文件
        
        Args:
            file_path: 文件路径
            content: 文本内容
            
        Returns:
            是否保存成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise Exception(f"保存文本文件失败: {str(e)}")
    
    def load_text_file(self, file_path: str) -> str:
        """
        加载纯文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文本内容
        """
        try:
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"加载文本文件失败: {str(e)}")
    
    def _prepare_content_data(self, content: str, results: Dict[int, Any]) -> list:
        """
        准备内容数据
        
        Args:
            content: 文本内容
            results: 计算结果
            
        Returns:
            内容数据列表
        """
        lines = content.split('\n')
        content_data = []
        
        for line_num, line_text in enumerate(lines, 1):
            line_data = {
                "line": line_num,
                "text": line_text,
                "result": None
            }
            
            # 如果有计算结果，添加结果信息
            if line_num in results:
                result_data = results[line_num]
                line_data["result"] = {
                    "expression": result_data.expression,
                    "result": result_data.result,
                    "result_type": result_data.result_type,
                    "is_equation": result_data.is_equation,
                    "timestamp": result_data.timestamp.isoformat(),
                    "solutions": result_data.solutions if hasattr(result_data, 'solutions') else []
                }
            
            content_data.append(line_data)
        
        return content_data
    
    def _parse_content_data(self, content_data: list) -> tuple:
        """
        解析内容数据
        
        Args:
            content_data: 内容数据列表
            
        Returns:
            (文本内容, 结果字典)
        """
        lines = []
        results = {}
        
        for line_data in content_data:
            lines.append(line_data["text"])
            
            if line_data["result"]:
                from core.result_manager import ResultData
                
                result_info = line_data["result"]
                result_data = ResultData(
                    line_number=line_data["line"],
                    expression=result_info["expression"],
                    result=result_info["result"],
                    result_type=result_info["result_type"],
                    is_equation=result_info["is_equation"]
                )
                
                # 恢复时间戳
                if "timestamp" in result_info:
                    try:
                        result_data.timestamp = datetime.fromisoformat(result_info["timestamp"])
                    except:
                        result_data.timestamp = datetime.now()
                
                # 恢复解列表
                if "solutions" in result_info:
                    result_data.solutions = result_info["solutions"]
                
                results[line_data["line"]] = result_data
        
        content = '\n'.join(lines)
        return content, results
    
    def _validate_document(self, document_data: Dict[str, Any]) -> None:
        """
        验证文档格式
        
        Args:
            document_data: 文档数据
        """
        required_fields = ["version", "content"]
        for field in required_fields:
            if field not in document_data:
                raise Exception(f"文档格式错误: 缺少字段 '{field}'")
        
        if not isinstance(document_data["content"], list):
            raise Exception("文档格式错误: content 字段应为列表")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """
        获取默认设置
        
        Returns:
            默认设置字典
        """
        return {
            "precision": 10,
            "angle_unit": "radians",
            "number_format": "auto",
            "font_size": 12,
            "auto_save": True,
            "auto_save_interval": 300  # 5分钟
        }
    
    def export_to_text(self, content: str, results: Dict[int, Any]) -> str:
        """
        导出为文本格式（包含计算结果）
        
        Args:
            content: 文本内容
            results: 计算结果
            
        Returns:
            带结果的文本内容
        """
        lines = content.split('\n')
        output_lines = []
        
        for line_num, line_text in enumerate(lines, 1):
            output_line = line_text
            
            # 如果有计算结果，添加到行末
            if line_num in results:
                result_data = results[line_num]
                if result_data.result_type != "error":
                    formatted_result = self._format_result_for_export(result_data.result)
                    output_line += f"  = {formatted_result}"
            
            output_lines.append(output_line)
        
        return '\n'.join(output_lines)
    
    def _format_result_for_export(self, result: Any) -> str:
        """
        格式化结果用于导出
        
        Args:
            result: 计算结果
            
        Returns:
            格式化的结果字符串
        """
        if isinstance(result, (int, float)):
            if isinstance(result, float) and result.is_integer():
                return str(int(result))
            elif isinstance(result, float):
                return f"{result:.10g}"
            return str(result)
        else:
            return str(result)
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典或None
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "is_qalc_file": file_path.endswith(self.file_extension)
            }
        except:
            return None