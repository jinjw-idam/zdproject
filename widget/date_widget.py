import os

import requests
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QPushButton, QLineEdit, QLabel, QTableView, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMessageBox
from PyQt5 import QtWidgets



class date_widget(QTabWidget):
    def __init__(self, main_window=None):
        super(date_widget, self).__init__()
        # 全局变量
        self.file_path = None
        self.main_window = main_window
        self.init_ui()
        self.tabCloseRequested.connect(self.close_datetab)
        # 加载完 UI 立刻查询并展示数据
        self.search_all()

    def init_ui(self):
        self.setParent(self.main_window.centralwidget)
        self.setGeometry(QtCore.QRect(530, 0, 1351, 601))
        self.setObjectName("dateWidget")
        self.setTabsClosable(True)
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.tableView = QtWidgets.QTableView(self.tab_7)
        self.tableView.setGeometry(QtCore.QRect(10, 10, 601, 481))
        self.tableView.setObjectName("tableView")
        self.tableView_2 = QtWidgets.QTableView(self.tab_7)
        self.tableView_2.setGeometry(QtCore.QRect(620, 10, 591, 481))
        self.tableView_2.setObjectName("tableView_2")
        self.addTab(self.tab_7, "databese")
        self.setCurrentIndex(0)


        # 配置表头自适应 能够点击表项响应全局变量
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 绑定功能
        # self.pushButton_2.clicked.connect(self.search_all)
        # self.pushButton.clicked.connect(self.search_by_condition)

    # 可以不写 为了测试用的
    def auto_fill_file_path(self):
        print("展示全局路径：", self.main_window.uploaded_file_path)
        if self.main_window and self.main_window.uploaded_file_path:
            self.file_path = self.main_window.uploaded_file_path

            if self.file_path.endswith('xlsx'):
                try:
                    pass
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"读取Excel失败：{e}")

    # 上传并保存
    def show_and_upload(self):
        # 保证 tab 被显示Q
        if self.tab_7.isHidden():
            self.tab_7.show()
        if self.indexOf(self.tab_7) == -1:
            self.addTab(self.tab_7, "database")
        self.setCurrentIndex(self.indexOf(self.tab_7))

        file_path = getattr(self.main_window, 'uploaded_file_path', None)
        print(file_path)

        # ✅ 无论是否有 file_path，都刷新表格
        if file_path and os.path.exists(file_path):
            # 上传文件
            try:
                r = requests.post("http://127.0.0.1:5000/upload_path", json={"file_path": file_path})
                if r.status_code != 200:
                    QMessageBox.warning(self, "上传失败", r.text)
            except Exception as e:
                QMessageBox.critical(self, "异常", f"上传出错：{e}")

        # ✅ 始终刷新表格（即使没上传）
        self.search_all()

    # 展示数据库
    def show_database(self):
        # 保证 tab 被显示Q
        if self.tab_7.isHidden():
            self.tab_7.show()
        if self.indexOf(self.tab_7) == -1:
            self.addTab(self.tab_7, "database")
        self.setCurrentIndex(self.indexOf(self.tab_7))

        self.search_all()

    # 查全
    def search_all(self):
        try:
            r = requests.get("http://127.0.0.1:5000/search_all")
            if r.status_code == 200:
                data = r.json().get('data', [])
                print(data)
                self.show_table(data)
            else:
                QMessageBox.warning(self, "查询失败", r.text)
        except Exception as e:
            QMessageBox.critical(self, "异常", str(e))

    # 绑定表项和全局路径
    def set_global_path(self, index):
        row = index.row()
        model = self.tableView.model()
        file_path_item = model.item(row, 5)  # 第5列是文件路径
        if file_path_item:
            file_path = file_path_item.text()
            if self.main_window:
                self.main_window.uploaded_file_path = file_path
                print(f"全局文件路径已更新为：\n{file_path}")


    # 条件查找
    def search_by_condition(self):
        params = {}
        id_text = self.lineEdit.text().strip()
        filename_text = self.lineEdit_2.text().strip()  # 实际是文件名输入框

        if id_text:
            params['id'] = id_text
        if filename_text:
            params['filename'] = filename_text

        if not params:
            QMessageBox.warning(self, "提示", "请至少输入ID或文件名作为查询条件")
            return

        try:
            response = requests.get("http://127.0.0.1:5000/search", params=params)
            if response.status_code == 200:
                data = response.json()['data']
                self.show_table(data)
            else:
                QMessageBox.warning(self, "查询失败", response.text)
        except Exception as e:
            QMessageBox.critical(self, "异常", str(e))

    def show_table(self, data):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['time', 'channel_1', 'channel_2', 'channel_3', '文件名', '文件路径'])

        for row in data:
            time_str = ", ".join(str(x) for x in row.get('time', []))
            ch1_str = ", ".join(str(x) for x in row.get('channel_1', []))
            ch2_str = ", ".join(str(x) for x in row.get('channel_2', []))
            ch3_str = ", ".join(str(x) for x in row.get('channel_3', []))
            filename = row.get('filename', '')
            file_path = row.get('file_path', '')

            row_items = [
                QStandardItem(time_str),
                QStandardItem(ch1_str),
                QStandardItem(ch2_str),
                QStandardItem(ch3_str),
                QStandardItem(filename),
                QStandardItem(file_path)
            ]
            model.appendRow(row_items)

        self.tableView.setModel(model)
        # 隐藏第 4 列（文件名）和第 5 列（文件路径）
        self.tableView.setColumnHidden(4, True)
        self.tableView.setColumnHidden(5, True)
        self.tableView.clicked.connect(self.set_global_path)

    # 响应关闭
    def close_datetab(self, index):
        self.removeTab(index)

