import json
import traceback
import threading
import time

import requests
from flask import Blueprint, request, jsonify
import os
import pandas as pd
from datetime import datetime
import matplotlib
import pythoncom
import win32com.client
from flask import Flask, request, Response
import matlab.engine
import numpy as np
import cv2
from flask import Blueprint, request, jsonify
from datetime import datetime
import io
import csv
import pandas as pd
from scipy import signal
from sqlalchemy import and_
import os
from flask import request, jsonify
from docxtpl import DocxTemplate
import os
from flask import jsonify, request
from docxtpl import DocxTemplate
from docx2pdf import convert
from scipy.fft import fft, fftfreq, ifft
from models import db, UploadedData, FrequencyData
from utils.file_utils import get_info
from utils.vibration_analysis import *
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

from utils.frequency_analysis import *

matplotlib.use('Agg')  # ✅ 使用不依赖 GUI 的后端
routes = Blueprint('routes', __name__)

UPLOAD_DIR = 'static/uploaded_files'
plt.rcParams['axes.unicode_minus'] = False  # avoid minus sign issue

os.makedirs(UPLOAD_DIR, exist_ok=True)

channel_cache = []
frequency_cache = []
LAST_RECEIVE_TIME = time.time()
LOCK = threading.Lock()

SAVE_DIR = 'cached_data'
os.makedirs(SAVE_DIR, exist_ok=True)

saved_files = []  # 记录最新保存文件列表，供前端查询


@routes.route('/')
def hello():
    return "hello"


@routes.route('/fft_analysis')
def fft_analysis():
    try:
        # 获取参数，设置默认值
        time = request.args.get('time', 50.0)
        time_list = [float(x) for x in time.split(',')]
        time_list = matlab.double(time_list)
        amplitude = str(request.args.get('amplitude', 2.0))
        amplitude_list = [float(x) for x in amplitude.split(',')]
        amplitude_list = matlab.double(amplitude_list)
        # 启动MATLAB引擎
        eng = matlab.engine.start_matlab()

        # 调用MATLAB函数
        img_data = eng.fft_analysis(time_list, amplitude_list)
        img_data = np.array(img_data)
        # 关闭MATLAB引擎
        eng.quit()

        _, img_encoded = cv2.imencode('.png', img_data)
        print('!!!!!!!!!!!!!!!')
        img_bytes = img_encoded.tobytes()
        print('done')
        # 返回图像文件
        return img_bytes

    except Exception as e:
        print(str(e))
        return '500'


@routes.route('/draw_waterfall')
def draw_waterfall():
    try:
        # 获取参数，设置默认值
        fs = float(request.args.get('fs', 1000))  # 采样率
        duration = float(request.args.get('duration', 1.0))  # 持续时间(秒)
        frequencies = request.args.get('frequencies', 50.0)
        frequencies = [float(x) for x in frequencies.split(',')]
        frequencies = matlab.double(frequencies)
        amplitudes = str(request.args.get('amplitudes', 2.0))
        amplitudes = [float(x) for x in amplitudes.split(',')]
        amplitudes = matlab.double(amplitudes)
        # 启动MATLAB引擎
        eng = matlab.engine.start_matlab()

        # 调用MATLAB函数
        img_data = eng.generate_waterfall(fs, duration, frequencies, amplitudes, nargout=1)
        img_data = np.array(img_data)
        # 关闭MATLAB引擎
        eng.quit()

        _, img_encoded = cv2.imencode('.png', img_data)
        img_bytes = img_encoded.tobytes()
        # 返回图像文件
        return img_bytes

    except Exception as e:
        print(str(e))
        return '500'


def detect_data_type(data_dict):
    keys = set(data_dict.keys())
    if {'frequency', 'magnitude', 'phase'}.issubset(keys):
        return 'frequency'
    elif {'time', 'channel_1', 'channel_2', 'channel_3'}.issubset(keys):
        return 'channel'
    else:
        return 'unknown'


def save_cache_to_file(data_list, dtype):
    global saved_files
    if not data_list:
        return
    df = pd.DataFrame(data_list)
    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{dtype}_{now_str}.xlsx"
    filepath = os.path.join(SAVE_DIR, filename)
    df.to_excel(filepath, index=False)
    print(f"Saved {dtype} data to {filepath}")
    saved_files.append(filename)


@routes.route('/receive_data', methods=['POST'])
def receive_data():
    global LAST_RECEIVE_TIME, channel_cache, frequency_cache
    data = request.get_json()
    if not data:
        return jsonify({'status': 'no data'}), 400

    dtype = detect_data_type(data)
    if dtype == 'unknown':
        return jsonify({'status': 'unknown data type'}), 400

    with LOCK:
        if dtype == 'channel':
            channel_cache.append(data)
        elif dtype == 'frequency':
            frequency_cache.append(data)
        LAST_RECEIVE_TIME = time.time()

    return jsonify({'status': 'received', 'data_type': dtype}), 200


@routes.route('/save_cache_to_file', methods=['GET'])
def trigger_cache_save():
    global channel_cache, frequency_cache, LAST_RECEIVE_TIME
    with LOCK:
        save_cache_to_file(channel_cache, 'channel')
        save_cache_to_file(frequency_cache, 'frequency')
        channel_cache = []
        frequency_cache = []
        LAST_RECEIVE_TIME = time.time()
    return jsonify({'status': 'cache saved'}), 200


@routes.route('/save_file', methods=['GET'])
def get_saved_files():
    global saved_files
    return jsonify({'files': saved_files})


# def detect_data_type(data_dict):
#     keys = set(data_dict.keys())
#     if {'frequency', 'magnitude', 'phase'}.issubset(keys):
#         return 'frequency'
#     elif {'time', 'channel_1', 'channel_2', 'channel_3'}.issubset(keys):
#         return 'channel'
#     else:
#         return 'unknown'
#
#
# def save_cache_to_file(data_list, dtype):
#     global saved_files
#     if not data_list:
#         return
#     df = pd.DataFrame(data_list)
#     now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
#     filename = f"{dtype}_{now_str}.xlsx"
#     filepath = os.path.join(SAVE_DIR, filename)
#     df.to_excel(filepath, index=False)
#     print(f"Saved {dtype} data to {filepath}")
#     saved_files.append(filename)
#
#
# @routes.route('/receive_data', methods=['POST'])
# def receive_data():
#     global LAST_RECEIVE_TIME, channel_cache, frequency_cache
#     data = request.get_json()
#     if not data:
#         return jsonify({'status': 'no data'}), 400
#
#     dtype = detect_data_type(data)
#     if dtype == 'unknown':
#         return jsonify({'status': 'unknown data type'}), 400
#
#     with LOCK:
#         if dtype == 'channel':
#             channel_cache.append(data)
#         elif dtype == 'frequency':
#             frequency_cache.append(data)
#         LAST_RECEIVE_TIME = time.time()
#
#     return jsonify({'status': 'received', 'data_type': dtype}), 200
#
#
# @routes.route('/save_cache_to_file', methods=['GET'])
# def trigger_cache_save():
#     global channel_cache, frequency_cache, LAST_RECEIVE_TIME
#     with LOCK:
#         save_cache_to_file(channel_cache, 'channel')
#         save_cache_to_file(frequency_cache, 'frequency')
#         channel_cache = []
#         frequency_cache = []
#         LAST_RECEIVE_TIME = time.time()
#     return jsonify({'status': 'cache saved'}), 200
#
#
# @routes.route('/save_file', methods=['GET'])
# def get_saved_files():
#     global saved_files
#     return jsonify({'files': saved_files})


@routes.route('/upload_path', methods=['POST'])
def upload_by_path():
    try:
        data = request.get_json()
        file_path = data.get('file_path')

        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': '路径无效或文件不存在'}), 400

        filename = os.path.basename(file_path)
        upload_time = datetime.utcnow()

        if filename.lower().endswith('.txt'):
            df = pd.read_csv(file_path, delimiter='\t')
        elif filename.lower().endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif filename.lower().endswith('.csv'):
            df = pd.read_csv(file_path)  # 默认逗号分隔
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

        if 'time' not in df.columns:
            return jsonify({'error': '缺少必要列：time'}), 400
        required_channels = ['channel_1', 'channel_2', 'channel_3']
        for ch in required_channels:
            if ch not in df.columns:
                return jsonify({'error': f'缺少必要通道列：{ch}'}), 400

        time_list = df['time'].tolist()
        channel_1_list = df['channel_1'].tolist()
        channel_2_list = df['channel_2'].tolist()
        channel_3_list = df['channel_3'].tolist()

        save_path = os.path.join(UPLOAD_DIR, filename)
        if file_path != save_path:
            import shutil
            shutil.copy(file_path, save_path)

        record = UploadedData(
            filename=filename,
            upload_time=upload_time,
            file_path=save_path,
            time_list=json.dumps(time_list),
            channel_1_list=json.dumps(channel_1_list),
            channel_2_list=json.dumps(channel_2_list),
            channel_3_list=json.dumps(channel_3_list)
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({'message': '路径上传成功', 'id': record.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@routes.route('/upload_freq_path', methods=['POST'])
def upload_by_path_fre():
    try:
        data = request.get_json()
        file_path = data.get('file_path')

        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': '路径无效或文件不存在'}), 400

        filename = os.path.basename(file_path)
        upload_time = datetime.utcnow()

        if filename.lower().endswith('.txt'):
            df = pd.read_csv(file_path, delimiter='\t')
        elif filename.lower().endswith('.xlsx'):
            df = pd.read_excel(file_path)
        elif filename.lower().endswith('.csv'):
            df = pd.read_csv(file_path)  # 默认逗号分隔
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

        if 'frequency' not in df.columns:
            return jsonify({'error': '缺少必要列：frequency'}), 400

        freq_list = df['frequency'].tolist()
        mag_list = df['magnitude'].tolist()
        phase_list = df['phase'].tolist()

        save_path = os.path.join(UPLOAD_DIR, filename)
        if file_path != save_path:
            import shutil
            shutil.copy(file_path, save_path)

        record = FrequencyData(
            filename=filename,
            upload_time=upload_time,
            file_path=save_path,
            frequency_list=json.dumps(freq_list),
            magnitude_list=json.dumps(mag_list),
            phase_list=json.dumps(phase_list),
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({'message': '路径上传成功', 'id': record.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@routes.route('/search_all', methods=['GET'])
def search_all():
    try:
        records = UploadedData.query.all()
        data = []
        for r in records:
            time_list = json.loads(r.time_list)
            channel_1_list = json.loads(r.channel_1_list)
            channel_2_list = json.loads(r.channel_2_list)
            channel_3_list = json.loads(r.channel_3_list)

            data.append({
                'id': r.id,
                'filename': r.filename,
                'upload_time': r.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                'file_path': r.file_path,
                'time': time_list[:3],
                'channel_1': channel_1_list[:3],
                'channel_2': channel_2_list[:3],
                'channel_3': channel_3_list[:3],
            })
        return jsonify({'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes.route('/search_all_freq', methods=['GET'])
def search_all_freq():
    try:
        records = FrequencyData.query.all()
        data = []
        for r in records:
            # 假设frequency_list、magnitude_list、phase_list存的是JSON字符串
            frequency_list = json.loads(r.frequency_list)
            magnitude_list = json.loads(r.magnitude_list)
            phase_list = json.loads(r.phase_list)

            data.append({
                'id': r.id,
                'filename': r.filename,
                'upload_time': r.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                'file_path': r.file_path,
                'frequency': frequency_list[:3],  # 只返回前三条示例
                'magnitude': magnitude_list[:3],
                'phase': phase_list[:3],
            })
        return jsonify({'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes.route('/get_file_type', methods=['GET'])
def get_file_type():
    try:
        file_path = request.args.get('file_path')
        if not file_path:
            return jsonify({'error': '文件路径缺失'}), 400

        filename = os.path.basename(file_path)

        # 查询通道数据表
        if UploadedData.query.filter_by(filename=filename).first():
            return jsonify({'type': 'channel'}), 200

        # 查询频率数据表
        if FrequencyData.query.filter_by(filename=filename).first():
            return jsonify({'type': 'frequency'}), 200

        return jsonify({'error': '文件不存在于数据库中'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    file_path = data.get('file_path')
    save_path = data.get('save_path')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': '无效的文件路径'}), 400

    if not save_path or not os.path.isdir(save_path):
        return jsonify({'error': '保存路径无效或不存在'}), 400

    filename = os.path.basename(file_path)

    record = UploadedData.query.filter(UploadedData.filename == filename).first()
    if not record:
        return jsonify({'error': f'未找到文件名为 {filename} 的记录'}), 404

    time_list = json.loads(record.time_list)
    ch1_list = json.loads(record.channel_1_list)
    ch2_list = json.loads(record.channel_2_list)
    ch3_list = json.loads(record.channel_3_list)

    N = 20

    # 统计
    time_stats = summarize_data(time_list, N)
    ch1_stats = summarize_data(ch1_list, N)
    ch2_stats = summarize_data(ch2_list, N)
    ch3_stats = summarize_data(ch3_list, N)

    fs = compute_sampling_freq(time_list)
    if fs is None:
        return jsonify({'error': '时间数据异常，无法计算采样频率'}), 400

    xf, mag = frequency_spectrum(np.array(ch1_list), fs)
    ch1_peak_freq, ch1_peak_mag = find_dominant_peak(xf, mag)

    xf2, mag2 = frequency_spectrum(np.array(ch2_list), fs)
    ch2_peak_freq, ch2_peak_mag = find_dominant_peak(xf, mag)

    xf3, mag3 = frequency_spectrum(np.array(ch3_list), fs)
    ch3_peak_freq, ch3_peak_mag = find_dominant_peak(xf, mag)

    anomaly_ch1 = detect_anomaly_mean(ch1_list)
    anomaly_ch2 = detect_anomaly_iqr(ch2_list)
    anomaly_ch3 = detect_anomaly_iqr(ch3_list)

    freq_plot_path = plot_frequency_spectrum(xf, mag, save_path, f"report_{record.id}_ch1")
    freq_plot_path2 = plot_frequency_spectrum(xf2, mag2, save_path, f"report_{record.id}_ch2")
    freq_plot_path3 = plot_frequency_spectrum(xf3, mag3, save_path, f"report_{record.id}_ch3")

    doc = DocxTemplate('report_template.docx')
    # 模板上下文
    context = {
        'id': record.id,
        'filename': record.filename,
        'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
        'file_path': record.file_path,
        'time_min': time_stats['min'],
        'time_max': time_stats['max'],
        'channel_1_str': ch1_stats['first_n_str'],
        'channel_1_min': ch1_stats['min'],
        'channel_1_max': ch1_stats['max'],
        'channel_2_str': ch2_stats['first_n_str'],
        'channel_2_min': ch2_stats['min'],
        'channel_2_max': ch2_stats['max'],
        'channel_3_str': ch3_stats['first_n_str'],
        'ch3_min': ch3_stats['min'],
        'ch3_max': ch3_stats['max'],
        'ch1_peak_freq': ch1_peak_freq,
        'ch1_peak_mag': ch1_peak_mag,
        'ch2_peak_freq': ch2_peak_freq,
        'ch2_peak_mag': ch2_peak_mag,
        'ch3_peak_freq': ch3_peak_freq,
        'ch3_peak_mag': ch3_peak_mag,
        'anomaly_ch1': anomaly_ch1,
        'anomaly_ch2': anomaly_ch2,
        'anomaly_ch3': anomaly_ch3,
        'N': N,
        'freq_spectrum_image': InlineImage(doc, freq_plot_path, width=Mm(150)),
        'freq_spectrum_image2': InlineImage(doc, freq_plot_path2, width=Mm(150)),
        'freq_spectrum_image3': InlineImage(doc, freq_plot_path3, width=Mm(150)),
    }

    doc.render(context)

    output_path = os.path.join(save_path, f"report_id{record.id}.docx")
    doc.save(output_path)

    return jsonify({'message': '报告生成成功', 'file_path': output_path}), 200


@routes.route('/generate_and_print_report', methods=['POST'])
def generate_and_print_report():
    try:
        data = request.json
        file_path = data.get('file_path')
        save_path = data.get('save_path')

        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': '无效的文件路径'}), 400

        if not save_path or not os.path.isdir(save_path):
            return jsonify({'error': '保存路径无效或不存在'}), 400

        filename = os.path.basename(file_path)
        record = UploadedData.query.filter(UploadedData.filename == filename).first()
        if not record:
            return jsonify({'error': f'未找到文件名为 {filename} 的记录'}), 404

        time_list = json.loads(record.time_list)
        ch1_list = json.loads(record.channel_1_list)
        ch2_list = json.loads(record.channel_2_list)
        ch3_list = json.loads(record.channel_3_list)

        N = 20
        time_stats = summarize_data(time_list, N)
        ch1_stats = summarize_data(ch1_list, N)
        ch2_stats = summarize_data(ch2_list, N)
        ch3_stats = summarize_data(ch3_list, N)

        fs = compute_sampling_freq(time_list)
        if fs is None:
            return jsonify({'error': '时间数据异常，无法计算采样频率'}), 400

        # 频谱分析
        xf, mag = frequency_spectrum(np.array(ch1_list), fs)
        xf2, mag2 = frequency_spectrum(np.array(ch2_list), fs)
        xf3, mag3 = frequency_spectrum(np.array(ch3_list), fs)

        ch1_peak_freq, ch1_peak_mag = find_dominant_peak(xf, mag)
        ch2_peak_freq, ch2_peak_mag = find_dominant_peak(xf2, mag2)
        ch3_peak_freq, ch3_peak_mag = find_dominant_peak(xf3, mag3)

        anomaly_ch1 = detect_anomaly_mean(ch1_list)
        anomaly_ch2 = detect_anomaly_iqr(ch2_list)
        anomaly_ch3 = detect_anomaly_iqr(ch3_list)

        # 频谱图保存
        freq_plot_path = plot_frequency_spectrum(xf, mag, save_path, f"report_{record.id}_ch1")
        freq_plot_path2 = plot_frequency_spectrum(xf2, mag2, save_path, f"report_{record.id}_ch2")
        freq_plot_path3 = plot_frequency_spectrum(xf3, mag3, save_path, f"report_{record.id}_ch3")

        # 渲染报告
        doc = DocxTemplate('report_template.docx')
        context = {
            'id': record.id,
            'filename': record.filename,
            'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
            'file_path': record.file_path,
            'time_min': time_stats['min'],
            'time_max': time_stats['max'],
            'channel_1_str': ch1_stats['first_n_str'],
            'channel_1_min': ch1_stats['min'],
            'channel_1_max': ch1_stats['max'],
            'channel_2_str': ch2_stats['first_n_str'],
            'channel_2_min': ch2_stats['min'],
            'channel_2_max': ch2_stats['max'],
            'channel_3_str': ch3_stats['first_n_str'],
            'ch3_min': ch3_stats['min'],
            'ch3_max': ch3_stats['max'],
            'ch1_peak_freq': ch1_peak_freq,
            'ch1_peak_mag': ch1_peak_mag,
            'ch2_peak_freq': ch2_peak_freq,
            'ch2_peak_mag': ch2_peak_mag,
            'ch3_peak_freq': ch3_peak_freq,
            'ch3_peak_mag': ch3_peak_mag,
            'anomaly_ch1': anomaly_ch1,
            'anomaly_ch2': anomaly_ch2,
            'anomaly_ch3': anomaly_ch3,
            'N': N,
            'freq_spectrum_image': InlineImage(doc, freq_plot_path, width=Mm(150)),
            'freq_spectrum_image2': InlineImage(doc, freq_plot_path2, width=Mm(150)),
            'freq_spectrum_image3': InlineImage(doc, freq_plot_path3, width=Mm(150)),
        }

        doc.render(context)
        output_path = os.path.join(save_path, f"report_id{record.id}.docx")
        doc.save(output_path)

        # 打印 Word 报告
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()

        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        docx = word.Documents.Open(output_path)
        docx.PrintOut()
        docx.Close(False)
        word.Quit()

        return jsonify({'message': '报告生成并打印成功', 'file_path': output_path}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes.route('/generate_freq_report', methods=['POST'])
def generate_freq_report():
    try:
        data = request.json
        file_path = data.get('file_path')
        save_path = data.get('save_path')

        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': '无效的文件路径'}), 400

        if not save_path or not os.path.isdir(save_path):
            return jsonify({'error': '保存路径无效或不存在'}), 400

        filename = os.path.basename(file_path)
        record = FrequencyData.query.filter_by(filename=filename).first()
        if not record:
            return jsonify({'error': f'未找到文件名为 {filename} 的记录'}), 404

        freq = np.array(json.loads(record.frequency_list))
        mag = np.array(json.loads(record.magnitude_list))
        phase = np.array(json.loads(record.phase_list))

        # 分析
        stats = summarize_frequency_data(freq, mag, phase)
        peak_frequency, peak_magnitude = find_peak_magnitude(freq, mag)
        anomaly_result = detect_anomaly_magnitude(mag)

        # 生成图像
        prefix = f"report_{record.id}"
        magnitude_plot_path = plot_magnitude_trend(freq, mag, save_path, prefix)
        phase_plot_path = plot_phase_trend(freq, phase, save_path, prefix)

        # 生成 Word 报告
        doc = DocxTemplate('report_template_2.docx')
        context = {
            'id': record.id,
            'filename': record.filename,
            'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
            'file_path': record.file_path,
            'stats': stats,
            'peak_frequency': peak_frequency,
            'peak_magnitude': peak_magnitude,
            'anomaly_result': anomaly_result,
            'magnitude_plot': InlineImage(doc, magnitude_plot_path, width=Mm(150)),
            'phase_plot': InlineImage(doc, phase_plot_path, width=Mm(150)),
        }
        output_path = os.path.join(save_path, f"freq_report_{record.id}.docx")
        doc.render(context)
        doc.save(output_path)

        return jsonify({'message': '频率报告生成成功', 'file_path': output_path}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes.route('/generate_and_print_freq_report', methods=['POST'])
def generate_and_print_freq_report():
    try:
        data = request.json
        file_path = data.get('file_path')
        save_path = data.get('save_path')

        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': '无效的文件路径'}), 400

        if not save_path or not os.path.isdir(save_path):
            return jsonify({'error': '保存路径无效或不存在'}), 400

        filename = os.path.basename(file_path)
        record = FrequencyData.query.filter_by(filename=filename).first()
        if not record:
            return jsonify({'error': f'未找到文件名为 {filename} 的记录'}), 404

        freq = np.array(json.loads(record.frequency_list))
        mag = np.array(json.loads(record.magnitude_list))
        phase = np.array(json.loads(record.phase_list))

        stats = summarize_frequency_data(freq, mag, phase)
        peak_frequency, peak_magnitude = find_peak_magnitude(freq, mag)
        anomaly_result = detect_anomaly_magnitude(mag)

        prefix = f"report_{record.id}"
        magnitude_plot_path = plot_magnitude_trend(freq, mag, save_path, prefix)
        phase_plot_path = plot_phase_trend(freq, phase, save_path, prefix)

        doc = DocxTemplate('report_template_2.docx')
        context = {
            'id': record.id,
            'filename': record.filename,
            'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
            'file_path': record.file_path,
            'stats': stats,
            'peak_frequency': peak_frequency,
            'peak_magnitude': peak_magnitude,
            'anomaly_result': anomaly_result,
            'magnitude_plot': InlineImage(doc, magnitude_plot_path, width=Mm(150)),
            'phase_plot': InlineImage(doc, phase_plot_path, width=Mm(150)),
        }
        output_path = os.path.join(save_path, f"freq_report_{record.id}.docx")
        doc.render(context)
        doc.save(output_path)

        # 打印 Word 报告 (Windows 环境下)
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        docx = word.Documents.Open(output_path)
        docx.PrintOut()
        docx.Close(False)
        word.Quit()

        return jsonify({'message': '频率报告已生成并发送到打印机', 'file_path': output_path}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


################################不使用matlab，而使用matplotlib#######################################
center_freqs_3 = np.array([10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125,
                           160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250,
                           1600, 2000])
center_freqs_1 = np.array([31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])


def third_octave_spectrum(data, fs, ref=1e-6):
    lower_freqs = center_freqs_3 / (2 ** (1 / 6))
    upper_freqs = center_freqs_3 * (2 ** (1 / 6))

    # 计算PSD (Welch方法)
    freqs, psd = signal.welch(data, fs, nperseg=fs // 2)

    # 频带能量积分
    rms_values = []
    for fl, fu in zip(lower_freqs, upper_freqs):
        mask = (freqs >= fl) & (freqs <= fu)
        rms = np.sqrt(np.trapezoid(psd[mask], freqs[mask])) if any(mask) else 0
        rms_values.append(max(rms, 1e-10))
    # 转换为加速度级 (dB, 参考1μɡ)
    levels = 20 * np.log10(np.array(rms_values) / ref)
    levels = np.maximum(levels, 0)  # 将负值截断为0
    return center_freqs_3, levels


def one_octave_spectrum(data, fs, ref=1e-6):
    lower_freqs = center_freqs_1 / (2 ** (1 / 2))
    upper_freqs = center_freqs_1 * (2 ** (1 / 2))

    # 计算PSD (Welch方法)
    freqs, psd = signal.welch(data, fs, nperseg=fs // 2)

    # 频带能量积分
    rms_values = []
    for fl, fu in zip(lower_freqs, upper_freqs):
        mask = (freqs >= fl) & (freqs <= fu)
        rms = np.sqrt(np.trapezoid(psd[mask], freqs[mask])) if any(mask) else 0
        rms_values.append(max(rms, 1e-10))
    # 转换为加速度级 (dB, 参考1μɡ)
    levels = 20 * np.log10(np.array(rms_values) / ref)
    levels = np.maximum(levels, 0)  # 将负值截断为0
    return center_freqs_1, levels


def get_waterfall_info(file_path, channel_name, n_segments=20, overlap=0.5):
    time_list, channel_matrix, channel_names = get_info(file_path)
    channel_index = channel_names.index(channel_name)
    amplitude_list = channel_matrix[channel_index]
    time_array = np.array(time_list)
    amplitude_array = np.array(amplitude_list)

    # 计算基本参数
    N = len(time_array)  # 总采样点数
    T = time_array[1] - time_array[0]  # 采样间隔(秒)
    Fs = 1 / T  # 采样频率(Hz)

    # 分段参数计算
    segment_length = int(N // (n_segments * (1 - overlap) + n_segments * overlap))
    step = int(segment_length * (1 - overlap))

    # 准备三维坐标数据
    x = []  # 时间轴 (每段的中心时间)
    y = None  # 频率轴
    z = []  # 幅度矩阵

    # 分段计算FFT (修复缩进)
    for i in range(n_segments):
        start = i * step
        end = start + segment_length
        if end > N:
            break

        # 获取当前段数据
        segment = amplitude_array[start:end]
        center_time = time_array[start + segment_length // 2]

        # 计算FFT
        yf = fft(segment)
        freq = fftfreq(segment_length, T)[:segment_length // 2]
        magnitude = 2 / segment_length * np.abs(yf[0:segment_length // 2])

        x.append(center_time)
        if y is None:  # 只需设置一次频率轴
            y = freq
        z.append(magnitude)

    # 转换为numpy数组
    X, Y = np.meshgrid(x, y)
    Z = np.array(z).T  # 转置使维度匹配
    return X, Y, Z


def get_colormap_info(channel_data, fs):
    # STFT 参数
    window = 'hann'  # 窗函数
    nperseg = 256  # 每段FFT长度
    noverlap = 128  # 重叠点数

    # 计算STFT
    f, t_stft, Zxx = signal.stft(channel_data, fs, window=window, nperseg=nperseg, noverlap=noverlap)

    # Zxx 是复数矩阵，取其幅值（dB或线性）
    amplitude = np.abs(Zxx)  # 线性幅值
    return t_stft, f, amplitude


def calculate_cepstrum_routes(channel_data, fs):
    fft_result = fft(channel_data)
    log_spectrum = np.log(np.abs(fft_result) + 1e-10)  # 避免 log(0)
    cepstrum = np.abs(ifft(log_spectrum))  # 实倒谱

    # 计算倒谱的 quefrency（倒频率）轴
    quefrency = np.arange(len(channel_data)) / fs

    return quefrency, cepstrum


def calculate_all_routes(channel_data):
    sum_result = np.sum(channel_data)
    avg_result = np.mean(channel_data)
    max_result = np.max(channel_data)
    min_result = np.min(channel_data)
    rms_result = np.sqrt(np.mean(np.square(channel_data)))
    return sum_result, avg_result, max_result, min_result, rms_result


# 定义标准频率点(Hz)
frequencies = np.array([0.1, 0.125, 0.16, 0.2, 0.25, 0.315, 0.4, 0.5, 0.63,
                        0.8, 1, 1.25, 1.6, 2, 2.5, 3.15, 4, 5, 6.3, 8, 10,
                        12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125,
                        160, 200, 250, 315, 400, 500, 630, 800, 1000,
                        1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300,
                        8000, 10000, 12500, 16000, 20000])

# ABC计权在各频率点上的修正值(dB)
A_weighting = np.array([-70.4, -63.4, -56.7, -50.5, -44.7, -39.4, -34.6,
                        -30.2, -26.2, -22.5, -19.1, -16.1, -13.4, -10.9,
                        -8.6, -6.6, -4.8, -3.2, -1.9, -0.8, 0, 0.6, 1.0,
                        1.2, 1.3, 1.2, 1.0, 0.5, -0.1, -1.1, -2.5, -4.3,
                        -6.6, -9.3, -12.2, -15.2, -18.2, -21.3, -24.2,
                        -27.1, -29.9, -32.5, -34.9, -37.2, -39.4, -41.4,
                        -43.3, -45.2, -46.9, -48.5, -50.0, -51.4, -52.7,
                        -53.9, -55.0])

B_weighting = np.array([-38.2, -33.2, -28.5, -24.2, -20.4, -16.8, -13.8,
                        -10.9, -8.4, -6.2, -4.4, -2.9, -1.6, -0.6, 0, 0.3,
                        0.5, 0.6, 0.6, 0.5, 0, -0.9, -2.0, -3.2, -4.6, -6.1,
                        -7.8, -9.6, -11.5, -13.4, -15.3, -17.2, -19.1, -21.0,
                        -22.8, -24.6, -26.3, -28.0, -29.6, -31.2, -32.7,
                        -34.1, -35.5, -36.8, -38.1, -39.3, -40.5, -41.6,
                        -42.7, -43.7, -44.7, -45.6, -46.5, -47.4, -48.2])

C_weighting = np.array([-14.3, -11.2, -8.5, -6.2, -4.4, -3.0, -2.0, -1.3,
                        -0.8, -0.5, -0.3, -0.2, -0.1, 0, 0, 0, 0, 0, 0, 0,
                        0, -0.1, -0.2, -0.3, -0.5, -0.8, -1.3, -1.9, -2.6,
                        -3.4, -4.2, -5.1, -6.0, -6.9, -7.9, -8.9, -9.9,
                        -10.9, -11.9, -12.9, -13.9, -14.9, -15.9, -16.9,
                        -17.9, -18.9, -19.9, -20.9, -21.9, -22.9, -23.9,
                        -24.9, -25.9, -26.9, -27.9, -28.9])


def design_weighting_filter(fs, weighting_type='A'):
    """
    设计ABC计权滤波器
    :param fs: 采样频率
    :param weighting_type: 'A', 'B' 或 'C'
    :return: 滤波器系数 (b, a)
    """
    if weighting_type == 'A':
        # A计权滤波器设计
        f1 = 20.598997
        f2 = 107.65265
        f3 = 737.86223
        f4 = 12194.217
        A1000 = 1.9997

        NUM = [(2 * np.pi * f4) ** 2 * (10 ** (A1000 / 20)), 0, 0, 0, 0]
        DEN = np.polymul([1, 4 * np.pi * f4, (2 * np.pi * f4) ** 2],
                         [1, 4 * np.pi * f1, (2 * np.pi * f1) ** 2])
        DEN = np.polymul(DEN, [1, 2 * np.pi * f3])
        DEN = np.polymul(DEN, [1, 2 * np.pi * f2])

    elif weighting_type == 'B':
        # B计权滤波器设计
        f1 = 20.598997
        f2 = 158.5
        f4 = 12194.217
        B1000 = 0.1696

        NUM = [(2 * np.pi * f4) ** 2 * (10 ** (B1000 / 20)), 0, 0, 0]
        DEN = np.polymul([1, 4 * np.pi * f4, (2 * np.pi * f4) ** 2],
                         [1, 4 * np.pi * f1, (2 * np.pi * f1) ** 2])
        DEN = np.polymul(DEN, [1, 2 * np.pi * f2])

    elif weighting_type == 'C':
        # C计权滤波器设计
        f1 = 20.598997
        f4 = 12194.217
        C1000 = 0.0619

        NUM = [(2 * np.pi * f4) ** 2 * (10 ** (C1000 / 20)), 0, 0]
        DEN = np.polymul([1, 4 * np.pi * f4, (2 * np.pi * f4) ** 2],
                         [1, 4 * np.pi * f1, (2 * np.pi * f1) ** 2])
    else:
        raise ValueError("weighting_type must be 'A', 'B' or 'C'")

    # 双线性变换
    b, a = signal.bilinear(NUM, DEN, fs)
    return b, a


def apply_weighting(data, fs, weighting_type='A'):
    """
    应用ABC计权滤波器
    :param data: 输入信号
    :param fs: 采样频率
    :param weighting_type: 'A', 'B' 或 'C'
    :return: 加权后的信号
    """
    b, a = design_weighting_filter(fs, weighting_type)
    weighted_data = signal.lfilter(b, a, data)
    f, Pxx = signal.welch(weighted_data, fs, nperseg=fs // 2)
    return f, Pxx
