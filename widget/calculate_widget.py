import os

import mplcursors
import numpy as np
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMessageBox, QInputDialog, QDialog, QLabel, QComboBox
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector

from utils.calculate_utils import *


class calculateWidget(QTabWidget):
    def __init__(self, main_window=None):
        super(calculateWidget, self).__init__()
        self.file_path = None
        self.main_window = main_window
        self.init_ui()
        self.tabCloseRequested.connect(self.close_calculatetab)

    def generate_fft(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_fft'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = self.create_fft_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            self.draw_fft(new_tab)
            self.setCurrentIndex(tab_index)

    def selfcomposed(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        channel_name = self.choose_one_channel()
        if channel_name is None:
            return
        base_name=os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_selfcomposed'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_calculate_widget(need_button=True)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            calculate_selfcomposed(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def cepstrum(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        channel_name = self.choose_one_channel()
        if channel_name is None:
            return
        base_name=os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_cepstrum'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_calculate_widget(need_button=True)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            calculate_cepstrum(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def math_calculate(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        channel_name = self.choose_one_channel()
        if channel_name is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_' + channel_name + '_mathcalculate'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_calculate_widget(need_button=False,need_label=True)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            calculate_all(self.file_path, new_tab, channel_name)
            self.setCurrentIndex(tab_index)

    def weight_calculate(self,type):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        channel_name = self.choose_one_channel()
        if channel_name is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + f'_{type}weightcalculate'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_calculate_widget(need_button=True, need_label=False)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            calculate_weight(self.file_path, new_tab, base_name, channel_name, type)
            self.setCurrentIndex(tab_index)

    def create_fft_widget(self):
        new_tab = QWidget()  # 创建空白页面（可替换为你的自定义控件）
        new_tab.figure = Figure()
        new_tab.canvas = FigureCanvas(new_tab.figure)
        new_tab.layout = QVBoxLayout(new_tab)  # 直接设置布局到 QWidget
        new_tab.layout.addWidget(new_tab.canvas)  # 添加 Matplotlib 画布
        new_tab.figure.clear()
        return new_tab

    def draw_fft(self, widget: QWidget):
        xf, amplitude_spectrum = fft_analysis(self.main_window.uploaded_file_path)
        ax = widget.figure.add_subplot(111)
        line = ax.plot(xf, amplitude_spectrum)
        ax.set_title("FFT分析图")
        ax.set_xlabel("频率")
        ax.set_ylabel("幅度")
        widget.cursor = mplcursors.cursor(line, hover=True)
        widget.cursor.connect(
            "add", lambda sel: sel.annotation.set_text(
                f"Frequency: {sel.target[0]:.2f}\nAmplitude: {sel.target[1]:.2f}"
            )
        )
        widget.canvas.draw()

    def choose_one_channel(self):
        _, _, channel_names = get_csv_info(self.file_path)
        items = channel_names
        selected, ok = QInputDialog.getItem(
            None,  # 父窗口（None表示无父窗口）
            "选择通道",  # 标题
            "请选择一个通道:",  # 提示文本
            items,  # 选项列表
            0,  # 默认选中索引
            False  # 是否可编辑
        )
        if ok and selected:
            return selected
        else:
            return None

    def choose_channel_sincos(self):
        _, _, channel_names = get_csv_info(self.file_path)

        # 创建自定义对话框
        dialog = QDialog()
        dialog.setWindowTitle("选择两个通道")

        # 创建布局和控件
        layout = QVBoxLayout()

        # 第一个下拉框
        layout.addWidget(QLabel("选择第一个通道:"))
        combo1 = QComboBox()
        combo1.addItems(channel_names)
        layout.addWidget(combo1)

        # 第二个下拉框
        layout.addWidget(QLabel("选择第二个通道:"))
        combo2 = QComboBox()
        combo2.addItems(channel_names)
        layout.addWidget(combo2)

        # 确认按钮
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(dialog.accept)
        layout.addWidget(btn_ok)

        dialog.setLayout(layout)

        # 显示对话框并获取结果
        if dialog.exec_() == QDialog.Accepted:
            channel1 = combo1.currentText()
            channel2 = combo2.currentText()
            return channel1, channel2
        return None, None  # 用户取消

    def close_calculatetab(self, index):
        self.removeTab(index)

    def auto_fill_file_path(self):
        print("展示全局路径：", self.main_window.uploaded_file_path)
        if self.main_window and self.main_window.uploaded_file_path:
            self.file_path = self.main_window.uploaded_file_path

            if self.file_path.endswith('xlsx'):
                try:
                    pass
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"读取Excel失败：{e}")

    def init_ui(self):
        self.setParent(self.main_window.centralwidget)
        self.setGeometry(QtCore.QRect(0, 530, 521, 531))
        self.setTabsClosable(True)
        self.setObjectName("calculateWidget")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.addTab(self.tab_3, "default")
        self.setCurrentIndex(0)
