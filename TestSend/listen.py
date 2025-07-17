import requests
from flask import Flask, request, jsonify
import os
import time
import threading
from datetime import datetime
import pandas as pd

app = Flask(__name__)

channel_cache = []
frequency_cache = []
LAST_RECEIVE_TIME = time.time()
LOCK = threading.Lock()

SAVE_DIR = 'cached_data'
os.makedirs(SAVE_DIR, exist_ok=True)

def detect_data_type(data_dict):
    keys = set(data_dict.keys())
    if {'frequency', 'magnitude', 'phase'}.issubset(keys):
        return 'frequency'
    elif {'time', 'channel_1', 'channel_2', 'channel_3'}.issubset(keys):
        return 'channel'
    else:
        return 'unknown'

def save_cache_to_file(data_list, dtype):
    if not data_list:
        return
    df = pd.DataFrame(data_list)
    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{dtype}_{now_str}.xlsx"
    filepath = os.path.join(SAVE_DIR, filename)
    df.to_excel(filepath, index=False)
    print(f"Saved {dtype} data to {filepath}")

    # 上传文件
    try:
        with open(filepath, 'rb') as f:
            res = requests.post("http://127.0.0.1:5000/upload_path", files={'file': (filename, f)})
            print(f"Upload {dtype} result:", res.status_code)
    except Exception as e:
        print(f"Upload {dtype} error:", e)

def timeout_watcher():
    global LAST_RECEIVE_TIME, channel_cache, frequency_cache
    while True:
        time.sleep(10)
        now = time.time()
        with LOCK:
            if now - LAST_RECEIVE_TIME > 5:  # 5分钟无新数据
                print("Timeout detected. Saving caches...")
                save_cache_to_file(channel_cache, 'channel')
                save_cache_to_file(frequency_cache, 'frequency')
                channel_cache = []
                frequency_cache = []
                LAST_RECEIVE_TIME = now  # 重置时间防止重复触发

@app.route('/receive_data', methods=['POST'])
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

@app.route('/upload_path', methods=['POST'])
def upload_path():
    file = request.files.get('file')
    if file:
        filename = file.filename
        save_path = os.path.join('uploaded_files', filename)
        os.makedirs('uploaded_files', exist_ok=True)
        file.save(save_path)
        print(f"Uploaded and saved: {save_path}")
        return jsonify({'status': 'uploaded'}), 200
    return jsonify({'status': 'no file'}), 400

if __name__ == '__main__':
    threading.Thread(target=timeout_watcher, daemon=True).start()
    app.run(debug=True)
