from flask import Flask
from models import db
import config
from routes import routes
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
app.register_blueprint(routes)
print("当前解释器路径:", sys.executable)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
