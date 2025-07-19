import os

from PyQt5.QtWidgets import QTabWidget, QMessageBox
from PyQt5 import QtCore, QtWidgets

from utils.display_utils import tcp_display_widget
from utils.show_utils import create_show_widget, draw_shishishow


class displayWidget(QTabWidget):
    def __init__(self, main_window=None):
        super(displayWidget, self).__init__()
        self.file_path = None
        self.main_window = main_window
        self.init_ui()
        self.tcp_show()
        self.tabCloseRequested.connect(self.close_displaytab)

    def shishi_show(self):
        self.auto_fill_file_path()
        if self.file_path is None:
            return
        name = os.path.splitext(os.path.basename(self.file_path))[0] + '_' + 'show'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = create_show_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
            draw_shishishow(self.file_path, new_tab)
        self.setCurrentIndex(tab_index)

    def tcp_show(self):
        name = 'TCP_show'
        tab_index = -1
        for index in range(self.count()):
            if self.tabText(index) == name:
                tab_index = index
        if tab_index == -1:
            new_tab = tcp_display_widget()  # 创建空白页面（可替换为你的自定义控件）
            tab_index = self.addTab(new_tab, name)
        self.setCurrentIndex(tab_index)

    def auto_fill_file_path(self):
        print("展示全局路径：", self.main_window.uploaded_file_path)
        if self.main_window and self.main_window.uploaded_file_path:
            self.file_path = self.main_window.uploaded_file_path
            if self.file_path.endswith('xlsx'):
                try:
                    pass
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"读取Excel失败：{e}")

    def close_displaytab(self, index):
        self.removeTab(index)

    def init_ui(self):
        self.setParent(self.main_window.centralwidget)
        self.setTabsClosable(True)
        self.setGeometry(QtCore.QRect(540, 550, 1341, 491))
        self.setObjectName("displayWidget")
