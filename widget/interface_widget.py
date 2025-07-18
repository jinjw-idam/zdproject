import os
import time
import threading
import pandas as pd
import requests

from PyQt5.QtWidgets import (
    QTabWidget, QFileDialog, QMessageBox
)
from PyQt5.QtCore import pyqtSignal


class interface_widget(QTabWidget):
    show_message_signal = pyqtSignal(str, str)     # 用于提示信息
    ask_upload_signal = pyqtSignal(list)           # 用于上传确认

    def __init__(self, main_window=None):
        super(interface_widget, self).__init__()
        self.file_path = None
        self.main_window = main_window
        self.saved_files = []  # 保存的文件名
        self.listening = False
        self.listen_start_time = None

        # 连接信号到槽函数
        self.show_message_signal.connect(self._show_message_box)
        self.ask_upload_signal.connect(self._ask_upload)

    def listen(self):
        if self.listening:
            QMessageBox.information(self, "提示", "监听已经在进行中")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模拟发送的 Excel 文件", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        self.listening = True
        self.saved_files.clear()

        threading.Thread(target=self.send_data_and_monitor, args=(file_path,), daemon=True).start()

    def send_data_and_monitor(self, file_path):
        self.send_data_from_excel(file_path)

        time.sleep(10)  # 等待模拟监听结束

        # 触发后端缓存保存
        try:
            resp = requests.get("http://127.0.0.1:5000/save_cache_to_file")
            print("触发缓存保存，返回:", resp.status_code)
        except Exception as e:
            print("手动保存异常:", e)

        self.listening = False  # 监听结束

        # 请求后端保存的文件列表
        try:
            resp = requests.get("http://127.0.0.1:5000/save_file")
            if resp.status_code == 200:
                data = resp.json()
                self.saved_files = data.get('files', [])
            else:
                self.saved_files = []
        except Exception as e:
            print("获取保存文件列表异常:", e)
            self.saved_files = []

        if not self.saved_files:
            self.show_message_signal.emit("提示", "监听结束，但未检测到保存的文件。")
            return

        # 触发上传确认对话框
        self.ask_upload_signal.emit(self.saved_files)

    def send_data_from_excel(self, file_path, interval=0.01):
        df = pd.read_excel(file_path, header=None)
        url = "http://127.0.0.1:5000/receive_data"
        for idx, row in df.iterrows():
            if not self.listening:
                break
            row_len = len(row.dropna())
            if row_len == 4:
                data = {
                    "time": float(row[0]),
                    "channel_1": float(row[1]),
                    "channel_2": float(row[2]),
                    "channel_3": float(row[3]),
                }
            elif row_len == 3:
                data = {
                    "frequency": float(row[0]),
                    "magnitude": float(row[1]),
                    "phase": float(row[2]),
                }
            else:
                continue
            try:
                requests.post(url, json=data)
            except Exception as e:
                print(f"发送异常，第{idx}行: {e}")
            time.sleep(interval)

    def upload_files(self):
        for file_name in self.saved_files:
            file_path = os.path.join("cached_data", file_name)
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "文件不存在", f"{file_path} 不存在，跳过上传")
                continue

            if file_name.startswith("channel"):
                url = "http://127.0.0.1:5000/upload_path"
            elif file_name.startswith("frequency"):
                url = "http://127.0.0.1:5000/upload_freq_path"
            else:
                QMessageBox.warning(self, "未知文件类型", f"文件 {file_name} 类型未知，跳过")
                continue

            try:
                res = requests.post(url, json={"file_path": file_path})
                if res.status_code == 200:
                    QMessageBox.information(self, "上传成功", f"{file_name} 上传成功")
                else:
                    QMessageBox.warning(self, "上传失败", f"{file_name} 上传失败: {res.text}")
            except Exception as e:
                QMessageBox.warning(self, "上传异常", f"{file_name} 上传异常: {e}")

    def _show_message_box(self, title, content):
        QMessageBox.information(self, title, content)

    def _ask_upload(self, file_list):
        files_str = "\n".join(file_list)
        reply = QMessageBox.question(self, "监听结束",
                                     f"监听结束，保存了以下文件：\n{files_str}\n是否上传？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.upload_files()
