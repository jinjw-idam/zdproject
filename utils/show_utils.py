import os

import matplotlib
import requests
from PyQt5 import QtWidgets, QtCore
import numpy as np
import pandas as pd
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtWidgets import QFileDialog, QWidget, QVBoxLayout
from matplotlib import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import SpanSelector
from scipy import signal
from scipy.fft import fft, fftfreq

from routes import third_octave_spectrum, one_octave_spectrum, get_waterfall_info, get_colormap_info
from utils.file_utils import *

matplotlib.rc("font", family='Microsoft YaHei')
import mplcursors


def draw_XY(file_path, show_widget: QWidget, select=False):
    time_list, amplitude_list = get_info(file_path)
    ax = show_widget.figure.add_subplot(111)
    line = ax.plot(time_list, amplitude_list)
    ax.set_title("XY图")
    ax.set_xlabel("时间")
    ax.set_ylabel("幅度")
    show_widget.cursor = mplcursors.cursor(line, hover=True)
    show_widget.cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"Time: {sel.target[0]:.2f}\nAmplitude: {sel.target[1]:.2f}"
        )
    )
    if select:
        show_widget.span_selector = SpanSelector(
            ax,
            lambda xmin, xmax: on_select(show_widget, time_list, amplitude_list, xmin, xmax),
            'horizontal',
            useblit=True,
            props=dict(alpha=0.4, facecolor='yellow'),
            interactive=True
        )
        show_widget.info_output_label.setText(f"时间范围{time_list[0]:.2f}~{time_list[-1]:.2f}\n"
                                              f"最大值{np.max(amplitude_list):.2f},"
                                              f"最小值{np.min(amplitude_list):.2f},"
                                              f"平均值{np.average(amplitude_list):.2f}")
    show_widget.canvas.draw()


def on_select(widget, time_list, amplitude_list, xmin, xmax):
    """SpanSelector的选择回调函数"""
    # 清除之前的选择区域
    if widget.selected_region:
        for patch in widget.selected_region:
            patch.remove()

    # 绘制新的选择区域
    ax = widget.figure.axes[0]
    widget.selected_region = [
        ax.axvline(xmin, color='red', linestyle='--'),
        ax.axvline(xmax, color='red', linestyle='--'),
        ax.axvspan(xmin, xmax, facecolor='yellow', alpha=0.2)
    ]

    # 获取选择的数据
    mask = (time_list >= xmin) & (time_list <= xmax)
    selected_data = amplitude_list[mask]

    # 打印选择信息（可以替换为你需要的操作）
    widget.info_output_label.setText(f"时间范围{xmin:.2f}~{xmax:.2f}\n"
                                     f"最大值{np.max(selected_data):.2f},最小值{np.min(selected_data):.2f},平均值{np.average(selected_data):.2f}")

    # 刷新画布
    widget.canvas.draw()


def draw_waterfall(file_path, show_widget: QWidget):
    X, Y, Z = get_waterfall_info(file_path)
    show_widget.figure.clear()
    ax = show_widget.figure.add_subplot(111, projection='3d')
    # 绘制瀑布图
    surf = ax.plot_surface(
        X, Y, Z,
        cmap=cm.viridis,
        rstride=1,
        cstride=1,
        linewidth=0,
        antialiased=True
    )

    # 添加颜色条
    show_widget.figure.colorbar(
        surf,
        ax=ax,
        shrink=0.5,
        aspect=10,
        label='Magnitude',
        pad=0.2
    )

    # 设置坐标轴标签
    ax.set_xlabel('Time (s)', labelpad=10)
    ax.set_ylabel('Frequency (Hz)', labelpad=10)
    ax.set_zlabel('Magnitude', labelpad=10)

    # 调整视角
    ax.view_init(elev=30, azim=-45)
    ax.set_title("瀑布图")

    show_widget.canvas.draw()


def draw_Frontback(file_path, show_widget: QWidget):
    time_list, input_amplitude_list, output_amplitude_list = get_file_info(file_path)
    ax = show_widget.figure.add_subplot(111)
    ax.clear()
    line1 = ax.plot(time_list, input_amplitude_list, color='b', linewidth=1.5, label='Front')
    line2 = ax.plot(time_list, output_amplitude_list, color='r', linewidth=1.5, label='Back')
    ax.set_title("Frontback图")
    ax.set_xlabel("时间")
    ax.set_ylabel("幅度")
    cursor1 = mplcursors.cursor(line1, hover=True)
    cursor2 = mplcursors.cursor(line2, hover=True)

    # 定义悬停时的回调函数
    def update_annotation(sel):
        # 获取当前悬停的数据点
        x, y = sel.target[0], sel.target[1]
        # 设置注解文本
        sel.annotation.set_text(
            f"Time: {x:.2f}\nAmplitude: {y:.2f}\nSignal: {'Front' if sel.artist == line1[0] else 'Back'}"
        )
        # 设置注解样式
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

    # 绑定回调函数到两个光标
    cursor1.connect("add", update_annotation)
    cursor2.connect("add", update_annotation)
    show_widget.canvas.draw()


def draw_Bode(file_path, show_widget: QWidget):
    frequency_list, magnitude_list, phase_list = get_bode_info(file_path)
    show_widget.figure.suptitle("Bode图")
    show_widget.figure.clear()
    ax1 = show_widget.figure.add_subplot(2, 1, 1)
    ax1.semilogx(frequency_list, magnitude_list, 'b')
    ax1.set_title("幅频特性")
    ax1.set_ylabel("幅度 (dB)")
    ax2 = show_widget.figure.add_subplot(2, 1, 2)
    ax2.semilogx(frequency_list, phase_list, 'b', label='理论值')
    ax2.set_title("相频特性")
    ax2.set_ylabel("相位 (度)")
    ax2.set_xlabel("频率 (rad/s)")
    # 刷新画布
    show_widget.canvas.draw()


def draw_Nyquist(file_path, show_widget: QWidget):
    frequency_list, magnitude_list, phase_list = get_bode_info(file_path)
    gain_linear = 10 ** (np.array(magnitude_list) / 20)
    phase_rad = np.array(phase_list) * np.pi / 180
    H = gain_linear * np.exp(1j * phase_rad)
    ax = show_widget.figure.add_subplot(1, 1, 1)
    ax.plot(H.real, H.imag, 'b-')
    ax.plot(H.real, -H.imag, 'b-')
    ax.set_xlabel('实部')
    ax.set_ylabel('虚部')
    ax.set_title('Nyquist图')
    show_widget.canvas.draw()


def draw_third_octave_spectrum(file_path, show_widget: QWidget, channel_name):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    center_freqs_3, levels = third_octave_spectrum(channel_data, fs=1000)
    ax = show_widget.figure.add_subplot(1, 1, 1)
    ax.bar(range(len(center_freqs_3)), levels, width=0.8, color='steelblue', edgecolor='black')

    # 坐标轴标签和标题
    ax.set_xlabel('Center Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Acceleration Level (dB re 1μɡ)', fontsize=12)
    ax.set_title(f'{channel_name}的1/3倍频程图', fontsize=14)

    # 设置X轴刻度（显示ISO中心频率）
    ax.set_xticks(range(len(center_freqs_3)), [f'{f}' for f in center_freqs_3], rotation=45)
    ax.set_xlim(-0.5, len(center_freqs_3) - 0.5)  # 调整边界

    # 网格和样式
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.figure.tight_layout()
    show_widget.canvas.draw()


def draw_one_octave_spectrum(file_path, show_widget: QWidget, channel_name):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    center_freqs_1, levels = one_octave_spectrum(channel_data, fs=1000)
    ax = show_widget.figure.add_subplot(1, 1, 1)
    ax.bar(range(len(center_freqs_1)), levels, width=0.8, color='steelblue', edgecolor='black')

    # 坐标轴标签和标题
    ax.set_xlabel('Center Frequency (Hz)', fontsize=12)
    ax.set_ylabel('Acceleration Level (dB re 1μɡ)', fontsize=12)
    ax.set_title(f'{channel_name}的单倍频程图', fontsize=14)

    # 设置X轴刻度（显示ISO中心频率）
    ax.set_xticks(range(len(center_freqs_1)), [f'{f}' for f in center_freqs_1], rotation=45)
    ax.set_xlim(-0.5, len(center_freqs_1) - 0.5)  # 调整边界

    # 网格和样式
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.figure.tight_layout()
    show_widget.canvas.draw()


def draw_colormap(file_path, show_widget: QWidget, channel_name):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_index = channel_names.index(channel_name)
    channel_data = channel_matrix[channel_index]
    fs = 1 / (time_list[1] - time_list[0])
    t_stft, f, amplitude = get_colormap_info(channel_data, fs)
    ax = show_widget.figure.add_subplot(1, 1, 1)
    mesh = ax.pcolormesh(t_stft, f, amplitude, shading='auto', cmap='jet')  # 'viridis', 'plasma' 等可选
    show_widget.figure.colorbar(mesh, ax=ax, label='Amplitude (m/s²)')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_title('Colormap')
    ax.figure.tight_layout()
    show_widget.canvas.draw()


def draw_shishishow(file_path, show_widget: QWidget):
    time_list, channel_matrix, channel_names = get_csv_info(file_path)
    channel_num = len(channel_names)
    for i in range(channel_num):
        ax = show_widget.figure.add_subplot(channel_num, 1, i + 1)
        line = ax.plot(time_list, channel_matrix[i])
        ax.set_title(f"{channel_names[i]}")
        ax.set_ylabel("振幅")
        cursor = mplcursors.cursor(line, hover=True)

        # 自定义标注文本
        @cursor.connect("add")
        def on_add(sel):
            x, y = sel.target
            sel.annotation.set(text=f"x={x:.2f}\ny={y:.2f}")
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)
    ax.set_xlabel('时间')
    ax.figure.tight_layout()
    show_widget.canvas.draw()


def create_show_widget(need_label=False):
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
    return new_tab
