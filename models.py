from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UploadedData(db.Model):
    __tablename__ = 'uploaded_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增ID
    time_list = db.Column(db.Text, nullable=False)                    # time 列表，JSON字符串存储
    amplitude_list = db.Column(db.Text, nullable=False)               # amplitude 列表，JSON字符串存储
    filename = db.Column(db.String(256), nullable=False)              # 原始文件名
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # 上传时间
    file_path = db.Column(db.String(512), nullable=False)  # 文件在服务器的保存路径
