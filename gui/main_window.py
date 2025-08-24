"""
主窗口模块
管理整个应用程序的主窗口和菜单
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calculator import CalculatorEngine
from core.parser import ExpressionParser
from core.equation_solver import EquationSolver
from core.result_manager import ResultManager
from utils.file_manager import FileManager

class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.root.title("Python计算器 - QalcTxt")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # 初始化核心组件
        self.calculator = CalculatorEngine()
        self.parser = ExpressionParser()
        self.equation_solver = EquationSolver()
        self.result_manager = ResultManager()
        self.file_manager = FileManager()
        
        # 当前文件路径
        self.current_file = None
        self.is_modified = False
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_menu()
        self.create_widgets()
        self.create_layout()
        
        # 初始化事件处理方法为None，等待组件设置
        self.text_editor_component = None
        self.file_operations_component = None
        
        # 用于跟踪行数变化
        self.previous_line_count = 1
        
        # 设置焦点
        self.text_editor.focus_set()
    
    def setup_styles(self):
        """设置界面样式"""
        self.style = ttk.Style()
        
        # 设置字体
        self.editor_font = ("Consolas", 12)
        self.result_font = ("Consolas", 11)
        
        # 配置颜色
        self.bg_color = "#ffffff"
        self.text_color = "#000000"
        self.result_color = "#006400"
        self.error_color = "#dc3545"
        self.comment_color = "#6a6a6a"
        self.line_number_bg = "#f5f5f5"
        self.line_number_fg = "#666666"
    
    def create_menu(self):
        """创建菜单栏"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="文件(F)", menu=file_menu)
        file_menu.add_command(label="新建 (Ctrl+N)", command=self.new_file)
        file_menu.add_command(label="打开 (Ctrl+O)", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="保存 (Ctrl+S)", command=self.save_file)
        file_menu.add_command(label="另存为 (Ctrl+Shift+S)", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit_application)
        
        # 编辑菜单
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="编辑(E)", menu=edit_menu)
        edit_menu.add_command(label="撤销 (Ctrl+Z)", command=self.undo)
        edit_menu.add_command(label="重做 (Ctrl+Y)", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="全选 (Ctrl+A)", command=self.select_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="清空结果", command=self.clear_results)
        
        # 计算菜单
        calc_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="计算(C)", menu=calc_menu)
        calc_menu.add_command(label="计算当前行 (Enter)", command=self.calculate_current_line)
        calc_menu.add_command(label="计算所有行 (Shift+Enter)", command=self.calculate_all_lines)
        calc_menu.add_separator()
        calc_menu.add_command(label="清空所有计算结果", command=self.clear_all_results)
        
        # 帮助菜单
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="帮助(H)", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.root)
        
        # 使用PanedWindow创建可拖动的分隔栏
        self.paned_window = ttk.PanedWindow(self.main_frame, orient='horizontal')
        
        # 左侧框架（行号+文本编辑器）
        self.left_frame = ttk.Frame(self.paned_window)
        
        # 行号显示
        self.line_numbers = tk.Text(
            self.left_frame,
            width=4,
            height=1,
            bg=self.line_number_bg,
            fg=self.line_number_fg,
            font=self.editor_font,
            state='disabled',
            wrap='none',
            takefocus=False,
            border=0,
            padx=5,
            pady=5
        )
        
        # 文本编辑器（设置为换行显示）
        self.text_editor = tk.Text(
            self.left_frame,
            font=self.editor_font,
            bg=self.bg_color,
            fg=self.text_color,
            wrap='word',  # 改为word换行
            undo=True,
            maxundo=50,
            padx=10,
            pady=5,
            insertbackground=self.text_color,
            selectbackground="#3399ff",
            selectforeground="white"
        )
        
        # 右侧框架（结果显示）
        self.right_frame = ttk.Frame(self.paned_window)
        
        # 结果显示区域（设置为换行显示）
        self.result_display = tk.Text(
            self.right_frame,
            width=25,
            font=self.result_font,
            bg="#f8f9fa",
            fg=self.result_color,
            wrap='word',  # 改为word换行
            state='disabled',
            takefocus=False,
            padx=10,
            pady=5
        )
        
        # 滚动条
        self.v_scrollbar_left = ttk.Scrollbar(self.left_frame, orient='vertical')
        self.v_scrollbar_right = ttk.Scrollbar(self.right_frame, orient='vertical')
        self.h_scrollbar = ttk.Scrollbar(self.main_frame, orient='horizontal')
        
        # 状态栏
        self.status_frame = ttk.Frame(self.root)
        self.status_label = ttk.Label(
            self.status_frame,
            text="就绪 | 行: 1, 列: 1",
            relief='sunken',
            anchor='w'
        )
        
        # 配置滚动
        self.text_editor.config(yscrollcommand=self.v_scrollbar_left.set)
        self.text_editor.config(xscrollcommand=self.h_scrollbar.set)
        self.line_numbers.config(yscrollcommand=self.v_scrollbar_left.set)
        self.result_display.config(yscrollcommand=self.v_scrollbar_right.set)
        
        self.v_scrollbar_left.config(command=self.sync_scroll_left)
        self.v_scrollbar_right.config(command=self.result_display.yview)
        self.h_scrollbar.config(command=self.text_editor.xview)
    
    def create_layout(self):
        """创建布局"""
        # 主框架布局
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # PanedWindow布局
        self.paned_window.pack(fill='both', expand=True)
        
        # 左侧框架布局（行号+文本编辑器）
        self.left_frame.grid_columnconfigure(1, weight=1)
        self.left_frame.grid_rowconfigure(0, weight=1)
        
        # 行号
        self.line_numbers.grid(row=0, column=0, sticky='ns')
        
        # 文本编辑器
        self.text_editor.grid(row=0, column=1, sticky='nsew')
        
        # 左侧垂直滚动条
        self.v_scrollbar_left.grid(row=0, column=2, sticky='ns')
        
        # 右侧框架布局（结果显示）
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        
        # 结果显示
        self.result_display.grid(row=0, column=0, sticky='nsew')
        
        # 右侧垂直滚动条
        self.v_scrollbar_right.grid(row=0, column=1, sticky='ns')
        
        # 将左右框架添加到PanedWindow
        self.paned_window.add(self.left_frame, weight=2)  # 左侧占更多空间
        self.paned_window.add(self.right_frame, weight=1)
        
        # 水平滚动条
        self.h_scrollbar.pack(side='bottom', fill='x')
        
        # 状态栏
        self.status_frame.pack(side='bottom', fill='x')
        self.status_label.pack(side='left', fill='x', expand=True)
    
    def initialize_components(self):
        """初始化组件并绑定事件"""
        # 重新绑定菜单项（在组件初始化后）
        self.rebind_menu_commands()
        
        # 绑定事件（在组件初始化后）
        self.bind_events()
    
    def rebind_menu_commands(self):
        """重新绑定菜单命令"""
        # 重新创建菜单以使用正确的方法引用
        self.create_menu()
    
    def bind_events(self):
        """绑定事件"""
        # 键盘事件
        self.text_editor.bind('<Return>', self.on_enter_key)
        self.text_editor.bind('<Shift-Return>', self.on_shift_enter_key)
        self.text_editor.bind('<KeyRelease>', self.on_text_changed)
        self.text_editor.bind('<Button-1>', self.on_text_clicked)
        self.text_editor.bind('<Control-s>', lambda e: self.save_file())
        self.text_editor.bind('<Control-o>', lambda e: self.open_file())
        self.text_editor.bind('<Control-n>', lambda e: self.new_file())
        
        # 滚动同步（分别绑定到不同组件）
        self.text_editor.bind('<MouseWheel>', self.on_mouse_wheel)
        self.line_numbers.bind('<MouseWheel>', self.on_mouse_wheel)
        self.result_display.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
    
    def sync_scroll_left(self, *args):
        """同步左侧垂直滚动（行号和文本编辑器）"""
        self.text_editor.yview(*args)
        self.line_numbers.yview(*args)
    
    def on_mouse_wheel(self, event):
        """鼠标滚轮事件"""
        # 判断鼠标在哪个区域
        widget = event.widget
        if widget == self.text_editor or widget == self.line_numbers:
            # 在左侧区域，同步滚动行号和文本编辑器
            self.text_editor.yview_scroll(int(-1 * (event.delta / 120)), "units")
            self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif widget == self.result_display:
            # 在结果显示区域，只滚动结果显示
            self.result_display.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
    
    def update_line_numbers(self):
        """更新行号显示"""
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        
        # 获取文本总行数
        content = self.text_editor.get('1.0', 'end-1c')
        lines = content.split('\n')
        line_count = len(lines)
        
        # 生成行号
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.insert('1.0', line_numbers_text)
        
        self.line_numbers.config(state='disabled')
    
    def update_status_bar(self):
        """更新状态栏"""
        try:
            cursor_pos = self.text_editor.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            status_text = f"就绪 | 行: {line}, 列: {int(col) + 1}"
            
            if self.is_modified:
                status_text = "已修改 | " + status_text
            
            self.status_label.config(text=status_text)
        except:
            pass
    
    def on_text_changed(self, event=None):
        """文本改变事件"""
        self.is_modified = True
        
        # 检查行数变化
        content = self.text_editor.get('1.0', 'end-1c')
        lines = content.split('\n')
        current_line_count = len(lines)
        
        # 如果行数发生变化，通知组件处理
        if hasattr(self, 'text_editor_component') and self.text_editor_component:
            if current_line_count != self.previous_line_count:
                self.text_editor_component.handle_line_count_change(
                    self.previous_line_count, current_line_count
                )
        
        self.previous_line_count = current_line_count
        
        self.update_line_numbers()
        self.update_status_bar()
        self.update_title()
    
    def on_text_clicked(self, event=None):
        """文本点击事件"""
        self.root.after_idle(self.update_status_bar)
    
    def update_title(self):
        """更新窗口标题"""
        title = "Python计算器 - QalcTxt"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title = f"{filename} - {title}"
        if self.is_modified:
            title = "* " + title
        self.root.title(title)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()
    
    # 菜单命令方法（这些将在其他模块中实现具体功能）
    def new_file(self): pass
    def open_file(self): pass
    def save_file(self): pass
    def save_as_file(self): pass
    def quit_application(self): pass
    def undo(self): pass
    def redo(self): pass
    def select_all(self): pass
    def clear_results(self): pass
    def calculate_current_line(self): pass
    def calculate_all_lines(self): pass
    def clear_all_results(self): pass
    def show_help(self): pass
    def show_about(self): pass
    def on_enter_key(self, event): pass
    def on_shift_enter_key(self, event): pass