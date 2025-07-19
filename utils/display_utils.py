# display_widget.py
import json

from PyQt5.QtWidgets import (QLabel, QWidget, QVBoxLayout, QTextEdit,
                             QPushButton, QMainWindow, QHBoxLayout)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np

from thread.TCP_thread import TCPClientThread


class tcp_display_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.tcp_thread = None
        self.data_buffers = {
            'time': [],
            'channel_1': [],
            'channel_2': [],
            'channel_3': []
        }
        self.max_points = 1000
        self.setWindowTitle("Vibration Data Monitor")

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 连接控制区域
        control_layout = QHBoxLayout()
        self.connection_label = QLabel("Status: Not connected")
        self.host_input = QTextEdit("127.0.0.1")
        self.host_input.setMaximumHeight(30)
        self.port_input = QTextEdit("5050")
        self.port_input.setMaximumHeight(30)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect)
        self.disconnect_button.setEnabled(False)

        control_layout.addWidget(QLabel("Host:"))
        control_layout.addWidget(self.host_input)
        control_layout.addWidget(QLabel("Port:"))
        control_layout.addWidget(self.port_input)
        control_layout.addWidget(self.connect_button)
        control_layout.addWidget(self.disconnect_button)
        control_layout.addWidget(self.connection_label)

        # 绘图区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.addLegend()
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.showGrid(x=True, y=True)

        # 创建三条曲线，不同颜色
        self.plot_curves = {
            'channel_1': self.plot_widget.plot(pen='y', name='Channel 1'),
            'channel_2': self.plot_widget.plot(pen='b', name='Channel 2'),
            'channel_3': self.plot_widget.plot(pen='r', name='Channel 3')
        }

        # 数据显示区域
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)

        # 组装主界面
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.plot_widget)
        main_layout.addWidget(QLabel("Received Data:"))
        main_layout.addWidget(self.data_display)

        self.setLayout(main_layout)

    def toggle_connection(self):
        if self.tcp_thread and self.tcp_thread.isRunning():
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        host = self.host_input.toPlainText().strip()
        try:
            port = int(self.port_input.toPlainText().strip())
        except ValueError:
            self.connection_label.setText("Status: Invalid port number")
            return

        self.tcp_thread = TCPClientThread(host, port)
        self.tcp_thread.new_data.connect(self.handle_new_data)
        self.tcp_thread.connection_status.connect(self.update_connection_status)
        self.tcp_thread.parse_error.connect(self.handle_parse_error)
        self.tcp_thread.start()

        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)
        self.clear_data()

    def disconnect(self):
        if self.tcp_thread:
            self.tcp_thread.stop()
            self.tcp_thread.wait()
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)

    def update_connection_status(self, status):
        self.connection_label.setText("Status: " + status)
        if "Disconnected" in status or "failed" in status:
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)

    def handle_parse_error(self, error_msg):
        """处理解析错误"""
        self.data_display.append(f"[ERROR] {error_msg}")

    def handle_new_data(self, data):
        """处理接收到的新数据"""
        # 在文本区域显示原始数据
        self.data_display.append(json.dumps(data))

        # 存储数据
        for key in self.data_buffers:
            self.data_buffers[key].append(data[key])

            # 限制数据点数量
            if len(self.data_buffers[key]) > self.max_points:
                self.data_buffers[key] = self.data_buffers[key][-self.max_points:]

        # 更新所有通道的曲线
        for ch in ['channel_1', 'channel_2', 'channel_3']:
            self.plot_curves[ch].setData(
                np.array(self.data_buffers['time']),
                np.array(self.data_buffers[ch])
            )

    def clear_data(self):
        """清除所有数据"""
        for key in self.data_buffers:
            self.data_buffers[key] = []
        self.data_display.clear()

    def closeEvent(self, event):
        """窗口关闭时确保线程停止"""
        self.disconnect()
        event.accept()