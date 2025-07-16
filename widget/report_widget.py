import os

import requests
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QPushButton, QLineEdit, QLabel, QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMessageBox
from PyQt5 import QtWidgets



class report_widget(QTabWidget):
    def __init__(self, main_window=None):
        super(report_widget, self).__init__()
        self.file_path = None
        self.uploaded_once = False
        self.file_type = None  # 👈 新增：记录上传文件类型
        self.main_window = main_window

    def get_file_type(self, file_path):
        try:
            resp = requests.get("http://127.0.0.1:5000/get_file_type", params={"file_path": file_path})
            if resp.status_code == 200:
                return resp.json().get("type")
            return None
        except Exception as e:
            QMessageBox.critical(self.main_window, "类型识别失败", str(e))
            return None

    def generate_report(self):
        file_path = getattr(self.main_window, 'uploaded_file_path', None)
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self.main_window, "错误", "请先选择一个有效的文件路径")
            return

        file_name = os.path.basename(file_path)
        file_type = self.get_file_type(file_path)
        if not file_type:
            QMessageBox.warning(self.main_window, "错误", "无法识别该文件类型")
            return

        # ✅ 加入类型确认提示
        type_str = "通道数据" if file_type == "channel" else "频率数据" if file_type == "frequency" else "未知类型"
        reply = QMessageBox.question(
            self.main_window,
            "确认生成报告",
            f"当前选择的文件为：\n{file_name}\n文件类型：{type_str}\n\n是否确认生成报告？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        save_path = os.path.abspath("./static/shengcheng_reports")
        os.makedirs(save_path, exist_ok=True)

        endpoint = "generate_report" if file_type == "channel" else "generate_freq_report"
        try:
            payload = {"file_path": file_path, "save_path": save_path}
            response = requests.post(f"http://127.0.0.1:5000/{endpoint}", json=payload)
            if response.status_code == 200:
                file_path = response.json().get('file_path')
                QMessageBox.information(self.main_window, "成功", f"报告已生成：\n{file_path}")
                if os.path.exists(file_path):
                    os.startfile(file_path)
            else:
                QMessageBox.warning(self.main_window, "失败", response.text)
        except Exception as e:
            QMessageBox.critical(self.main_window, "异常", str(e))

    def generate_and_print_report(self):
        file_path = getattr(self.main_window, 'uploaded_file_path', None)
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self.main_window, "错误", "请先选择一个有效的文件路径")
            return

        file_name = os.path.basename(file_path)
        file_type = self.get_file_type(file_path)
        if not file_type:
            QMessageBox.warning(self.main_window, "错误", "无法识别该文件类型")
            return
        type_str = "通道数据" if file_type == "channel" else "频率数据" if file_type == "frequency" else "未知类型"
        # 弹窗确认打印
        reply = QMessageBox.question(
            self.main_window,
            "确认打印报告",
            f"当前选择的文件为：\n{file_name}\n文件类型：{type_str}\n\n是否确认生成并打印报告？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # 设置默认保存路径
        save_path = os.path.abspath("./static/dayin_reports")
        os.makedirs(save_path, exist_ok=True)

        # 选择后端接口
        endpoint = "generate_and_print_report" if file_type == "channel" else "generate_and_print_freq_report"
        payload = {
            "file_path": file_path,
            "save_path": save_path
        }

        try:
            resp = requests.post(f"http://127.0.0.1:5000/{endpoint}", json=payload)
            if resp.status_code == 200:
                QMessageBox.information(self.main_window, "成功", "报告已生成并发送到打印机")
            else:
                QMessageBox.warning(self.main_window, "失败", resp.text)
        except Exception as e:
            QMessageBox.critical(self.main_window, "打印失败", str(e))



