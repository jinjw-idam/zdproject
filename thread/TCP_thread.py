# thread/TCP_thread.py
import socket
import json
from PyQt5.QtCore import QThread, pyqtSignal


class TCPClientThread(QThread):
    """
    增强版TCP通信线程类，专门处理JSON格式的多通道振动数据
    """
    new_data = pyqtSignal(dict)  # 改为发射解析后的字典数据
    connection_status = pyqtSignal(str)
    parse_error = pyqtSignal(str)  # 新增解析错误信号

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.buffer_size = 4096
        self.raw_buffer = ""  # 用于累积不完整的数据包

    def run(self):
        self.running = True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connection_status.emit(f"Connected to {self.host}:{self.port}")

            while self.running:
                try:
                    data = self.sock.recv(self.buffer_size)
                    if not data:
                        break

                    # 解码并处理数据
                    self._process_received_data(data.decode('utf-8'))

                except socket.error as e:
                    self.connection_status.emit(f"Socket error: {e}")
                    break
                except UnicodeDecodeError:
                    self.parse_error.emit("UTF-8 decode error")
                    continue

        except Exception as e:
            self.connection_status.emit(f"Connection failed: {e}")
        finally:
            if hasattr(self, 'sock'):
                self.sock.close()
            self.connection_status.emit("Disconnected")

    def _process_received_data(self, new_data):
        """处理接收到的数据，解析JSON格式"""
        self.raw_buffer += new_data

        # 按换行符分割处理完整消息
        while '\n' in self.raw_buffer:
            line, self.raw_buffer = self.raw_buffer.split('\n', 1)
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                # 验证数据格式
                if not all(key in data for key in ['time', 'channel_1', 'channel_2', 'channel_3']):
                    raise ValueError("Missing required fields")
                self.new_data.emit(data)
            except json.JSONDecodeError as e:
                self.parse_error.emit(f"JSON parse error: {e}")
            except ValueError as e:
                self.parse_error.emit(f"Data format error: {e}")

    def stop(self):
        self.running = False
        if hasattr(self, 'sock'):
            self.sock.close()