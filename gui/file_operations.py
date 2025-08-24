"""
文件操作组件
处理文件的新建、打开、保存等操作
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os

class FileOperationsComponent:
    """文件操作组件类"""
    
    def __init__(self, main_window):
        """
        初始化文件操作组件
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.file_manager = main_window.file_manager
        
        # 文件类型定义
        self.qalc_file_types = [
            ("QalcTxt 计算书", "*.qalc"),
            ("文本文件", "*.txt"),
            ("所有文件", "*.*")
        ]
        
        self.text_file_types = [
            ("文本文件", "*.txt"),
            ("QalcTxt 计算书", "*.qalc"),
            ("所有文件", "*.*")
        ]
        
        # 绑定方法到主窗口
        self.bind_methods()
    
    def bind_methods(self):
        """绑定方法到主窗口"""
        self.main_window.new_file = self.new_file
        self.main_window.open_file = self.open_file
        self.main_window.save_file = self.save_file
        self.main_window.save_as_file = self.save_as_file
        self.main_window.quit_application = self.quit_application
        self.main_window.show_help = self.show_help
        self.main_window.show_about = self.show_about
    
    def new_file(self):
        """新建文件"""
        # 检查是否需要保存当前文件
        if not self._check_save_current():
            return
        
        # 清空编辑器
        self.main_window.text_editor.delete('1.0', 'end')
        
        # 清空结果
        self.main_window.result_manager.clear_results()
        self.main_window.result_display.config(state='normal')
        self.main_window.result_display.delete('1.0', 'end')
        self.main_window.result_display.config(state='disabled')
        
        # 重置状态
        self.main_window.current_file = None
        self.main_window.is_modified = False
        
        # 更新界面
        self.main_window.update_line_numbers()
        self.main_window.update_status_bar()
        self.main_window.update_title()
        
        # 设置焦点
        self.main_window.text_editor.focus_set()
    
    def open_file(self):
        """打开文件"""
        # 检查是否需要保存当前文件
        if not self._check_save_current():
            return
        
        # 选择文件
        file_path = filedialog.askopenfilename(
            title="打开计算书",
            filetypes=self.qalc_file_types,
            defaultextension=".qalc"
        )
        
        if not file_path:
            return
        
        try:
            # 根据文件类型加载
            if file_path.endswith('.qalc'):
                self._load_qalc_file(file_path)
            else:
                self._load_text_file(file_path)
            
            # 更新状态
            self.main_window.current_file = file_path
            self.main_window.is_modified = False
            
            # 更新界面
            self.main_window.update_line_numbers()
            self.main_window.update_status_bar()
            self.main_window.update_title()
            
            messagebox.showinfo("成功", f"文件已打开: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("错误", f"打开文件失败: {str(e)}")
    
    def save_file(self):
        """保存文件"""
        if self.main_window.current_file:
            self._save_to_file(self.main_window.current_file)
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """另存为文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存计算书",
            filetypes=self.qalc_file_types,
            defaultextension=".qalc"
        )
        
        if file_path:
            self._save_to_file(file_path)
            self.main_window.current_file = file_path
            self.main_window.update_title()
    
    def _save_to_file(self, file_path):
        """
        保存到指定文件
        
        Args:
            file_path: 文件路径
        """
        try:
            # 获取内容
            content = self.main_window.text_editor.get('1.0', 'end-1c')
            
            # 获取结果
            results = self.main_window.result_manager.get_all_results()
            
            # 根据文件类型保存
            if file_path.endswith('.qalc'):
                success = self.file_manager.save_calculator_document(
                    file_path, content, results
                )
            else:
                # 保存为文本文件（包含结果）
                content_with_results = self.file_manager.export_to_text(content, results)
                success = self.file_manager.save_text_file(file_path, content_with_results)
            
            if success:
                self.main_window.is_modified = False
                self.main_window.update_title()
                self.main_window.update_status_bar()
                messagebox.showinfo("成功", f"文件已保存: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("错误", "保存文件失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存文件失败: {str(e)}")
    
    def _load_qalc_file(self, file_path):
        """
        加载QalcTxt格式文件
        
        Args:
            file_path: 文件路径
        """
        document_data = self.file_manager.load_calculator_document(file_path)
        
        # 清空当前内容
        self.main_window.text_editor.delete('1.0', 'end')
        self.main_window.result_manager.clear_results()
        
        # 加载文本内容
        self.main_window.text_editor.insert('1.0', document_data["content"])
        
        # 恢复计算结果
        for line_num, result_data in document_data["results"].items():
            self.main_window.result_manager.results[line_num] = result_data
        
        # 更新结果显示
        if hasattr(self.main_window, 'text_editor_component'):
            self.main_window.text_editor_component._update_all_results_display()
    
    def _load_text_file(self, file_path):
        """
        加载文本文件
        
        Args:
            file_path: 文件路径
        """
        content = self.file_manager.load_text_file(file_path)
        
        # 清空当前内容
        self.main_window.text_editor.delete('1.0', 'end')
        self.main_window.result_manager.clear_results()
        
        # 加载文本内容
        self.main_window.text_editor.insert('1.0', content)
        
        # 清空结果显示
        self.main_window.result_display.config(state='normal')
        self.main_window.result_display.delete('1.0', 'end')
        self.main_window.result_display.config(state='disabled')
    
    def _check_save_current(self):
        """
        检查是否需要保存当前文件
        
        Returns:
            是否可以继续操作
        """
        if not self.main_window.is_modified:
            return True
        
        result = messagebox.askyesnocancel(
            "保存文件",
            "当前文件已修改，是否保存？\n\n是：保存后继续\n否：不保存继续\n取消：取消操作"
        )
        
        if result is True:  # 保存
            self.save_file()
            return not self.main_window.is_modified  # 保存成功才继续
        elif result is False:  # 不保存
            return True
        else:  # 取消
            return False
    
    def quit_application(self):
        """退出应用程序"""
        # 检查是否需要保存
        if not self._check_save_current():
            return
        
        # 退出程序
        self.main_window.root.quit()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """QalcTxt Python计算器 使用说明

基本功能：
• 输入数学表达式，按 Enter 键计算当前行
• 按 Shift+Enter 键计算所有行
• 支持可拖动的分隔栏和文本换行显示

支持的运算：
• 基本运算: +, -, *, /, **, %, //
• 数学函数: sin, cos, tan, log, exp, sqrt 等
• 常数: pi, e

方程求解：
• 单个方程: x^2 - 5*x + 6 = 0
• solve函数: solve(x^2 - 5*x + 6, x)
• 方程组新语法: x,y:x+y=1,x-y=1
• 多变量solve: solve(x+y-11,x-y-1.0,[x,y])
• 多解显示格式: x[0] = 2, x[1] = 3

行引用：
• @3 表示引用第3行的结果
• @3.0 表示引用第3行第一个解
• @3.1 表示引用第3行第二个解
• @1.1.0 表示引用第1行第2个变量的第1个解（方程组）
• 智能行引用更新（插入/删除行时自动调整）

注释：
• 使用 # 表示注释
• 注释后的内容不会被计算

智能回车：
• 在有结果的行末回车：只重新计算，不换行
• 在最后一行的行末回车：计算并换行
• 在中间位置回车：计算并换行

快捷键：
• Enter: 计算当前行
• Shift+Enter: 计算所有行
• Ctrl+S: 保存文件
• Ctrl+O: 打开文件
• Ctrl+N: 新建文件
• Ctrl+Z: 撤销
• Ctrl+Y: 重做
• Ctrl+A: 全选

示例用法：
1. 基本计算: 2 + 3 * 4
2. 单个方程: x^2 = 9
3. 方程组: x,y:x+y=11,x-y=1
4. solve函数: solve(x^2-4, x)
5. 行引用: @1 + @2
6. 多解引用: @3.0 + @3.1

文件格式：
• .qalc: QalcTxt格式，保存完整计算历史
• .txt: 纯文本格式"""
        
        messagebox.showinfo("使用说明", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """QalcTxt Python计算器 v1.0

一个功能强大的文本式计算器，支持：
• 实时数学计算
• 方程求解
• 行间结果引用
• 注释支持
• 计算历史保存

技术特性：
• 基于 Python 和 tkinter
• 使用 SymPy 进行符号计算
• 支持复数和高精度计算
• 安全的表达式求值

开发团队：Calculator Team
版本：1.0.0
开源许可：MIT License"""
        
        messagebox.showinfo("关于", about_text)