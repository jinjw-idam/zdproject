import os

import matplotlib
from PyQt5 import QtWidgets, QtCore
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from scipy import signal
from scipy.fft import fft, fftfreq

from routes import calculate_cepstrum_routes
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


def calculate_selfcomposed(file_path, show_widget: QWidget, channel_name):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    fs = 1 / (time_list[1] - time_list[0])
    f, Pxx = signal.welch(channel_data, fs, nperseg=len(channel_data))  # Welch方法估计
    ax = show_widget.figure.add_subplot(1, 1, 1)
    line = ax.plot(f, Pxx)
    ax.set_xlabel('频率[Hz]')
    ax.set_ylabel('功率谱密度[V²/Hz]')
    ax.set_title('自谱')
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"X: {sel.target[0]:.2f}\nY: {sel.target[1]:.2f}"
        )
    )
    show_widget.canvas.draw()


def calculate_cepstrum(file_path, show_widget: QWidget, channel_name):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    fs = 1 / (time_list[1] - time_list[0])
    quefrency, cepstrum = calculate_cepstrum_routes(channel_data, fs)
    ax = show_widget.figure.add_subplot(1, 1, 1)
    line = ax.plot(quefrency[:len(channel_data)//2], cepstrum[:len(channel_data)//2])
    ax.set_xlabel('倒频率[s]')
    ax.set_ylabel('倒谱幅值')
    ax.set_title('实倒谱')
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"X: {sel.target[0]:.2f}\nY: {sel.target[1]:.2f}"
        )
    )
    show_widget.canvas.draw()


def create_calculate_widget(need_button=False):
    new_tab = QWidget()  # 创建空白页面（可替换为你的自定义控件）
    new_tab.figure = Figure()
    new_tab.canvas = FigureCanvas(new_tab.figure)
    new_tab.layout = QVBoxLayout(new_tab)  # 直接设置布局到 QWidget
    new_tab.layout.addWidget(new_tab.canvas)  # 添加 Matplotlib 画布
    new_tab.figure.clear()
    new_tab.selected_region = None
    new_tab.span_selector = None
    if need_button:
        new_tab.save_button = QPushButton()
        new_tab.save_button.setText("保存数据块")
        new_tab.save_button.setObjectName("save_button")
        new_tab.layout.addWidget(new_tab.save_button)  # 将标签添加到布局
    return new_tab
