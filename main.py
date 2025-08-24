"""
QalcTxt Python计算器 - 主程序入口
一个功能强大的文本式计算器，支持实时计算、方程求解、行引用等功能
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from gui.main_window import MainWindow
    from gui.text_editor import TextEditorComponent
    from gui.file_operations import FileOperationsComponent
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有必要的模块都已正确安装")
    sys.exit(1)

class QalcTxtApplication:
    """QalcTxt应用程序主类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.main_window = None
        self.text_editor_component = None
        self.file_operations_component = None
    
    def initialize(self):
        """初始化应用程序组件"""
        try:
            print("正在创建主窗口...")
            # 创建主窗口
            self.main_window = MainWindow()
            print("主窗口创建成功")
            
            print("正在初始化文本编辑器组件...")
            # 初始化文本编辑器组件
            self.text_editor_component = TextEditorComponent(self.main_window)
            self.main_window.text_editor_component = self.text_editor_component
            print("文本编辑器组件初始化成功")
            
            print("正在初始化文件操作组件...")
            # 初始化文件操作组件
            self.file_operations_component = FileOperationsComponent(self.main_window)
            self.main_window.file_operations_component = self.file_operations_component
            print("文件操作组件初始化成功")
            
            print("正在初始化组件并绑定事件...")
            # 初始化组件并绑定事件（在组件设置后）
            self.main_window.initialize_components()
            print("事件绑定成功")
            
            print("正在设置初始状态...")
            # 设置初始状态
            self.main_window.update_line_numbers()
            self.main_window.update_status_bar()
            print("初始化完成")
            
            return True
            
        except Exception as e:
            print(f"初始化错误: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("初始化错误", f"应用程序初始化失败: {str(e)}")
            return False
    
    def run(self):
        """运行应用程序"""
        if self.initialize():
            try:
                self.main_window.run()
            except Exception as e:
                messagebox.showerror("运行错误", f"应用程序运行时出错: {str(e)}")
        else:
            print("应用程序初始化失败")
            sys.exit(1)

def check_dependencies():
    """检查依赖库"""
    required_modules = []
    optional_modules = ['sympy']
    
    missing_required = []
    missing_optional = []
    
    print("正在检查依赖...")
    
    # 检查必需模块
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ 必需模块 {module} 已安装")
        except ImportError:
            missing_required.append(module)
            print(f"✗ 缺少必需模块: {module}")
    
    # 检查可选模块
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✓ 可选模块 {module} 已安装")
        except ImportError:
            missing_optional.append(module)
            print(f"⚠ 缺少可选模块: {module}")
    
    # 报告缺失的模块
    if missing_required:
        print(f"错误: 缺少必需的模块: {', '.join(missing_required)}")
        print("请安装这些模块后再运行程序")
        return False
    
    if missing_optional:
        print(f"警告: 缺少可选模块: {', '.join(missing_optional)}")
        print("某些功能可能不可用，建议安装这些模块以获得完整功能")
        print("安装命令: pip install " + " ".join(missing_optional))
    
    print("依赖检查完成")
    return True

def main():
    """主函数"""
    print("QalcTxt Python计算器 v1.0")
    print("正在启动...")
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        sys.exit(1)
    
    # 创建并运行应用程序
    try:
        app = QalcTxtApplication()
        app.run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行时出现未处理的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")  # 让用户看到错误信息
    finally:
        print("程序已退出")

if __name__ == "__main__":
    main()