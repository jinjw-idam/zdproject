import pandas as pd
import requests
import time

url = "http://127.0.0.1:5000/receive_data"

def send_data_from_excel_no_header(file_path, interval=0.01):
    # 读取 Excel 文件，没有列名（header=None）
    df = pd.read_excel(file_path, header=None)

    for idx, row in df.iterrows():
        row_len = len(row.dropna())  # 非空的列数

        if row_len == 4:
            data = {
                "time": float(row[0]),
                "channel_1": float(row[1]),
                "channel_2": float(row[2]),
                "channel_3": float(row[3]),
            }
        elif row_len == 3:
            data = {
                "frequency": float(row[0]),
                "magnitude": float(row[1]),
                "phase": float(row[2]),
            }
        else:
            print(f"Row {idx} 列数异常（{row_len}），跳过")
            continue

        try:
            res = requests.post(url, json=data)
            if res.status_code != 200:
                print(f"发送失败，第{idx}行: 状态码 {res.status_code}, 内容 {res.text}")
        except Exception as e:
            print(f"请求异常，第{idx}行: {e}")

        time.sleep(interval)

if __name__ == '__main__':
    send_data_from_excel_no_header('sendDate.xlsx', interval=0.01)
