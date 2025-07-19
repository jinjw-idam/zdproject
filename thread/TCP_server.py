import numpy as np
import socket
import json
import time
from datetime import datetime

# 参数设置
fs = 1000  # 采样率 (Hz)
num_channels = 3  # 通道数量

# 多通道信号配置
frequencies = [
    [50, 120, 400],  # 通道1频率成分
    [60, 150, 500],  # 通道2频率成分
    [40, 100, 300]  # 通道3频率成分
]
amplitudes = [
    [0.1, 0.05, 0.02],  # 通道1幅值
    [0.08, 0.03, 0.01],  # 通道2幅值
    [0.12, 0.06, 0.03]  # 通道3幅值
]

# TCP服务器设置
HOST = '127.0.0.1'
PORT = 5050


def send_data_via_tcp():
    """通过TCP持续发送时间戳和多通道数据"""
    sample_index = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            try:
                while True:
                    # 计算已运行时间
                    elapsed_time = sample_index * 1/fs

                    # 生成当前时刻的信号值（避免生成整个时间序列）
                    current_signals = []
                    for ch in range(num_channels):
                        signal_value = 0.0
                        for freq, amp in zip(frequencies[ch], amplitudes[ch]):
                            signal_value += amp * np.sin(2 * np.pi * freq * elapsed_time)
                        current_signals.append(signal_value)

                    # 构造数据包
                    data_packet = {
                        "time": elapsed_time,  # 运行时长
                        "channel_1": current_signals[0],
                        "channel_2": current_signals[1],
                        "channel_3": current_signals[2],
                    }
                    sample_index += 1

                    # JSON格式化并发送
                    data_str = json.dumps(data_packet) + "\n"
                    conn.sendall(data_str.encode())

                    # 控制发送速率（根据采样率）
                    time.sleep(1 / fs)

                    # 每秒打印一次状态
                    if sample_index % fs == 0:
                        print(f"Sent {sample_index} samples")

            except KeyboardInterrupt:
                print("\nServer stopped by user")
            except ConnectionResetError:
                print("Client disconnected")


if __name__ == "__main__":
    send_data_via_tcp()