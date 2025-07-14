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
        self.main_window = main_window

    # 生成报告  保存路径自选
    def generate_report(self):
        file_path = getattr(self.main_window, 'uploaded_file_path', None)
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self.main_window, "错误", "请先选择一个有效的文件路径")
            return

        file_name = os.path.basename(file_path)
        reply = QMessageBox.question(
            self.main_window,
            "确认生成报告",
            f"当前选择的文件为：\n{file_name}\n是否确认生成报告？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            save_path = QFileDialog.getExistingDirectory(self.main_window, "选择报告保存路径")
            if not save_path:
                QMessageBox.information(self.main_window, "取消", "未选择保存目录")
                return

            try:
                payload = {
                    "file_path": file_path,
                    "save_path": save_path
                }
                response = requests.post("http://127.0.0.1:5000/generate_report", json=payload)
                if response.status_code == 200:
                    file_path = response.json().get('file_path')
                    QMessageBox.information(self.main_window, "成功", f"报告已生成：\n{file_path}")
                    # 生成完自动打开
                    if os.path.exists(file_path):
                        os.startfile(file_path)
                else:
                    QMessageBox.warning(self.main_window, "失败", response.text)
            except Exception as e:
                QMessageBox.critical(self.main_window, "异常", str(e))

    # 生成并打印报告 保存路径默认
    def generate_and_print_report(self):
        file_path = getattr(self.main_window, 'uploaded_file_path', None)

        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self.main_window, "错误", "请先选择一个有效的文件路径")
            return

        filename = os.path.basename(file_path)

        reply = QMessageBox.question(
            self.main_window,
            "确认打印报告",
            f"将打印报告文件：\n{filename}\n是否确认？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # 替换为你项目实际报告保存目录
                save_path = "/static/reports"

                resp = requests.post(
                    "http://127.0.0.1:5000/generate_and_print_report",
                    json={"file_path": file_path, "save_path": save_path}
                )
                if resp.status_code == 200:
                    QMessageBox.information(self.main_window, "成功", "报告已发送到打印机")
                else:
                    QMessageBox.warning(self.main_window, "失败", resp.text)
            except Exception as e:
                QMessageBox.critical(self.main_window, "打印失败", str(e))

