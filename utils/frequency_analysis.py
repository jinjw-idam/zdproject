import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')  # 无GUI环境绘图
plt.rcParams['axes.unicode_minus'] = False  # avoid minus sign issue


def summarize_frequency_data(freq, mag, phase, N=20):
    """统计基本信息及频率、幅值、相位的前N个值字符串"""
    return {
        'count': len(freq),
        'frequency_min': float(np.min(freq)),
        'frequency_max': float(np.max(freq)),
        'magnitude_min': float(np.min(mag)),
        'magnitude_max': float(np.max(mag)),
        'phase_min': float(np.min(phase)),
        'phase_max': float(np.max(phase)),
        'frequency_first_n': ', '.join(map(str, freq[:N])),
        'magnitude_first_n': ', '.join(map(str, mag[:N])),
        'phase_first_n': ', '.join(map(str, phase[:N]))
    }

def find_peak_magnitude(freq, mag):
    """找幅值的最大峰值对应的频率和值"""
    idx = np.argmax(np.abs(mag))
    return float(freq[idx]), float(mag[idx])

def detect_anomaly_magnitude(mag, threshold_std=5.0):
    """简单基于标准差的异常检测"""
    std_val = np.std(mag)
    if std_val > threshold_std:
        return f"检测到幅值波动异常（标准差={std_val:.2f}）"
    else:
        return f"幅值稳定（标准差={std_val:.2f}），未检测到异常"

def plot_magnitude_trend(freq, mag, save_dir, filename_prefix):
    """绘制频率-幅值趋势图并保存"""
    plt.figure(figsize=(8, 4))
    plt.plot(freq, mag, label='Magnitude (dB)')
    plt.title('Frequency-Magnitude Trend')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.grid(True)
    plt.legend()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{filename_prefix}_magnitude.png")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path

def plot_phase_trend(freq, phase, save_dir, filename_prefix):
    """绘制频率-相位趋势图并保存"""
    plt.figure(figsize=(8, 4))
    plt.plot(freq, phase, color='orange', label='Phase (°)')
    plt.title('Frequency-Phase Trend')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Phase (°)')
    plt.grid(True)
    plt.legend()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{filename_prefix}_phase.png")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path
