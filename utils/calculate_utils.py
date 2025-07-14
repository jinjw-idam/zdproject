import os

import matplotlib
from PyQt5 import QtWidgets, QtCore
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from scipy.fft import fft, fftfreq

from utils.file_utils import *

matplotlib.rc("font", family='Microsoft YaHei')
import mplcursors


def fft_analysis(file_path):
    time_list, amplitude_list = get_info(file_path)
    np_time_list = np.array(time_list)
    np_amplitude_list = np.array(amplitude_list)
    N = len(np_time_list)  # 采样点数
    T = np_time_list[1] - np_time_list[0]  # 采样间隔(秒)
    Fs = 1 / T  # 采样频率(Hz)

    yf = fft(np_amplitude_list)  # 复数形式的频谱
    xf = fftfreq(N, T)[:N // 2]  # 正频率部分
    amplitude_spectrum = 2 / N * np.abs(yf[0:N // 2])
    return xf, amplitude_spectrum

# def generate_fft(tab_widget, file_path, time_list, amplitude_list):
#     if time_list is None or amplitude_list is None:
#         return
#     name = os.path.splitext(os.path.basename(file_path))[0] + '_fft'
#     tab_index = -1
#     for index in range(tab_widget.count()):
#         if tab_widget.tabText(index) == name:
#             tab_index = index
#     if tab_index == -1:
#         new_tab = create_fft_widget(time_list, amplitude_list)  # 创建空白页面（可替换为你的自定义控件）
#         tab_index = tab_widget.addTab(new_tab, name)
#         draw_fft(new_tab)
#     return tab_index
#
#
# def create_fft_widget(time_list, amplitude_list):
#     new_tab = QWidget()  # 创建空白页面（可替换为你的自定义控件）
#     new_tab.time_list = time_list
#     new_tab.amplitude_list = amplitude_list
#     new_tab.figure = Figure()
#     new_tab.canvas = FigureCanvas(new_tab.figure)
#     new_tab.layout = QVBoxLayout(new_tab)  # 直接设置布局到 QWidget
#     new_tab.layout.addWidget(new_tab.canvas)  # 添加 Matplotlib 画布
#     new_tab.figure.clear()
#     return new_tab
#
#
# def draw_fft(widget: QWidget):
#     np_time_list = np.array(widget.time_list)
#     np_amplitude_list = np.array(widget.amplitude_list)
#     N = len(np_time_list)  # 采样点数
#     T = np_time_list[1] - np_time_list[0]  # 采样间隔(秒)
#     Fs = 1 / T  # 采样频率(Hz)
#
#     yf = fft(np_amplitude_list)  # 复数形式的频谱
#     xf = fftfreq(N, T)[:N // 2]  # 正频率部分
#     amplitude_spectrum = 2 / N * np.abs(yf[0:N // 2])
#     ax = widget.figure.add_subplot(111)
#     line = ax.plot(xf, amplitude_spectrum)
#     ax.set_title("FFT分析图")
#     ax.set_xlabel("频率")
#     ax.set_ylabel("幅度")
#     widget.cursor = mplcursors.cursor(line, hover=True)
#     widget.cursor.connect(
#         "add", lambda sel: sel.annotation.set_text(
#             f"Frequency: {sel.target[0]:.2f}\nAmplitude: {sel.target[1]:.2f}"
#         )
#     )
#     widget.canvas.draw()
