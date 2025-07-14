import json
import traceback

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
from models import db, UploadedData
from utils.file_utils import get_info

routes = Blueprint('routes', __name__)

UPLOAD_DIR = 'static/uploaded_files'
os.makedirs(UPLOAD_DIR, exist_ok=True)


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


# @routes.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#
#     filename = file.filename
#     upload_time = datetime.utcnow()
#
#     try:
#         if filename.lower().endswith('.txt'):
#             stream = io.StringIO(file.stream.read().decode('utf-8'))
#             df = pd.read_csv(stream, delimiter='\t')
#         elif filename.lower().endswith('.xlsx'):
#             df = pd.read_excel(file)
#         else:
#             return jsonify({'error': 'Unsupported file type'}), 400
#
#         if 'time' not in df.columns or 'amplitude' not in df.columns:
#             return jsonify({'error': 'Missing required columns: time, amplitude'}), 400
#
#         time_list = df['time'].tolist()
#         amplitude_list = df['amplitude'].tolist()
#
#         save_path = os.path.join(UPLOAD_DIR, filename)
#         file.seek(0)
#         file.save(save_path)
#
#         record = UploadedData(
#             filename=filename,
#             upload_time=upload_time,
#             file_path=save_path,
#             time_list=json.dumps(time_list),
#             amplitude_list=json.dumps(amplitude_list)
#         )
#
#         db.session.add(record)
#         db.session.commit()
#
#         return jsonify({'message': '文件上传成功', 'id': record.id}), 200
#
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
#
#
# @routes.route('/upload_path', methods=['POST'])
# def upload_by_path():
#     try:
#         data = request.get_json()
#         file_path = data.get('file_path')
#
#         if not file_path or not os.path.exists(file_path):
#             return jsonify({'error': '路径无效或文件不存在'}), 400
#
#         filename = os.path.basename(file_path)
#         upload_time = datetime.utcnow()
#
#         if filename.lower().endswith('.txt'):
#             df = pd.read_csv(file_path, delimiter='\t')
#         elif filename.lower().endswith('.xlsx'):
#             df = pd.read_excel(file_path)
#         else:
#             return jsonify({'error': '不支持的文件类型'}), 400
#
#         if 'time' not in df.columns or 'amplitude' not in df.columns:
#             return jsonify({'error': '缺少必要列：time, amplitude'}), 400
#
#         time_list = df['time'].tolist()
#         amplitude_list = df['amplitude'].tolist()
#
#         # 复制文件到统一上传目录
#         save_path = os.path.join(UPLOAD_DIR, filename)
#         if file_path != save_path:
#             import shutil
#             shutil.copy(file_path, save_path)
#
#         # 插入数据库
#         record = UploadedData(
#             filename=filename,
#             upload_time=upload_time,
#             file_path=save_path,
#             time_list=json.dumps(time_list),
#             amplitude_list=json.dumps(amplitude_list)
#         )
#         db.session.add(record)
#         db.session.commit()
#
#         return jsonify({'message': '路径上传成功', 'id': record.id}), 200
#
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500
#
#
#
# @routes.route('/search_all', methods=['GET'])
# def search_all():
#     try:
#         records = UploadedData.query.all()
#         data = []
#         for r in records:
#             time_list = json.loads(r.time_list)
#             amplitude_list = json.loads(r.amplitude_list)
#
#             data.append({
#                 'id': r.id,
#                 'filename': r.filename,
#                 'upload_time': r.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 'file_path': r.file_path,
#                 'time': time_list[:3],         # 截取前3个
#                 'amplitude': amplitude_list[:3]
#             })
#         return jsonify({'data': data}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
# @routes.route('/search', methods=['GET'])
# def search():
#     try:
#         id_val = request.args.get('id', type=int)
#         filename_val = request.args.get('filename', type=str)
#
#         query = UploadedData.query
#
#         if id_val is not None:
#             query = query.filter(UploadedData.id == id_val)
#         if filename_val:
#             query = query.filter(UploadedData.filename.like(f"%{filename_val}%"))
#
#         records = query.all()
#
#         data = []
#         for r in records:
#             # 解析JSON字符串成列表
#             time_list = json.loads(r.time_list)
#             amplitude_list = json.loads(r.amplitude_list)
#
#             # 截取前3个元素，避免列表过长
#             time_preview = time_list[:3]
#             amplitude_preview = amplitude_list[:3]
#
#             data.append({
#                 'id': r.id,
#                 'filename': r.filename,
#                 'upload_time': r.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
#                 'file_path': r.file_path,
#                 'time': time_preview,
#                 'amplitude': amplitude_preview
#             })
#
#         return jsonify({'data': data}), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
# @routes.route('/generate_report', methods=['POST'])
# def generate_report():
#     try:
#         data = request.json
#         file_path = data.get('file_path')
#         save_path = data.get('save_path')
#
#         if not file_path or not os.path.exists(file_path):
#             return jsonify({'error': '无效的文件路径'}), 400
#
#         if not save_path or not os.path.isdir(save_path):
#             return jsonify({'error': '保存路径无效或不存在'}), 400
#
#         filename = os.path.basename(file_path)
#
#         # 用 filename 查询数据库记录
#         record = UploadedData.query.filter(UploadedData.filename == filename).first()
#         if not record:
#             return jsonify({'error': f'未找到文件名为 {filename} 的记录'}), 404
#
#         # 获取数据字段
#         import json
#         time_list = json.loads(record.time_list)
#         amplitude_list = json.loads(record.amplitude_list)
#
#         N = 20  # 展示前N个
#         context = {
#             'id': record.id,
#             'filename': record.filename,
#             'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
#             'file_path': record.file_path,
#             'time_str': ', '.join(map(str, time_list[:N])),
#             'amplitude_str': ', '.join(map(str, amplitude_list[:N])),
#             'time_min': min(time_list),
#             'time_max': max(time_list),
#             'amplitude_min': min(amplitude_list),
#             'amplitude_max': max(amplitude_list),
#             'N': N,
#         }
#
#         # 渲染文档
#         template_path = 'report_template.docx'
#         if not os.path.exists(template_path):
#             return jsonify({'error': '报告模板不存在'}), 500
#
#         doc = DocxTemplate(template_path)
#         doc.render(context)
#
#         filename_out = f"report_id{record.id}.docx"
#         full_path = os.path.join(save_path, filename_out)
#         doc.save(full_path)
#
#         return jsonify({'message': '报告生成成功', 'file_path': full_path}), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
# @routes.route('/generate_and_print_report', methods=['POST'])
# def generate_and_print_report():
#     try:
#         data = request.json
#         file_path = data.get('file_path')
#         save_path = data.get('save_path')
#         print(file_path)
#         print(save_path)
#
#         # 1. 校验路径
#         if not file_path or not os.path.exists(file_path):
#             return jsonify({'error': '无效的文件路径'}), 400
#         if not save_path or not os.path.isdir(save_path):
#             return jsonify({'error': '保存路径无效或不存在'}), 400
#
#         filename = os.path.basename(file_path)
#         print("filename:",filename)
#
#         # 2. 查询数据库记录
#         record = UploadedData.query.filter(UploadedData.filename == filename).first()
#         if not record:
#             return jsonify({'error': f'未找到文件名为 {filename} 的记录'}), 404
#
#         time_list = json.loads(record.time_list)
#         amplitude_list = json.loads(record.amplitude_list)
#
#         N = 20
#         context = {
#             'id': record.id,
#             'filename': record.filename,
#             'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
#             'file_path': record.file_path,
#             'time_str': ', '.join(map(str, time_list[:N])),
#             'amplitude_str': ', '.join(map(str, amplitude_list[:N])),
#             'time_min': min(time_list),
#             'time_max': max(time_list),
#             'amplitude_min': min(amplitude_list),
#             'amplitude_max': max(amplitude_list),
#             'N': N,
#         }
#
#         # 3. 加载并渲染 Word 模板
#         template_path = 'report_template.docx'
#         if not os.path.exists(template_path):
#             return jsonify({'error': '报告模板不存在'}), 500
#
#         doc = DocxTemplate(template_path)
#         doc.render(context)
#
#         filename_out = f"report_id{record.id}.docx"
#         full_report_path = os.path.join(save_path, filename_out)
#         doc.save(full_report_path)
#         print("已保存word")
#
#         # 4. 打印 Word 报告
#         pythoncom.CoInitialize()
#         word = win32com.client.Dispatch("Word.Application")
#         word.Visible = False
#
#         docx = word.Documents.Open(full_report_path)
#         docx.PrintOut()
#         docx.Close(False)
#         print("已打印")
#         word.Quit()
#
#         return jsonify({'message': '报告生成并打印成功', 'file_path': full_report_path}), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename
    upload_time = datetime.utcnow()

    try:
        if filename.lower().endswith('.txt'):
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            df = pd.read_csv(stream, delimiter='\t')
        elif filename.lower().endswith('.xlsx'):
            df = pd.read_excel(file)
        elif filename.lower().endswith('.csv'):
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            df = pd.read_csv(stream)  # 默认逗号分隔
        else:
            return jsonify({'error': 'Unsupported file type'}), 400

        if 'time' not in df.columns:
            return jsonify({'error': 'Missing required column: time'}), 400
        required_channels = ['channel_1', 'channel_2', 'channel_3']
        for ch in required_channels:
            if ch not in df.columns:
                return jsonify({'error': f'Missing required channel column: {ch}'}), 400

        time_list = df['time'].tolist()
        channel_1_list = df['channel_1'].tolist()
        channel_2_list = df['channel_2'].tolist()
        channel_3_list = df['channel_3'].tolist()

        save_path = os.path.join(UPLOAD_DIR, filename)
        file.seek(0)
        file.save(save_path)

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

        return jsonify({'message': '文件上传成功', 'id': record.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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


@routes.route('/search', methods=['GET'])
def search():
    try:
        id_val = request.args.get('id', type=int)
        filename_val = request.args.get('filename', type=str)

        query = UploadedData.query

        if id_val is not None:
            query = query.filter(UploadedData.id == id_val)
        if filename_val:
            query = query.filter(UploadedData.filename.like(f"%{filename_val}%"))

        records = query.all()

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


@routes.route('/generate_report', methods=['POST'])
def generate_report():
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
        channel_1_list = json.loads(record.channel_1_list)
        channel_2_list = json.loads(record.channel_2_list)
        channel_3_list = json.loads(record.channel_3_list)

        N = 20
        context = {
            'id': record.id,
            'filename': record.filename,
            'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
            'file_path': record.file_path,
            'time_str': ', '.join(map(str, time_list[:N])),
            'channel_1_str': ', '.join(map(str, channel_1_list[:N])),
            'channel_2_str': ', '.join(map(str, channel_2_list[:N])),
            'channel_3_str': ', '.join(map(str, channel_3_list[:N])),
            'time_min': min(time_list),
            'time_max': max(time_list),
            'channel_1_min': min(channel_1_list),
            'channel_1_max': max(channel_1_list),
            'channel_2_min': min(channel_2_list),
            'channel_2_max': max(channel_2_list),
            'channel_3_min': min(channel_3_list),
            'channel_3_max': max(channel_3_list),
            'N': N,
        }

        template_path = 'report_template.docx'
        if not os.path.exists(template_path):
            return jsonify({'error': '报告模板不存在'}), 500

        doc = DocxTemplate(template_path)
        doc.render(context)

        filename_out = f"report_id{record.id}.docx"
        full_path = os.path.join(save_path, filename_out)
        doc.save(full_path)

        return jsonify({'message': '报告生成成功', 'file_path': full_path}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
        channel_1_list = json.loads(record.channel_1_list)
        channel_2_list = json.loads(record.channel_2_list)
        channel_3_list = json.loads(record.channel_3_list)

        N = 20
        context = {
            'id': record.id,
            'filename': record.filename,
            'upload_time': record.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
            'file_path': record.file_path,
            'time_str': ', '.join(map(str, time_list[:N])),
            'channel_1_str': ', '.join(map(str, channel_1_list[:N])),
            'channel_2_str': ', '.join(map(str, channel_2_list[:N])),
            'channel_3_str': ', '.join(map(str, channel_3_list[:N])),
            'time_min': min(time_list),
            'time_max': max(time_list),
            'channel_1_min': min(channel_1_list),
            'channel_1_max': max(channel_1_list),
            'channel_2_min': min(channel_2_list),
            'channel_2_max': max(channel_2_list),
            'channel_3_min': min(channel_3_list),
            'channel_3_max': max(channel_3_list),
            'N': N,
        }

        template_path = 'report_template.docx'
        if not os.path.exists(template_path):
            return jsonify({'error': '报告模板不存在'}), 500

        doc = DocxTemplate(template_path)
        doc.render(context)

        filename_out = f"report_id{record.id}.docx"
        full_report_path = os.path.join(save_path, filename_out)
        doc.save(full_report_path)

        # 打印 Word 报告
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False

        docx = word.Documents.Open(full_report_path)
        docx.PrintOut()
        docx.Close(False)
        word.Quit()

        return jsonify({'message': '报告生成并打印成功', 'file_path': full_report_path}), 200

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


def get_waterfall_info(file_path, n_segments=20, overlap=0.5):
    time_list, amplitude_list = get_info(file_path)
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


def calculate_cepstrum_routes(channel_data,fs):
    fft_result = fft(channel_data)
    log_spectrum = np.log(np.abs(fft_result) + 1e-10)  # 避免 log(0)
    cepstrum = np.abs(ifft(log_spectrum))  # 实倒谱

    # 计算倒谱的 quefrency（倒频率）轴
    quefrency = np.arange(len(channel_data)) / fs

    return quefrency, cepstrum
