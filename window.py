import sys

import pandas as pd
import requests
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox

from widget.date_widget import date_widget
from widget.report_widget import report_widget
from widget.show_widget import showWidget
from widget.calculate_widget import calculateWidget
from ui import Ui_MainWindow
from utils.file_utils import *
from utils.calculate_utils import *
from utils.show_utils import *



class main_window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(main_window, self).__init__()
        self.uploaded_file_path = None  # 全局共享的上传文件路径
        self.setupUi(self)
        self.showWidget = showWidget(self)
        self.calculateWidget = calculateWidget(self)
        self.dateWidget = date_widget(self)
        self.reportWidget = report_widget(self)
        # 记住全局路径
        self.actionopen.triggered.connect(self.open_file)
        # 打开文件的时候 保存放在数据库里
        # self.actionopen.triggered.connect(self.dateWidget.show_and_upload)
        # 画XY图
        self.actionXY.triggered.connect(self.showWidget.draw_XY_img)
        # 画瀑布图
        self.actionwaterfall.triggered.connect(self.showWidget.draw_waterfall_img)
        # 画Bode图
        self.actionBode.triggered.connect(self.showWidget.draw_Bode_img)
        # 画Frontback图
        self.actionFrontback.triggered.connect(self.showWidget.draw_Frontback_img)
        # 画Nyquist图
        self.actionNyquist.triggered.connect(self.showWidget.draw_Nyquist_img)
        # 画1/3倍频程图
        self.action1_3.triggered.connect(self.showWidget.draw_third_octave_spectrum_img)
        # 画单倍频程图
        self.action1_1.triggered.connect(self.showWidget.draw_one_octave_spectrum_img)
        # fft分析
        self.actionfft.triggered.connect(self.calculateWidget.generate_fft)


    def open_file(self):
        uploaded_file_path = QFileDialog.getOpenFileName(None, 'Select File')[0]
        self.uploaded_file_path = uploaded_file_path
        # self.showWidget.shishi_show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = main_window()
    MainWindow.show()
    sys.exit(app.exec_())
