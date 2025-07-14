from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UploadedData(db.Model):
    __tablename__ = 'uploaded_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_list = db.Column(db.Text, nullable=False)  # 存储 JSON 格式时间序列
    channel_1_list = db.Column(db.Text, nullable=False)  # 通道 1 数据
    channel_2_list = db.Column(db.Text, nullable=False)  # 通道 2 数据
    channel_3_list = db.Column(db.Text, nullable=False)  # 通道 3 数据
    filename = db.Column(db.String(256), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    file_path = db.Column(db.String(512), nullable=False)

class FrequencyData(db.Model):
    __tablename__ = 'frequency_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    frequency_list = db.Column(db.Text, nullable=False)  # JSON 格式频率列表
    magnitude_list = db.Column(db.Text, nullable=False)  # JSON 格式幅值列表
    phase_list = db.Column(db.Text, nullable=False)      # JSON 格式相位列表
    filename = db.Column(db.String(256), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    file_path = db.Column(db.String(512), nullable=False)



