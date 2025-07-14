import pandas as pd
from PyQt5.QtWidgets import QFileDialog


def new_file():
    img_path = QFileDialog.getOpenFileName(None, 'Select File')[0]
    time_list = None
    amplitude_list = None
    if img_path.endswith('xlsx'):
        df = pd.read_excel(img_path)  # 确保文件路径正确
        time_list = df['time'].values
        amplitude_list = df['amplitude'].values
    return img_path, time_list, amplitude_list


def get_info(file_path):
    if file_path.endswith('xlsx'):
        df = pd.read_excel(file_path)  # 确保文件路径正确
        time_list = df['time'].values
        amplitude_list = df['amplitude'].values
        return time_list, amplitude_list
    if file_path.endswith('.csv'):
        time_array, channel_matrix, channel_names = get_csv_info(file_path)
        return time_array, channel_matrix, channel_names


def get_file_info(file_path):
    time_list = None
    input_amplitude_list = None
    output_amplitude_list = None
    if file_path.endswith('xlsx'):
        df = pd.read_excel(file_path)  # 确保文件路径正确
        time_list = df['time'].values
        input_amplitude_list = df['input_amplitude'].values
        output_amplitude_list = df['output_amplitude'].values
    return time_list, input_amplitude_list, output_amplitude_list


def get_bode_info(file_path):
    frequency_list = None
    magnitude_list = None
    phase_list = None
    if file_path.endswith('xlsx'):
        df = pd.read_excel(file_path)  # 确保文件路径正确
        frequency_list = df['frequency'].values
        magnitude_list = df['magnitude'].values
        phase_list = df['phase'].values
    return frequency_list, magnitude_list, phase_list


def get_csv_info(file_path):
    df = pd.read_csv(file_path)

    # 提取时间列（假设第一列是时间）
    time_array = df.iloc[:, 0].values

    # 提取所有通道数据
    channel_data = df.iloc[:, 1:]  # 选择第一列之后的所有列

    # 转换为矩阵（numpy数组）
    channel_matrix = channel_data.values.T  # 转置使每列成为一个通道

    # 获取通道名称
    channel_names = channel_data.columns.tolist()

    return time_array, channel_matrix, channel_names


def get_channel_name(file_path, index):
    df = pd.read_csv(file_path)
    channel_data = df.iloc[:, 1:]  # 选择第一列之后的所有列
    channel_names = channel_data.columns.tolist()
    return channel_names[index]
