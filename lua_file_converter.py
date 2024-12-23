import os
import subprocess
import time  # 导入 time 模块
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit, QHBoxLayout, QFileDialog, QMessageBox

class LuaFilePathViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lua File Path Viewer")
        self.setGeometry(100, 100, 400, 400)

        # 创建文本框用于显示Lua文件路径
        self.path_display = QTextEdit(self)
        self.path_display.setReadOnly(True)
        self.path_display.setPlaceholderText("选择目录或Lua文件后，路径将显示在这里...")

        # 创建输出显示区域
        self.output_display = QTextEdit(self)
        self.output_display.setReadOnly(True)
        self.output_display.setPlaceholderText("Lua脚本输出将在这里显示...")

        # 创建进度标签
        self.progress_label = QLabel("进度: 0/0", self)

        # 创建添加Lua文件按钮
        self.browse_file_button = QPushButton("添加 Lua 文件", self)

        # 创建添加文件夹按钮
        self.browse_folder_button = QPushButton("添加 文件夹", self)

        # 创建开始按钮
        self.start_button = QPushButton("开始", self)

        # 创建停止按钮
        self.stop_button = QPushButton("停止", self)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.browse_file_button)
        button_layout.addWidget(self.browse_folder_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)  # 添加停止按钮

        # 布局设置
        layout = QVBoxLayout()
        layout.addWidget(self.path_display)
        layout.addLayout(button_layout)
        layout.addWidget(self.output_display)  # 添加输出显示区域
        layout.addWidget(self.progress_label)  # 添加进度标签

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.file_paths = []  # 用于存储文件路径
        self.folder_path = ""  # 用于存储文件夹路径
        self.current_process = None  # 用于存储当前运行的进程
        self.is_stopped = False  # 用于标记是否停止处理

        # 连接按钮点击事件
        self.browse_file_button.clicked.connect(self.browse_files)
        self.browse_folder_button.clicked.connect(self.browse_folder)
        self.start_button.clicked.connect(self.start_processing)  # 连接开始按钮事件
        self.stop_button.clicked.connect(self.stop_processing)  # 创建停止按钮并连接事件

    def browse_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "选择 Lua 文件", "", "Lua Files (*.lua);;All Files (*)", options=options)
        if files:
            self.file_paths = files  # 保存选择的文件路径
            self.update_path_display(is_file_selection=True)  # 传递文件选择标志
            self.update_progress_label(0, len(self.file_paths))  # 更新进度标签为 0/路径数

    def browse_folder(self):
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "", options=options)
        if folder:
            self.folder_path = folder  # 保存选择的文件夹路径
            self.file_paths = self.get_all_lua_files(folder)  # 获取所有Lua文件
            self.update_path_display(is_file_selection=False)  # 传递文件夹选择标志
            self.update_progress_label(0, len(self.file_paths))  # 更新进度标签为 0/路径数

    def get_all_lua_files(self, folder):
        lua_files = []
        for root, _, files in os.walk(folder):  # 递归遍历文件夹
            for file in files:
                if file.endswith('.lua'):
                    lua_files.append(os.path.join(root, file))  # 添加整路径
        return lua_files

    def update_path_display(self, is_file_selection):
        if is_file_selection:
            # 使用一级目录作为相对路径
            relative_paths = [os.path.relpath(path, os.path.dirname(path)) for path in self.file_paths]
        else:
            # 使用选择的文件夹作为相对路径
            relative_paths = [os.path.relpath(path, self.folder_path) for path in self.file_paths]
        
        self.path_display.setPlainText("\n".join(relative_paths))  # 更新路径显示框

    def update_progress_label(self, current, total, current_file=None):
        if current_file:
            self.progress_label.setText(f"进度: {current}/{total} - 当前文件: {os.path.basename(current_file)}")
        else:
            self.progress_label.setText(f"进度: {current}/{total}")

    def start_processing(self):
        if not self.file_paths:  # 检查是否有有效路径
            QMessageBox.warning(self, "警告", "请先选择 Lua 文件或文件夹！")  # 弹出警告框
            return  # 不运行后续代码

        self.output_display.clear()  # 清空输出内容
        total_files = len(self.file_paths)  # 获取文件总数
        self.is_stopped = False  # 重置停止标志
        start_time = time.time()  # 记录开始时间

        for index, file_path in enumerate(self.file_paths):
            if self.is_stopped:  # 检查是否已请求停止
                break

            # 去掉文件后缀
            file_path_without_extension = os.path.splitext(file_path)[0]
            print(f"Processing: {file_path_without_extension}")  # 调试信息，显示正在处理的文件
            
            # 使用 Popen 启动 Lua 脚本
            self.current_process = subprocess.Popen(['lua', 'formatLuaFile.lua', file_path_without_extension], 
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')

            # 实时读取输出
            while True:
                output = self.current_process.stdout.readline()  # 逐行读取输出
                if output:  # 如果有输出
                    self.output_display.append(output.strip())  # 显示输出并去掉多余空格
                    self.output_display.verticalScrollBar().setValue(self.output_display.verticalScrollBar().maximum())  # 滚动到最新输出
                    QApplication.processEvents()  # 处理 GUI 事件，确保输出实时更新

                if output == '' and self.current_process.poll() is not None:
                    break  # 如果没有输出且进程已结束，退出循环

                if self.is_stopped:  # 检查是否已请求停止
                    if self.current_process:  # 确保当前进程不为 None
                        self.current_process.terminate()  # 停止当前进程
                        self.output_display.append("处理已停止。")  # 显示停止信息
                    break

            # 等待进程结束并获取错误输出
            if self.current_process:  # 确保当前进程不为 None
                stderr_output = self.current_process.stderr.read()
                if stderr_output:
                    self.output_display.append(f"错误: {stderr_output.strip()}")  # 显示错误信息
            
            # 显示当前正在处理的文件
            self.output_display.append(f"正在处理文件: {file_path}")

            # 更新进度标签，传递当前文件名
            self.update_progress_label(index + 1, total_files, file_path)
            
            # 处理 GUI 事件，确保进度标签更新
            QApplication.processEvents()

        # 计算总用时
        end_time = time.time()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算用时
        elapsed_time_str = f"{elapsed_time:.2f}秒"  # 格式化用时

        # 延迟 1-2 秒后更新输出信息
        time.sleep(1)  # 延迟 1 秒
        self.output_display.append(f"\n\n==========================================================")
        self.output_display.append(f"\n所有脚本处理完成！")
        self.output_display.append(f"完成任务数量: {total_files}")
        self.output_display.append(f"总用时: {elapsed_time_str}")
        self.output_display.append("作者: 爱玩游戏的馒头")  # 替换为您的名字
        self.output_display.append("QQ: 97674543\n\n")  # 替换为您的名字

        # 所有脚本处理完成后弹出提示框
        QMessageBox.information(self, "完成", "所有脚本处理完成！")  # 弹出信息框

    def stop_processing(self):
        self.is_stopped = True  # 设置停止标志
        if self.current_process:  # 确保当前进程不为 None
            self.current_process.terminate()  # 停止当前运行的进���
            self.current_process = None  # 清空当前进程
            self.output_display.append("处理已停止。")  # 显示停止信息

if __name__ == "__main__":
    app = QApplication([])
    window = LuaFilePathViewer()
    window.show()
    app.exec_()
