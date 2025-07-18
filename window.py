import sys

import pandas as pd
import requests
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox

from widget.date_widget import date_widget
from widget.display_widget import displayWidget
from widget.interface_widget import interface_widget
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
        self.displayWidget = displayWidget(self)
        self.calculateWidget = calculateWidget(self)
        self.dateWidget = date_widget(self)
        self.reportWidget = report_widget(self)
        self.interfaceWidget = interface_widget(self)

        # 记住全局路径
        self.actionopen.triggered.connect(self.open_file)
        # 打开文件的时候 保存放在数据库里
        self.actionopen.triggered.connect(self.dateWidget.show_and_upload)
        # 画XY图
        self.actionXY.triggered.connect(self.showWidget.draw_XY_img)
        # 画瀑布图
        self.actionwaterfall.triggered.connect(self.showWidget.draw_waterfall_img)
        # 画Bode图
        self.actionBode.triggered.connect(self.showWidget.draw_Bode_img)
        # 画Frontback图
        self.actionFrontback.triggered.connect(self.showWidget.draw_Frontback_img)
        # 画UL图
        self.actionUL.triggered.connect(self.showWidget.draw_UL_img)
        # 画Nyquist图
        self.actionNyquist.triggered.connect(self.showWidget.draw_Nyquist_img)
        # 画1/3倍频程图
        self.action1_3.triggered.connect(self.showWidget.draw_third_octave_spectrum_img)
        # 画单倍频程图
        self.action1_1.triggered.connect(self.showWidget.draw_one_octave_spectrum_img)
        # 画colormap图
        self.actionColormap.triggered.connect(self.showWidget.draw_colormap_img)
        # fft计算
        self.actionfft.triggered.connect(self.calculateWidget.fft_calculate)
        # 自谱计算
        self.actionself_composed.triggered.connect(self.calculateWidget.selfcomposed)
        # 倒谱计算
        self.actioncepstrum.triggered.connect(self.calculateWidget.cepstrum)
        # 数学计算
        self.actioncalculate_all.triggered.connect(self.calculateWidget.math_calculate)
        # 三角函数运算
        self.actionsincos_2.triggered.connect(self.calculateWidget.trig_calculate)
        # 计权运算
        self.actionA_weight.triggered.connect(lambda: self.calculateWidget.weight_calculate('A'))
        self.actionB_weight.triggered.connect(lambda: self.calculateWidget.weight_calculate('B'))
        self.actionC_weight.triggered.connect(lambda: self.calculateWidget.weight_calculate('C'))
        # 展示数据库
        self.actionshujuku.triggered.connect(self.dateWidget.show_database)
        # 生成报告
        self.actionsehngc.triggered.connect(self.reportWidget.generate_report)
        # 绑定打印菜单
        self.actiondayin.triggered.connect(self.reportWidget.generate_and_print_report)
        # 监听
        self.actionjianting.triggered.connect(self.interfaceWidget.listen)

    def open_file(self):
        uploaded_file_path = QFileDialog.getOpenFileName(None, 'Select File')[0]
        self.uploaded_file_path = uploaded_file_path

        file_path = self.uploaded_file_path
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
                    self.displayWidget.shishi_show()
                else:
                    print("该文件为频率数据，不展示实时图")
            except Exception as e:
                print(f"文件读取失败: {e}")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = main_window()
    MainWindow.show()
    sys.exit(app.exec_())
