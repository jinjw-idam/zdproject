import os

import mplcursors
import numpy as np
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QMessageBox, QInputDialog
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
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_XY'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget(need_label=True)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_XY(self.file_path, new_tab, select=True)
            self.setCurrentIndex(tab_index)

    def draw_Frontback_img(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_XY'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget(need_label=False)  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_Frontback(self.file_path, new_tab)
            self.setCurrentIndex(tab_index)

    def draw_waterfall_img(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_waterfall'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_waterfall(self.file_path, new_tab)
            self.setCurrentIndex(tab_index)

    def draw_Bode_img(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_Bode'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_Bode(self.file_path, new_tab)
            self.setCurrentIndex(tab_index)

    def draw_Nyquist_img(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_Nyquist'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_Nyquist(self.file_path, new_tab)
            self.setCurrentIndex(tab_index)

    def draw_third_octave_spectrum_img(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_' + channel_name + '_third_octave_spectrum'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_third_octave_spectrum(self.file_path, new_tab,channel_name)
            self.setCurrentIndex(tab_index)

    def draw_one_octave_spectrum_img(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        channel_name = self.choose_channel()
        if channel_name is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_' + channel_name + '_one_octave_spectrum'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_one_octave_spectrum(self.file_path, new_tab,channel_name)
            self.setCurrentIndex(tab_index)

    def shishi_show(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_' + 'show'
        new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
        tab_index = self.addTab(new_tab, name)
        draw_shishishow(self.file_path,new_tab)
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
