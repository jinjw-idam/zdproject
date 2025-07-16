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
        self.setGeometry(QtCore.QRect(530, 0, 1351, 531))
        self.setObjectName("dateWidget")
        self.setTabsClosable(True)

        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.tableView = QtWidgets.QTableView(self.tab_7)
        # 不用 setGeometry 了，改用布局管理
        layout7 = QVBoxLayout(self.tab_7)
        layout7.setContentsMargins(0, 0, 0, 0)
        layout7.addWidget(self.tableView)
        self.addTab(self.tab_7, "通道数据")

        self.tab_8 = QtWidgets.QWidget()
        self.tab_8.setObjectName("tab_8")
        self.tableView_2 = QtWidgets.QTableView(self.tab_8)
        layout8 = QVBoxLayout(self.tab_8)
        layout8.setContentsMargins(0, 0, 0, 0)
        layout8.addWidget(self.tableView_2)
        self.addTab(self.tab_8, "频率数据")

        self.setCurrentIndex(0)

        # 配置表头自适应
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)




        # self.setParent(self.main_window.centralwidget)
        # self.setGeometry(QtCore.QRect(530, 0, 1351, 531))
        #
        # self.tab_7 = QtWidgets.QWidget()
        # self.tab_7.setObjectName("tab_7")
        # self.tableView = QtWidgets.QTableView(self.tab_7)
        # self.tableView.setGeometry(QtCore.QRect(10, 10, 1201, 520))
        # self.tableView.setObjectName("tableView")
        # self.addTab(self.tab_7, "通道数据")
        #
        # self.tab_8 = QtWidgets.QWidget()
        # self.tab_8.setObjectName("tab_8")
        # self.tableView_2 = QtWidgets.QTableView(self.tab_8)
        # self.tableView_2.setGeometry(QtCore.QRect(10, 10, 1201, 520))
        # self.tableView_2.setObjectName("tableView_2")
        # self.addTab(self.tab_8, "频率数据")
        #
        #
        # self.setCurrentIndex(0)
        #
        #
        # # 配置表头自适应 能够点击表项响应全局变量
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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

    # 上传并保存（支持通道数据和频率数据自动识别）
    def show_and_upload(self):
        file_path = getattr(self.main_window, 'uploaded_file_path', None)
        print(f"上传文件路径: {file_path}")

        if file_path and os.path.exists(file_path):
            try:
                # 自动判断文件类型，预读取前几行
                import pandas as pd
                if file_path.endswith(".xlsx"):
                    df = pd.read_excel(file_path)
                elif file_path.endswith(".csv") or file_path.endswith(".txt"):
                    df = pd.read_csv(file_path, delimiter=None if file_path.endswith(".csv") else '\t')
                else:
                    QMessageBox.warning(self, "错误", "暂不支持的文件格式")
                    return

                # 根据列名决定上传接口
                if {"channel_1", "channel_2", "channel_3"}.issubset(df.columns):
                    upload_url = "http://127.0.0.1:5000/upload_path"
                    target_tab = self.tab_7
                elif {"frequency", "magnitude", "phase"}.issubset(df.columns):
                    upload_url = "http://127.0.0.1:5000/upload_freq_path"
                    target_tab = self.tab_8
                else:
                    QMessageBox.warning(self, "错误", "文件内容不符合要求，缺少必要列")
                    return

                # 上传文件
                r = requests.post(upload_url, json={"file_path": file_path})
                if r.status_code != 200:
                    QMessageBox.warning(self, "上传失败", r.text)
                    return

                # 自动切换到对应 tab
                self.setCurrentWidget(target_tab)

            except Exception as e:
                QMessageBox.critical(self, "异常", f"上传出错：{e}")

        else:
            QMessageBox.warning(self, "无效路径", "未检测到文件路径或文件不存在")

        # ✅ 无论是否上传成功，始终刷新所有数据
        self.search_all()

    # 展示数据库
    def show_database(self):
        # tab_7 恢复显示
        if self.indexOf(self.tab_7) == -1:
            self.addTab(self.tab_7, "通道数据")
        self.tab_7.show()

        # tab_8 恢复显示
        if self.indexOf(self.tab_8) == -1:
            self.addTab(self.tab_8, "频率数据")
        self.tab_8.show()

        # 默认跳转到 tab_7
        self.setCurrentWidget(self.tab_7)

        # 刷新所有数据
        self.search_all()

    # 查全
    def search_all(self):
        try:
            # 通道数据
            r1 = requests.get("http://127.0.0.1:5000/search_all")
            if r1.status_code == 200:
                data1 = r1.json().get('data', [])
                print("data1",data1)
                self.show_table(data1, is_frequency=False)

            # 频率数据
            r2 = requests.get("http://127.0.0.1:5000/search_all_freq")
            if r2.status_code == 200:
                data2 = r2.json().get('data', [])
                print("data2", data2)
                self.show_table(data2, is_frequency=True)

        except Exception as e:
            QMessageBox.critical(self, "异常", str(e))

    # 绑定表项和全局路径
    def set_global_path(self, index):
        row = index.row()
        model = self.tableView.model()
        file_path_item = model.item(row, 4)  # 第5列是文件路径
        if file_path_item:
            file_path = file_path_item.text()
            if self.main_window:
                self.main_window.uploaded_file_path = file_path
                print(f"全局文件路径已更新为：\n{file_path}")

    def set_global_path_from_table2(self, index):
        row = index.row()
        model = self.tableView_2.model()
        file_path_item = model.item(row, 3)  # 文件路径在第 3 列
        if file_path_item:
            file_path = file_path_item.text()
            if self.main_window:
                self.main_window.uploaded_file_path = file_path
                print(f"全局文件路径已更新为：\n{file_path}")


    def show_table(self, data, is_frequency=False):
        model = QStandardItemModel()

        if is_frequency:
            model.setHorizontalHeaderLabels(['frequency', 'magnitude', 'phase', '文件路径'])

            for row in data:
                f_str = ", ".join(str(x) for x in row.get('frequency', []))
                m_str = ", ".join(str(x) for x in row.get('magnitude', []))
                p_str = ", ".join(str(x) for x in row.get('phase', []))
                file_path = row.get('file_path', '')

                row_items = [
                    QStandardItem(f_str),
                    QStandardItem(m_str),
                    QStandardItem(p_str),
                    QStandardItem(file_path)
                ]
                model.appendRow(row_items)

            self.tableView_2.setModel(model)
            self.tableView_2.setColumnHidden(3, True)
            self.tableView_2.clicked.connect(self.set_global_path_from_table2)

        else:
            model.setHorizontalHeaderLabels(['time', 'channel_1', 'channel_2', 'channel_3', '文件路径'])

            for row in data:
                time_str = ", ".join(str(x) for x in row.get('time', []))
                ch1_str = ", ".join(str(x) for x in row.get('channel_1', []))
                ch2_str = ", ".join(str(x) for x in row.get('channel_2', []))
                ch3_str = ", ".join(str(x) for x in row.get('channel_3', []))
                file_path = row.get('file_path', '')

                row_items = [
                    QStandardItem(time_str),
                    QStandardItem(ch1_str),
                    QStandardItem(ch2_str),
                    QStandardItem(ch3_str),
                    QStandardItem(file_path)
                ]
                model.appendRow(row_items)

            self.tableView.setModel(model)
            self.tableView.setColumnHidden(4, True)
            self.tableView.clicked.connect(self.set_global_path)

    # 响应关闭
    def close_datetab(self, index):
        self.removeTab(index)

