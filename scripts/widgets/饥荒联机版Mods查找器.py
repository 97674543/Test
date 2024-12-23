import os
import json
import logging
import win32com.client
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QMessageBox, QLineEdit, QFileDialog, QTextEdit,
                             QDesktopWidget)
from PyQt5.QtCore import Qt, pyqtSignal
import string
import threading
from PyQt5.QtGui import (QIcon, QPixmap, QPainter, QColor)
# 配置日志记录，设置日志级别、格式以及日志文件路径
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='饥荒联机版Mods日志.log', filemode='w')

# 定义路径相关配置（方便后续修改维护）
PATH_CONFIG = {
    "wegame_apps_folder": "WeGameApps",
    "steam_apps_folder": "steamapps",
    "wegame_mods_sub_path": os.path.join("rail_apps", "饥荒：联机版(2000004)", "mods"),
    "steam_mods_sub_path": os.path.join("common", "Don't Starve Together", "mods"),
    "search_drives": [f"{drive}:\\" for drive in string.ascii_uppercase if os.path.exists(f"{drive}:\\")],
    "common_program_paths": ["", "Program Files (x86)", "Program Files"]
}

# 定义要排除的系统文件夹和常见只读文件夹名称
DEFAULT_EXCLUDE_FOLDERS = [
    "Windows", "ProgramData", "PerfLogs", "Recovery", "System Volume Information",
    "$RECYCLE.BIN", "AppData", "Documents and Settings"
]

# 缓存机制，添加锁对象用于控制访问
cache = {}
cache_lock = threading.Lock()
is_searching = False  # 定义全局变量以标识是否正在查找
searching_lock = threading.Lock()

# 定义默认配置
default_config = {
    "common_program_paths": ["Program Files", "Program Files (x86)"],
    "exclude_folders": ["Windows", "ProgramData"],
    "steam_mods_path": "",
    "wegame_mods_path": ""
}
# 判断是否为要排除的文件夹
def should_exclude_folder(folder_name, exclude_folders):
    return any(exclude_folder in folder_name for exclude_folder in exclude_folders) or folder_name.startswith('.')


# 查找指定路径的函数，返回路径或None，添加锁控制is_searching访问
def find_path(drive, folder_name, depth=3):
    global is_searching
    with searching_lock:
        is_searching = True
    try:
        print(f"开始在 {drive} 盘查找 {folder_name} 文件夹...")
        update_search_status_label(f"正在 {drive} 盘查找 {folder_name} 文件夹...")

        user_config = load_config()
        exclude_folders = DEFAULT_EXCLUDE_FOLDERS + user_config.get("exclude_folders", [])

        for root, dirs, files in os.walk(drive):
            if root.count(os.sep) - drive.count(os.sep) >= depth:
                del dirs[:]
                continue

            dirs[:] = [d for d in dirs if not should_exclude_folder(d, exclude_folders)]
            target_path = os.path.join(root, folder_name)
            # 每隔5次目录检查更新一次状态标签，减少更新频率避免性能影响
            if root.count(os.sep) % 5 == 0:
                update_search_status_label(f"正在检查 {target_path} 是否存在...")
            if os.path.exists(target_path):
                logging.info(f"找到 {folder_name} 文件夹，路径为: {target_path}")
                return target_path
    finally:
        with searching_lock:
            is_searching = False
        update_search_status_label(f"未找到 {folder_name} 文件夹。")
    return None


# 打开文件夹的函数，完善异常处理
def open_folder(path, update_status_on_error=True):
    def open_folder_thread():
        try:
            if os.path.exists(path):
                os.startfile(path)
                logging.info(f"成功打开文件夹: {path}")
                update_search_status_label("已成功打开文件夹。可保存路径,下次点击直接打开文件夹。")
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setWindowTitle("错误")
                msg_box.setText(f"文件夹 {path} 未找到，请检查路径是否正确。")
                msg_box.exec_()
                if update_status_on_error:
                    update_search_status_label(f"未找到文件夹: {path}")
                logging.error(f"尝试打开文件夹 {path} 失败，文件夹不存在。", extra={"path": path})  # 记录更详细的日志信息
        except Exception as e:
            logging.error(f"打开文件夹 {path} 出现异常: {str(e)}", extra={"path": path})
            if update_status_on_error:
                update_search_status_label(f"打开文件夹 {path} 出现异常，请检查相关情况。")

    threading.Thread(target=open_folder_thread).start()


def find_apps_path(app_type):
    if f"{app_type}_apps" in cache:
        return cache[f"{app_type}_apps"]
    with cache_lock:
        drives = [drive for drive in PATH_CONFIG["search_drives"] if drive!= "C:\\"] + ["C:\\"]
        for drive in drives:
            priority_paths = [os.path.join(drive, sub_path, PATH_CONFIG[f"{app_type}_apps_folder"]) for sub_path in PATH_CONFIG["common_program_paths"]]
            for path in priority_paths:
                if os.path.exists(path):
                    logging.info(f"找到 {app_type} 文件夹，路径为: {path}")
                    cache[f"{app_type}_apps"] = path
                    return path
            found_path = find_path(drive, PATH_CONFIG[f"{app_type}_apps_folder"])
            if found_path:
                cache[f"{app_type}_apps"] = found_path
                return found_path
    message = f"未找到 {app_type} 文件夹，请确认 {app_type} 是否正确安装。"
    show_error_message(message)
    logging.error(message)
    return None


# 使用示例
def find_wegame_apps_path():
    return find_apps_path("wegame")


def find_steam_apps_path():
    return find_apps_path("steam")


# 提取查文件夹的通用函数
def find_mods_path(base_path, mods_sub_path, depth=3):
    if base_path:
        update_search_status_label(f"正在 {base_path} 下查找 mods 文件夹...")
        user_config = load_config()
        exclude_folders = DEFAULT_EXCLUDE_FOLDERS + user_config.get("exclude_folders", [])

        for root, dirs, files in os.walk(base_path):
            if root.count(os.sep) - base_path.count(os.sep) >= depth:
                del dirs[:]
                continue
            dirs[:] = [d for d in dirs if not should_exclude_folder(d, exclude_folders)]
            mods_path = os.path.join(root, mods_sub_path)
            update_search_status_label(f"正在检查 {mods_path} 是否存在...")
            if os.path.exists(mods_path):
                logging.info(f"找到 mods 文件夹，路径为: {mods_path}")
                return mods_path
    update_search_status_label(f"未找到 mods 文件夹。")
    return None


# 查找Steam版和WeGame版mods文件夹路径
def find_steam_mods_path(steam_apps_path):
    mods_path = find_mods_path(steam_apps_path, PATH_CONFIG["steam_mods_sub_path"])
    if mods_path:
        with cache_lock:
            cache["steam_mods"] = mods_path
    return mods_path


def find_wegame_mods_path(wegame_apps_path):
    mods_path = find_mods_path(wegame_apps_path, PATH_CONFIG["wegame_mods_sub_path"])
    if mods_path:
        with cache_lock:
            cache["wegame_mods"] = mods_path
    return mods_path


# 统一的错误提示函数
def show_error_message(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("错误")
    msg_box.setText(message)
    msg_box.exec_()
    logging.error(message)


# 获取快捷方式指向的真路径
def get_real_path(shortcut_path):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    return shortcut.Targetpath


# 更新提示文字的函数
def update_search_status_label(text):
    max_text_length = 80
    if len(text) > max_text_length:
        text = text[:max_text_length - 3] + "..."
    main_window.search_status_label.setText(text)
    QApplication.processEvents()


# 处理文件拖放事件的函数
def handle_drop(event):
    files = event.mimeData().urls()
    for file in files:
        file_path = file.toLocalFile()
        print(f"拖拽的文件: {file_path}")  # 调试信息，查看拖拽的文件列表
        if not file_path.endswith(".lnk"):
            # 如果拖拽的文件不是.lnk 文件，提醒用户
            QMessageBox.warning(main_window, "警告", "拖拽的文件不是有效的.lnk快捷方式，请检查文件。")
            continue  # 跳过后续处理

        target_path = get_real_path(file_path)
        print(f"处理的快捷方式: {target_path}")  # 调试信息，查看处理的快捷方式
        if "steam" in target_path.lower():
            steam_apps_path = find_steam_apps_path()
            steam_mods_path = find_steam_mods_path(steam_apps_path)
            open_folder(steam_mods_path, update_status_on_error=True)
        elif "wegame" in target_path.lower():
            wegame_apps_path = find_wegame_apps_path()
            wegame_mods_path = find_wegame_mods_path(wegame_apps_path)
            open_folder(wegame_mods_path, update_status_on_error=True)
        else:
            # 如果不是 Steam 或 WeGame 的快捷方式，提醒用户
            QMessageBox.warning(main_window, "警告", "拖拽的文件不是 Steam 或 WeGame 的快捷方式，请检查文件。")


# 读取用户配置
def load_config():
    config_path = '饥荒联机版Mods配置.json'
    print(f"尝试加载配置文件: {config_path}")

    if not os.path.exists(config_path):
        print("配置文件不存在，创建默认配置。")
        save_config(default_config)  # 使用全局的default_config
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                raise ValueError("配置文件为空")
            config = json.loads(content)
            for key in default_config.keys():
                if key not in config:
                    raise ValueError(f"缺少必要字段: {key}")

            print(f"加载的配置: {config}")
            return config
    except (json.JSONDecodeError, ValueError) as e:
        print(f"配置文件错误: {e}，恢复默认配置。")
        save_config(default_config)
        return default_config


# 保存用户配置
def save_config(config):
    with open('饥荒联机版Mods配置.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


# 检查配置文件并恢复默认配置
def check_and_restore_config():
    config_path = '饥荒联机版Mods配置.json'
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        restore_default_config()
    else:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError:
            restore_default_config()


def restore_default_config():
    default_config = {
        "common_program_paths": ["Program Files", "Program Files (x86)"],
        "exclude_folders": ["Windows", "ProgramData"],
        "steam_mods_path": "",
        "wegame_mods_path": ""
    }
    save_config(default_config)
    update_search_status_label("配置文件已恢复为默认设置。")


# 提取公共函数，用于检查并处理配置文件中指定类型mods路径有效性
def check_and_handle_mods_path_config(mods_type):
    user_config = load_config()
    mods_path_key = f"{mods_type.lower()}_mods_path"
    mods_path = user_config.get(mods_path_key, "").strip()
    if mods_path and os.path.exists(mods_path):
        return mods_path
    else:
        user_config[mods_path_key] = ""
        save_config(user_config)
        update_search_status_label(f"配置文件中的{mods_type}版mods文件夹路径无效，已清除。")
        return None
# 获取资源文件的绝对路径
def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        base_path = sys._MEIPASS  # PyInstaller创建的临时文件夹
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.user_config = load_config()
        # self.setStyleSheet("background-image:url(background.jpg);")
        self.exclude_folders = DEFAULT_EXCLUDE_FOLDERS + self.user_config.get("exclude_folders", [])
        self.init_ui()
        # 加载图片
        self.pixmap = QPixmap(resource_path("background.jpg"))
        # 获取窗口尺寸
        screen_geometry = QDesktopWidget().screenGeometry()
        window_width = screen_geometry.width()
        window_height = screen_geometry.height()
        # 缩放图片以适应窗口大小
        self.pixmap = self.pixmap.scaled(window_width, window_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(0, 0, 0))
        self.setPalette(palette)

    def paintEvent(self, event):
        painter = QPainter(self)
        # 设置透明度（这里设置为半透明，取值范围是0.0 - 1.0）
        painter.setOpacity(0.5)
        painter.drawPixmap(self.rect(), self.pixmap)

    def init_ui(self):
        self.setWindowTitle("饥荒联机版Mods文件夹查找器")

        # 获取屏幕宽度和高度
        screen_geometry = QDesktopWidget().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 设置窗口的宽度和高度
        window_width = 550
        window_height = 170

        # 计算窗口的x和y坐标
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # 设置窗口的位置
        self.setGeometry(x, y, window_width, window_height)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)

        label_layout = QHBoxLayout()
        self.message_label = QLabel("将Steam/Wegame的快捷方式拖放到此处，或点击下面按钮打开对应版本的 mods 文件夹", self)
        self.message_label.setStyleSheet("color: white")
        # self.message_label.setStyleSheet("color: gray; height: 3000px;")
        # self.message_label.setFixedHeight(30)
        self.message_label.setAlignment(Qt.AlignCenter)
        label_layout.addWidget(self.message_label)
        main_layout.addLayout(label_layout, 1)

        steam_button_layout = QHBoxLayout()

        self.steam_button = QPushButton("打开Steam版mods文件夹", self)
        self.steam_button.clicked.connect(self.open_steam_button_click)
        steam_button_layout.addWidget(self.steam_button, 5)

        self.save_steam_button = QPushButton("保存Steam路径", self)
        self.save_steam_button.clicked.connect(lambda: self.save_mods_path("Steam"))
        steam_button_layout.addWidget(self.save_steam_button, 1)

        main_layout.addLayout(steam_button_layout)

        wegame_button_layout = QHBoxLayout()

        self.wegame_button = QPushButton("打开Wegame版mods文件夹", self)
        self.wegame_button.clicked.connect(self.open_wegame_button_click)
        wegame_button_layout.addWidget(self.wegame_button, 5)

        self.save_wegame_button = QPushButton("保存Wegame路径", self)
        self.save_wegame_button.clicked.connect(lambda: self.save_mods_path("WeGame"))
        wegame_button_layout.addWidget(self.save_wegame_button, 1)

        main_layout.addLayout(wegame_button_layout)

        config_button_layout = QHBoxLayout()
        self.config_button = QPushButton("编辑配置文件", self)
        self.config_button.clicked.connect(self.open_config_editor)
        config_button_layout.addWidget(self.config_button, 5)

        self.clear_paths_button = QPushButton("清除所有保存路径", self)
        self.clear_paths_button.clicked.connect(self.clear_saved_paths)
        config_button_layout.addWidget(self.clear_paths_button, 1)

        main_layout.addLayout(config_button_layout)

        QLabel_layout = QHBoxLayout()
        self.search_status_label = QLabel("", self)
        self.search_status_label.setAlignment(Qt.AlignCenter)
        self.search_status_label.setStyleSheet("color: white")
        QLabel_layout.addWidget(self.search_status_label)
        main_layout.addLayout(QLabel_layout)
        # main_layout.addWidget(self.search_status_label)

        # 设置保存相关按钮的固定宽度
        self.save_wegame_button.setStyleSheet("width: 120px;")
        self.clear_paths_button.setStyleSheet("width: 120px;")
        self.save_steam_button.setStyleSheet("width: 120px;")

        # 设置打开和编辑相关按钮的固定宽度
        self.wegame_button.setStyleSheet("width: 150px;")
        self.config_button.setStyleSheet("width: 150px;")
        self.steam_button.setStyleSheet("width: 150px;")

        self.setLayout(main_layout)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        handle_drop(event)

    def open_steam_button_click(self):
        self.steam_button.setEnabled(False)  # 禁用按钮，防止短时间多次点击
        cache.clear()  # 清理缓存
        if is_searching:
            QMessageBox.information(self, "提示", "当前已有查找任务在进行，请稍后操作。")
            return
        update_search_status_label("开始查找Steam版mods文件夹，请稍候...")

        # 检查配置文件中的保存路径
        steam_mods_path = check_and_handle_mods_path_config("Steam")
        if steam_mods_path:
            open_folder(steam_mods_path, update_status_on_error=True)
            update_search_status_label("使用配置文件中的Steam版mods文件夹路径。")
        else:
            steam_apps_path = find_steam_apps_path()  # 查找Steam应用程序文件夹路径
            steam_mods_path = find_steam_mods_path(steam_apps_path)  # 查找mods文件夹路径
            if steam_mods_path:
                open_folder(steam_mods_path, update_status_on_error=True)
                update_search_status_label("查找完毕，可再次点击按钮直接打开文件夹或进行其他操作。")
            else:
                update_search_status_label("未找到Steam版mods文件夹。")
        # 500毫秒后重新启用按钮，可根据实际情况调整时间间隔
        threading.Timer(0.5, lambda: self.steam_button.setEnabled(True)).start()  

    def open_wegame_button_click(self):
        self.wegame_button.setEnabled(False)  # 禁用按钮，防止短时间多次点击
        cache.clear()  # 清理缓存
        if is_searching:
            QMessageBox.information(self, "提示", "当前已有查找任务在进行，请稍后操作。")
            return
        update_search_status_label("开始查找WeGame版mods文件夹，请稍候...")

        # 检查配置文件中的保存路径
        wegame_mods_path = check_and_handle_mods_path_config("WeGame")
        if wegame_mods_path:
            open_folder(wegame_mods_path, update_status_on_error=True)
            update_search_status_label("使用配置文件中的WeGame版mods文件夹路径。")
        else:
            wegame_apps_path = find_wegame_apps_path()  # 查找WeGame应用程序文件夹路径
            wegame_mods_path = find_wegame_mods_path(wegame_apps_path)  # 查找mods文件夹路径
            if wegame_mods_path:
                open_folder(wegame_mods_path, update_status_on_error=True)
                update_search_status_label("查找完毕，可再次点击按钮直接打开文件夹或进行其他操作。")
            else:
                update_search_status_label("未找到WeGame版mods文件夹。")
        # 500毫秒后重新启用按钮，可根据实际情况调整时间间隔
        threading.Timer(0.5, lambda: self.wegame_button.setEnabled(True)).start()  

    def save_mods_path(self, mods_type):
        user_config = load_config()
        mods_path = cache.get(f"{mods_type.lower()}_mods")  # 获取缓存中的完整mods路径
        if mods_path:
            with cache_lock:
                user_config[f"{mods_type.lower()}_mods_path"] = mods_path
            save_config(user_config)
            update_search_status_label(f"{mods_type}版mods文件夹路径已保存。")
        else:
            update_search_status_label(f"请先搜索{mods_type}版mods文件夹。")

    def clear_saved_paths(self):
        user_config = load_config()  # 加载当前配置文件

        # 仅清理steam_mods_path和wegame_mods_path
        user_config["steam_mods_path"] = ""
        user_config["wegame_mods_path"] = ""

        save_config(user_config)  # 保存更新后的配置文件
        update_search_status_label("已清理Steam和WeGame版mods文件夹路径。")  # 更新状态提示

        # 清理相关缓存
        with cache_lock:
            cache.pop("steam_mods", None)
            cache.pop("wegame_mods", None)

    def open_config_editor(self):
        config_window = QWidget()
        config_window.setWindowTitle("编辑配置")
        icon = QIcon("favicon.ico")
        config_window.setWindowIcon(icon)

        # 获取屏幕宽度和高度
        screen_geometry = QDesktopWidget().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 设置窗口的宽度和高度
        config_window_width = 650
        config_window_height = 170

        # 计算窗口的x和y坐标
        x = (screen_width // 2) - (config_window_width // 2)
        y = (screen_height // 2) - (config_window_height // 2)

        # 设置窗口的位置
        config_window.setGeometry(x, y, config_window_width, config_window_height)

        padding = 10
        config_window.setContentsMargins(padding, padding, padding, padding)

        layout = QVBoxLayout()

        # 加载最新配置
        self.user_config = load_config()

        common_layout = QHBoxLayout()

        common_paths_label = QLabel("常用文件夹（逗号分隔）:", config_window)
        common_layout.addWidget(common_paths_label)

        common_paths_entry = QLineEdit(', '.join(self.user_config["common_program_paths"]), config_window)
        common_layout.addWidget(common_paths_entry)

        layout.addLayout(common_layout)

        exclude_layout = QHBoxLayout()

        exclude_folders_label = QLabel("排除文件夹（逗号分隔）:", config_window)
        exclude_layout.addWidget(exclude_folders_label)
        exclude_folders_entry = QLineEdit(', '.join(self.user_config["exclude_folders"]), config_window)
        exclude_layout.addWidget(exclude_folders_entry)
        layout.addLayout(exclude_layout)

        steam_mods_layout = QHBoxLayout()
        steam_mods_label = QLabel("Steam版mods文件夹路径:", config_window)
        steam_mods_layout.addWidget(steam_mods_label)
        steam_mods_entry = QLineEdit(self.user_config["steam_mods_path"], config_window)
        steam_mods_layout.addWidget(steam_mods_entry)
        layout.addLayout(steam_mods_layout)

        wegame_mods_layout = QHBoxLayout()
        wegame_mods_label = QLabel("Wegame版mods文件夹路径:", config_window)
        wegame_mods_layout.addWidget(wegame_mods_label)
        wegame_mods_entry = QLineEdit(self.user_config["wegame_mods_path"], config_window)
        wegame_mods_layout.addWidget(wegame_mods_entry)
        layout.addLayout(wegame_mods_layout)

        common_paths_label.setMinimumSize(140, 0)
        exclude_folders_label.setMinimumSize(140, 0)
        steam_mods_label.setMinimumSize(140, 0)
        wegame_mods_label.setMinimumSize(140, 0)

        def save_config_changes():
            try:
                user_config = load_config()
                user_config["common_program_paths"] = [p.strip() for p in common_paths_entry.text().split(',')]
                user_config["exclude_folders"] = [f.strip() for f in exclude_folders_entry.text().split(',')]
                user_config["steam_mods_path"] = steam_mods_entry.text().strip()
                user_config["wegame_mods_path"] = wegame_mods_entry.text().strip()

                save_config(user_config)

                # 更新主窗口的配置相关属性
                self.user_config = user_config
                self.exclude_folders = DEFAULT_EXCLUDE_FOLDERS + self.user_config.get("exclude_folders", [])

                config_window.close()
            except Exception as e:
                QMessageBox.critical(config_window, "错误", f"保存配置时发生错误: {str(e)}")
                logging.error(f"保存配置时发生错误: {str(e)}")

        def open_config_file():
            os.startfile('饥荒联机版Mods配置.json')

        def restore_default_config():
            common_paths_entry.setText(', '.join(["Program Files", "Program Files (x86)"]))
            exclude_folders_entry.setText(', '.join(["Windows", "ProgramData"]))
            steam_mods_entry.setText("")
            wegame_mods_entry.setText("")

        button_layout = QHBoxLayout()

        restore_button = QPushButton("恢复默认配置", config_window)
        restore_button.clicked.connect(restore_default_config)
        button_layout.addWidget(restore_button)

        save_button = QPushButton("保存配置", config_window)
        save_button.clicked.connect(save_config_changes)
        button_layout.addWidget(save_button)

        open_button = QPushButton("打开配置文件(可手动编辑)", config_window)
        open_button.clicked.connect(open_config_file)
        button_layout.addWidget(open_button)

        layout.addLayout(button_layout)

        config_window.setLayout(layout)
        config_window.show()

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    icon = QIcon(resource_path("favicon.ico"))
    main_window.setWindowIcon(icon)
    main_window.show()
    app.exec_()
