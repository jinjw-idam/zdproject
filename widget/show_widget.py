import os

import mplcursors
import numpy as np
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMessageBox, QInputDialog, QDialog, QLabel, QComboBox, \
    QPushButton
from PyQt5 import QtCore, QtWidgets
from matplotlib import cm

from utils.file_utils import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector

from utils.show_utils import *


class showWidget(QTabWidget):
    def __init__(self, main_window=None):
        super(showWidget, self).__init__()
        self.file_path = None
        self.main_window = main_window
        self.time_list = None
        self.amplitude_list = None
        self.init_ui()
        self.tabCloseRequested.connect(self.close_showtab)

    ##############################XY图#############################################
    def draw_XY_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_XY'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget(need_label=True)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_XY(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def draw_Frontback_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        channel_name1, channel_name2 = self.choose_two_channels()
        if channel_name1 is None or channel_name2 is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name1 + '_' + channel_name2 + '_frontback'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget(need_label=False)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_Frontback(self.file_path, new_tab, base_name, channel_name1, channel_name2)
            self.setCurrentIndex(tab_index)

    def draw_waterfall_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_waterfall'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget(need_label=False)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_waterfall(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def draw_Bode_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('xlsx'):
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_Bode'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_Bode(self.file_path, new_tab, base_name)
            self.setCurrentIndex(tab_index)

    def draw_UL_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_UL'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_UL(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def draw_Nyquist_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('xlsx'):
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_Nyquist'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_Nyquist(self.file_path, new_tab, base_name)
            self.setCurrentIndex(tab_index)

    def draw_third_octave_spectrum_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_third_octave_spectrum'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_third_octave_spectrum(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def draw_one_octave_spectrum_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_one_octave_spectrum'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_one_octave_spectrum(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def draw_colormap_img(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        name = base_name + '_' + channel_name + '_colormap'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_colormap(self.file_path, new_tab, base_name, channel_name)
            self.setCurrentIndex(tab_index)

    def shishi_show(self):
        self.auto_fill_file_path()
        if self.file_path is None or not self.file_path.endswith('csv'):
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_' + 'show'
        new_tab = create_show_widget(need_button=False)  # 创建空白页面（可替换为你的自定义控件）
        tab_index = self.addTab(new_tab, name)
        draw_shishishow(self.file_path, new_tab)
        self.setCurrentIndex(tab_index)

    #####################################################################################
    def auto_fill_file_path(self):
        print("展示全局路径：", self.main_window.uploaded_file_path)
        if self.main_window and self.main_window.uploaded_file_path:
            self.file_path = self.main_window.uploaded_file_path

            if self.file_path.endswith('xlsx'):
                try:
                    pass
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"读取Excel失败：{e}")

    def choose_channel(self):
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

    def choose_two_channels(self):
        _, _, channel_names = get_csv_info(self.file_path)

        while True:  # 循环直到选择有效或取消
            # 创建对话框
            dialog = QDialog()
            dialog.setWindowTitle("选择两个通道")
            dialog.setMinimumWidth(300)

            # 布局和控件
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

            # 按钮组
            btn_ok = QPushButton("确定")
            btn_ok.clicked.connect(dialog.accept)
            layout.addWidget(btn_ok)

            dialog.setLayout(layout)

            dialog.setLayout(layout)

            # 处理选择结果
            if dialog.exec_() == QDialog.Accepted:
                channel_name1 = combo1.currentText()
                channel_name2 = combo2.currentText()

                if channel_name1 == channel_name2:
                    QMessageBox.warning(self, "无效选择",
                                        "请选择两个不同的通道！\n"
                                        f"当前选择: {channel_name1} 和 {channel_name2}")
                    continue  # 重新循环显示对话框
                else:
                    return channel_name1, channel_name2
            else:
                return None, None  # 用户取消

    def close_showtab(self, index):
        self.removeTab(index)

    def init_ui(self):
        self.setParent(self.main_window.centralwidget)
        self.setGeometry(QtCore.QRect(0, 0, 521, 531))
        self.setTabsClosable(True)
        self.setObjectName("showWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.addTab(self.tab, "default")
        self.setCurrentIndex(0)
