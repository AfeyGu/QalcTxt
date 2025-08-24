"""
文本编辑器组件
实现多行输入、键盘事件处理和计算功能
"""

import tkinter as tk
from tkinter import messagebox
import re

class TextEditorComponent:
    """文本编辑器组件类，扩展主窗口的编辑器功能"""
    
    def __init__(self, main_window):
        """
        初始化文本编辑器组件
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.text_editor = main_window.text_editor
        self.result_display = main_window.result_display
        self.calculator = main_window.calculator
        self.parser = main_window.parser
        self.equation_solver = main_window.equation_solver
        self.result_manager = main_window.result_manager
        
        # 绑定具体的方法实现
        self.bind_methods()
    
    def bind_methods(self):
        """绑定方法到主窗口"""
        # 键盘事件
        self.main_window.on_enter_key = self.on_enter_key
        self.main_window.on_shift_enter_key = self.on_shift_enter_key
        
        # 计算方法
        self.main_window.calculate_current_line = self.calculate_current_line
        self.main_window.calculate_all_lines = self.calculate_all_lines
        self.main_window.clear_all_results = self.clear_all_results
        
        # 编辑方法
        self.main_window.undo = self.undo
        self.main_window.redo = self.redo
        self.main_window.select_all = self.select_all
        self.main_window.clear_results = self.clear_results
    
    def on_enter_key(self, event):
        """
        Enter键事件处理
        
        Args:
            event: 键盘事件
        """
        # 获取当前光标位置
        cursor_pos = self.text_editor.index(tk.INSERT)
        current_line = int(cursor_pos.split('.')[0])
        current_col = int(cursor_pos.split('.')[1])
        
        # 获取总行数
        content = self.text_editor.get('1.0', 'end-1c')
        total_lines = len(content.split('\n'))
        
        # 获取当前行内容
        line_start = f"{current_line}.0"
        line_end = f"{current_line}.end"
        line_content = self.text_editor.get(line_start, line_end)
        
        # 检查当前行是否已有计算结果
        has_result = self.result_manager.get_result(current_line) is not None
        
        # 获取光标到行末的内容
        content_after_cursor = line_content[current_col:]
        
        # 判断是否在最后一行
        is_last_line = current_line == total_lines
        
        # 如果当前行有结果且光标在行末且不是最后一行，则不换行，只重新计算
        if has_result and not content_after_cursor.strip() and not is_last_line:
            # 重新计算当前行
            self.calculate_current_line()
            # 阻止默认的Enter行为
            return "break"
        
        # 其他情况：
        # 1. 在最后一行的行末（无论是否有结果）
        # 2. 在中间位置换行
        # 3. 在没有结果的行末
        # 都计算当前行并插入新行
        self.calculate_current_line()
        
        # 插入新行
        self.text_editor.insert(tk.INSERT, '\n')
        
        # 更新行号和状态
        self.main_window.update_line_numbers()
        self.main_window.update_status_bar()
        
        # 阻止默认的Enter行为
        return "break"
    
    def on_shift_enter_key(self, event):
        """
        Shift+Enter键事件处理
        
        Args:
            event: 键盘事件
        """
        # 计算所有行
        self.calculate_all_lines()
        
        # 阻止默认行为
        return "break"
    
    def calculate_current_line(self):
        """计算当前行"""
        try:
            # 获取当前行号
            current_line = int(self.text_editor.index(tk.INSERT).split('.')[0])
            
            # 获取当前行内容
            line_start = f"{current_line}.0"
            line_end = f"{current_line}.end"
            line_content = self.text_editor.get(line_start, line_end)
            
            # 计算该行
            self._calculate_line(current_line, line_content)
            
        except Exception as e:
            messagebox.showerror("错误", f"计算当前行时出错: {str(e)}")
    
    def calculate_all_lines(self):
        """计算所有行"""
        try:
            # 清空之前的结果
            self.result_manager.clear_results()
            
            # 获取所有内容
            content = self.text_editor.get('1.0', 'end-1c')
            lines = content.split('\n')
            
            # 逐行计算
            for line_num, line_content in enumerate(lines, 1):
                if line_content.strip():  # 跳过空行
                    self._calculate_line(line_num, line_content)
            
            # 更新结果显示
            self._update_all_results_display()
            
        except Exception as e:
            messagebox.showerror("错误", f"计算所有行时出错: {str(e)}")
    
    def _calculate_line(self, line_number, line_content):
        """
        计算单行内容
        
        Args:
            line_number: 行号
            line_content: 行内容
        """
        try:
            # 解析表达式
            expression, is_empty, original = self.parser.parse_expression(
                line_content, self.result_manager
            )
            
            # 如果是空行或注释行，跳过计算
            if is_empty:
                return
            
            # 判断是否为方程
            is_equation = self.equation_solver.is_equation(expression)
            
            # 执行计算
            if is_equation:
                result = self.equation_solver.solve_equation(expression)
            else:
                result = self.calculator.calculate(expression)
            
            # 存储结果
            self.result_manager.store_result(
                line_number, original, result, is_equation
            )
            
            # 更新单行结果显示
            self._update_line_result_display(line_number)
            
        except Exception as e:
            # 存储错误结果
            error_msg = f"错误: {str(e)}"
            self.result_manager.store_result(line_number, line_content, error_msg, False)
            self._update_line_result_display(line_number)
    
    def _update_line_result_display(self, line_number):
        """
        更新单行结果显示
        
        Args:
            line_number: 行号
        """
        # 获取结果
        formatted_result = self.result_manager.get_formatted_result(line_number)
        
        if formatted_result:
            # 启用编辑
            self.result_display.config(state='normal')
            
            # 获取结果显示区域的对应行
            result_line_start = f"{line_number}.0"
            result_line_end = f"{line_number}.end"
            
            # 清空该行的旧结果
            try:
                self.result_display.delete(result_line_start, result_line_end)
            except:
                pass
            
            # 确保结果显示区域有足够的行
            self._ensure_result_display_lines(line_number)
            
            # 插入新结果
            self.result_display.insert(result_line_start, f"= {formatted_result}")
            
            # 设置颜色
            if formatted_result.startswith("错误"):
                self.result_display.tag_add("error", result_line_start, f"{line_number}.end")
                self.result_display.tag_config("error", foreground=self.main_window.error_color)
            else:
                self.result_display.tag_add("result", result_line_start, f"{line_number}.end")
                self.result_display.tag_config("result", foreground=self.main_window.result_color)
            
            # 禁用编辑
            self.result_display.config(state='disabled')
    
    def _update_all_results_display(self):
        """更新所有结果显示"""
        # 启用编辑
        self.result_display.config(state='normal')
        
        # 清空所有内容
        self.result_display.delete('1.0', 'end')
        
        # 获取文本编辑器的行数
        content = self.text_editor.get('1.0', 'end-1c')
        lines = content.split('\n')
        
        # 为每行添加结果
        for line_num in range(1, len(lines) + 1):
            formatted_result = self.result_manager.get_formatted_result(line_num)
            
            if formatted_result:
                result_text = f"= {formatted_result}\n"
            else:
                result_text = "\n"
            
            self.result_display.insert('end', result_text)
            
            # 设置颜色
            if formatted_result and formatted_result.startswith("错误"):
                start_index = f"{line_num}.0"
                end_index = f"{line_num}.end"
                self.result_display.tag_add("error", start_index, end_index)
                self.result_display.tag_config("error", foreground=self.main_window.error_color)
            elif formatted_result:
                start_index = f"{line_num}.0"
                end_index = f"{line_num}.end"
                self.result_display.tag_add("result", start_index, end_index)
                self.result_display.tag_config("result", foreground=self.main_window.result_color)
        
        # 禁用编辑
        self.result_display.config(state='disabled')
    
    def _ensure_result_display_lines(self, line_number):
        """
        确保结果显示区域有足够的行数
        
        Args:
            line_number: 需要的行号
        """
        # 获取当前结果显示区域的内容
        current_content = self.result_display.get('1.0', 'end-1c')
        current_lines = current_content.split('\n') if current_content else ['']
        
        # 如果行数不够，添加空行
        while len(current_lines) < line_number:
            self.result_display.insert('end', '\n')
            current_lines.append('')
    
    def clear_all_results(self):
        """清空所有计算结果"""
        try:
            # 清空结果管理器
            self.result_manager.clear_results()
            
            # 清空结果显示
            self.result_display.config(state='normal')
            self.result_display.delete('1.0', 'end')
            
            # 重新填充空行以匹配文本编辑器
            content = self.text_editor.get('1.0', 'end-1c')
            lines = content.split('\n')
            for _ in lines:
                self.result_display.insert('end', '\n')
            
            self.result_display.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("错误", f"清空结果时出错: {str(e)}")
    
    def clear_results(self):
        """清空当前行结果"""
        try:
            # 获取当前行号
            current_line = int(self.text_editor.index(tk.INSERT).split('.')[0])
            
            # 从结果管理器中删除
            self.result_manager.remove_result(current_line)
            
            # 清空显示
            self.result_display.config(state='normal')
            result_line_start = f"{current_line}.0"
            result_line_end = f"{current_line}.end"
            self.result_display.delete(result_line_start, result_line_end)
            self.result_display.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("错误", f"清空当前行结果时出错: {str(e)}")
    
    def undo(self):
        """撤销操作"""
        try:
            self.text_editor.edit_undo()
            self.main_window.update_line_numbers()
            self.main_window.update_status_bar()
        except tk.TclError:
            pass  # 没有可撤销的操作
    
    def redo(self):
        """重做操作"""
        try:
            self.text_editor.edit_redo()
            self.main_window.update_line_numbers()
            self.main_window.update_status_bar()
        except tk.TclError:
            pass  # 没有可重做的操作
    
    def handle_line_count_change(self, old_line_count, new_line_count):
        """
        处理行数变化，调整结果管理器中的行引用和文本中的@引用
        
        Args:
            old_line_count: 旧的行数
            new_line_count: 新的行数
        """
        try:
            # 获取当前光标位置，用于判断变化位置
            cursor_pos = self.text_editor.index(tk.INSERT)
            change_line = int(cursor_pos.split('.')[0])
            
            if new_line_count > old_line_count:
                # 增加了行
                lines_added = new_line_count - old_line_count
                self._handle_lines_inserted(change_line, lines_added)
                self._update_text_references_after_insert(change_line, lines_added)
            elif new_line_count < old_line_count:
                # 减少了行
                lines_deleted = old_line_count - new_line_count
                self._handle_lines_deleted(change_line, lines_deleted)
                self._update_text_references_after_delete(change_line, lines_deleted)
            
            # 更新结果显示
            self._update_all_results_display()
            
        except Exception as e:
            print(f"处理行数变化时出错: {str(e)}")
    
    def _update_text_references_after_insert(self, insert_line, lines_added):
        """
        在插入行后更新文本中的@引用
        
        Args:
            insert_line: 插入位置
            lines_added: 插入的行数
        """
        try:
            # 获取所有文本内容
            content = self.text_editor.get('1.0', 'end-1c')
            
            # 使用正则表达式查找所有@引用
            import re
            pattern = r'@(\d+)(?:\.(\d+)(?:\.(\d+))?)?'
            
            def replace_reference(match):
                line_ref = int(match.group(1))
                first_index = match.group(2)
                second_index = match.group(3)
                
                # 如果引用的行号大于等于插入位置，则需要加上插入的行数
                if line_ref >= insert_line:
                    new_line_ref = line_ref + lines_added
                    if second_index:
                        return f'@{new_line_ref}.{first_index}.{second_index}'
                    elif first_index:
                        return f'@{new_line_ref}.{first_index}'
                    else:
                        return f'@{new_line_ref}'
                else:
                    # 在插入位置之前的引用不变
                    return match.group(0)
            
            # 替换所有引用
            updated_content = re.sub(pattern, replace_reference, content)
            
            # 如果内容有变化，更新文本编辑器
            if updated_content != content:
                # 保存当前光标位置
                cursor_pos = self.text_editor.index(tk.INSERT)
                
                # 更新内容
                self.text_editor.delete('1.0', 'end')
                self.text_editor.insert('1.0', updated_content)
                
                # 恢复光标位置
                try:
                    self.text_editor.mark_set(tk.INSERT, cursor_pos)
                except:
                    pass
                    
        except Exception as e:
            print(f"更新文本引用时出错: {str(e)}")
    
    def _update_text_references_after_delete(self, delete_line, lines_deleted):
        """
        在删除行后更新文本中的@引用
        
        Args:
            delete_line: 删除位置
            lines_deleted: 删除的行数
        """
        try:
            # 获取所有文本内容
            content = self.text_editor.get('1.0', 'end-1c')
            
            # 使用正则表达式查找所有@引用
            import re
            pattern = r'@(\d+)(?:\.(\d+)(?:\.(\d+))?)?'
            
            def replace_reference(match):
                line_ref = int(match.group(1))
                first_index = match.group(2)
                second_index = match.group(3)
                
                # 判断引用的行号位置
                if line_ref < delete_line:
                    # 在删除位置之前的引用不变
                    return match.group(0)
                elif line_ref >= delete_line and line_ref < delete_line + lines_deleted:
                    # 在删除范围内的引用，标记为无效
                    return f'@INVALID_{line_ref}'
                else:
                    # 在删除范围之后的引用，减去删除的行数
                    new_line_ref = line_ref - lines_deleted
                    if second_index:
                        return f'@{new_line_ref}.{first_index}.{second_index}'
                    elif first_index:
                        return f'@{new_line_ref}.{first_index}'
                    else:
                        return f'@{new_line_ref}'
            
            # 替换所有引用
            updated_content = re.sub(pattern, replace_reference, content)
            
            # 如果内容有变化，更新文本编辑器
            if updated_content != content:
                # 保存当前光标位置
                cursor_pos = self.text_editor.index(tk.INSERT)
                
                # 更新内容
                self.text_editor.delete('1.0', 'end')
                self.text_editor.insert('1.0', updated_content)
                
                # 恢复光标位置
                try:
                    self.text_editor.mark_set(tk.INSERT, cursor_pos)
                except:
                    pass
                    
        except Exception as e:
            print(f"更新文本引用时出错: {str(e)}")
    
    def _handle_lines_inserted(self, insert_position, insert_count):
        """
        处理行插入，调整后面行的结果
        
        Args:
            insert_position: 插入位置（在哪一行之后插入）
            insert_count: 插入的行数
        """
        # 获取所有结果
        all_results = self.result_manager.get_all_results().copy()
        
        # 清空原结果
        self.result_manager.clear_results()
        
        # 重新存储结果，调整行号
        for old_line_num, result_data in all_results.items():
            if old_line_num >= insert_position:
                # 在插入位置及以后的行，行号需要加上插入的行数
                new_line_num = old_line_num + insert_count
                self.result_manager.results[new_line_num] = result_data
                result_data.line_number = new_line_num
            else:
                # 在插入位置之前的行，行号不变
                self.result_manager.results[old_line_num] = result_data
    
    def _handle_lines_deleted(self, delete_position, delete_count):
        """
        处理行删除，调整后面行的结果
        
        Args:
            delete_position: 删除位置（从哪一行开始删除）
            delete_count: 删除的行数
        """
        # 获取所有结果
        all_results = self.result_manager.get_all_results().copy()
        
        # 清空原结果
        self.result_manager.clear_results()
        
        # 重新存储结果，调整行号
        for old_line_num, result_data in all_results.items():
            if old_line_num <= delete_position:
                # 在删除位置之前的行，行号不变
                self.result_manager.results[old_line_num] = result_data
            elif old_line_num > delete_position + delete_count:
                # 在删除区域之后的行，行号需要减去删除的行数
                new_line_num = old_line_num - delete_count
                self.result_manager.results[new_line_num] = result_data
                result_data.line_number = new_line_num
            # 在删除区域内的行，直接丢弃
    
    def select_all(self):
        """全选文本"""
        self.text_editor.tag_add('sel', '1.0', 'end')
        self.text_editor.mark_set(tk.INSERT, '1.0')
        self.text_editor.see(tk.INSERT)
        return "break"