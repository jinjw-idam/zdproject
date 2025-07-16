import os

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
matplotlib.use('Agg')  # ✅ 使用不依赖 GUI 的后端
plt.rcParams['axes.unicode_minus'] = False  # avoid minus sign issue


def summarize_data(data_list, N=20):
    """计算数据的统计信息及前N个元素字符串"""
    if not data_list:
        return {"min": None, "max": None, "first_n_str": ""}
    return {
        "min": min(data_list),
        "max": max(data_list),
        "first_n_str": ', '.join(map(str, data_list[:N]))
    }

def compute_sampling_freq(time_list):
    """估算采样频率，假设时间均匀采样"""
    if len(time_list) < 2:
        return None
    dt = time_list[1] - time_list[0]
    if dt <= 0:
        return None
    return 1.0 / dt

def frequency_spectrum(y, fs):
    """计算FFT频谱"""
    n = len(y)
    yf = np.fft.rfft(y)
    xf = np.fft.rfftfreq(n, d=1/fs)
    mag = np.abs(yf)
    return xf, mag

def find_dominant_peak(xf, mag, threshold_ratio=0.1):
    """峰值检测，返回峰值频率和幅值"""
    peaks, properties = find_peaks(mag, height=max(mag)*threshold_ratio)
    if len(peaks) == 0:
        return None, None
    peak_idx = peaks[np.argmax(properties['peak_heights'])]
    return round(xf[peak_idx], 3), round(mag[peak_idx], 3)

def detect_anomaly_mean(data_list, multiplier=1.5):
    """
    基于平均绝对值的异常检测。
    multiplier 越大，容忍范围越宽松。
    """
    if not data_list:
        return "数据为空，无法检测异常。"

    mean_abs = np.mean(np.abs(data_list))
    threshold = multiplier * mean_abs
    if np.any(np.abs(data_list) > threshold):
        return "检测到异常振幅峰值（基于均值），建议进一步分析。"
    return "未检测到明显异常振幅（基于均值）。"


def detect_anomaly_iqr(data_list, multiplier=1.5):
    """
    基于四分位距 IQR 的异常检测，鲁棒性更好。
    multiplier 越大，容忍范围越宽松。
    """
    if not data_list:
        return "数据为空，无法检测异常。"

    q1 = np.percentile(data_list, 25)
    q3 = np.percentile(data_list, 75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr

    if np.any((np.array(data_list) < lower) | (np.array(data_list) > upper)):
        return "检测到异常振幅峰值（基于IQR），建议进一步分析。"
    return "未检测到明显异常振幅（基于IQR）。"

def plot_frequency_spectrum(xf, mag, save_dir, filename_prefix):
    """绘制频谱图并保存，返回保存路径"""
    plt.figure(figsize=(8, 4))
    plt.plot(xf, mag)
    plt.title('Frequency Spectrum')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{filename_prefix}_freq_spectrum.png")
    plt.savefig(save_path)
    plt.close()
    return save_path
