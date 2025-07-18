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

from routes import calculate_cepstrum_routes, calculate_all_routes, apply_weighting, fft_analysis
from utils.file_utils import *

matplotlib.rc("font", family='Microsoft YaHei')
import mplcursors


def draw_fft(file_path, show_widget: QWidget, base_name, channel_name):
    xf, amplitude_spectrum = fft_analysis(file_path,channel_name)
    ax = show_widget.figure.add_subplot(111)
    line = ax.plot(xf, amplitude_spectrum)
    ax.set_title("FFT分析图")
    ax.set_xlabel("频率")
    ax.set_ylabel("幅度")
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"Frequency: {sel.target[0]:.2f}\nAmplitude: {sel.target[1]:.2f}"
        )
    )
    show_widget.save_button.clicked.connect(lambda: save(show_widget.figure, base_name, channel_name, "傅里叶变换"))
    show_widget.canvas.draw()


def calculate_selfcomposed(file_path, show_widget: QWidget, base_name, channel_name):
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
    show_widget.save_button.clicked.connect(lambda: save(show_widget.figure, base_name, channel_name, "自谱"))
    show_widget.canvas.draw()


def calculate_cepstrum(file_path, show_widget: QWidget, base_name, channel_name):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    fs = 1 / (time_list[1] - time_list[0])
    quefrency, cepstrum = calculate_cepstrum_routes(channel_data, fs)
    ax = show_widget.figure.add_subplot(1, 1, 1)
    line = ax.plot(quefrency[:len(channel_data) // 2], cepstrum[:len(channel_data) // 2])
    ax.set_xlabel('倒频率[s]')
    ax.set_ylabel('倒谱幅值')
    ax.set_title('实倒谱')
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"X: {sel.target[0]:.2f}\nY: {sel.target[1]:.2f}"
        )
    )
    show_widget.save_button.clicked.connect(lambda: save(show_widget.figure, base_name, channel_name, "倒谱"))
    show_widget.canvas.draw()


def calculate_all(file_path, show_widget: QWidget, channel_name):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    ax = show_widget.figure.add_subplot(1, 1, 1)
    line = ax.plot(time_list, channel_data)
    ax.set_xlabel('时间')
    ax.set_ylabel('幅度')
    ax.set_title('时域图')
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"X: {sel.target[0]:.2f}\nY: {sel.target[1]:.2f}"
        )
    )
    sum_result, avg_result, max_result, min_result, rms_result = calculate_all_routes(channel_data)
    show_widget.info_output_label.setText(f"和:{sum_result:.2f},平均值:{avg_result:.2f},最大值:{max_result:.2f}\n"
                                          f"最小值:{min_result:.2f},均方根{rms_result:.2f}")
    show_widget.figure.tight_layout()  # 自动调整布局
    show_widget.canvas.draw()


def calculate_weight(file_path, show_widget: QWidget, base_name, channel_name, method_type):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    fs = 1 / (time_list[1] - time_list[0])
    f, Pxx = apply_weighting(channel_data, fs, method_type)
    ax = show_widget.figure.add_subplot(1, 1, 1)
    line = ax.plot(f, Pxx)
    ax.set_xlabel('频率')
    ax.set_ylabel('功率谱密度')
    ax.set_title(f'{method_type} 计权结果')
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"X: {sel.target[0]:.2f}\nY: {sel.target[1]:.2f}"
        )
    )
    show_widget.save_button.clicked.connect(lambda: save(show_widget.figure, base_name, channel_name, f"{method_type}计权"))
    show_widget.canvas.draw()


def calculate_trig(file_path, show_widget: QWidget, base_name, channel_name, method_type):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    ax = show_widget.figure.add_subplot(1, 1, 1)
    line=None
    if method_type == 'sin':
        line = ax.plot(time_list, np.sin(channel_data))
        ax.set_ylabel('正弦值')
        ax.set_title(f'{method_type} 计算结果')
    if method_type == 'cos':
        line = ax.plot(time_list, np.cos(channel_data))
        ax.set_ylabel('余弦值')
        ax.set_title(f'{method_type} 计算结果')
    if method_type == 'tan':
        line = ax.plot(time_list, np.tan(channel_data))
        ax.set_ylabel('正切值')
        ax.set_title(f'{method_type} 计算结果')
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"X: {sel.target[0]:.2f}\nY: {sel.target[1]:.2f}"
        )
    )
    show_widget.save_button.clicked.connect(lambda: save(show_widget.figure, base_name, channel_name, f"{method_type}计算"))
    show_widget.canvas.draw()


def create_calculate_widget(need_button=True, need_label=False):
    new_tab = QWidget()  # 创建空白页面（可替换为你的自定义控件）
    new_tab.figure = Figure()
    new_tab.canvas = FigureCanvas(new_tab.figure)
    new_tab.layout = QVBoxLayout(new_tab)  # 直接设置布局到 QWidget
    new_tab.layout.addWidget(new_tab.canvas)  # 添加 Matplotlib 画布
    new_tab.figure.clear()
    new_tab.selected_region = None
    new_tab.span_selector = None
    if need_label:
        new_tab.info_output_label = QtWidgets.QLabel()
        new_tab.info_output_label.setText("")
        new_tab.info_output_label.setObjectName("info_output_label")
        new_tab.layout.addWidget(new_tab.info_output_label)  # 将标签添加到布局
    if need_button:
        new_tab.save_button = QPushButton()
        new_tab.save_button.setText("保存数据块")
        new_tab.save_button.setObjectName("save_button")
        new_tab.layout.addWidget(new_tab.save_button)  # 将标签添加到布局
    return new_tab


def save(figure, base_name, channel_name, type):
    # 构建保存路径
    save_dir = os.path.join('data_block', base_name)
    save_name = channel_name + '_' + type + '.png'
    save_path = os.path.join(save_dir, save_name)

    # 确保目录存在（如果不存在则创建）
    os.makedirs(save_dir, exist_ok=True)

    # 保存图形
    figure.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存至: {save_path}")
