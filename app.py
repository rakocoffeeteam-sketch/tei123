from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os  # 關鍵：用來讀取雲端環境設定

app = Flask(__name__)

# 允許跨來源資源共享 (讓前端可以連線後端)
CORS(app)

# 資料庫設定 (使用 SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coffee_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 資料庫模型 ---
class Bean(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(50), nullable=False)
    roast_level = db.Column(db.String(20), nullable=False)
    flavor = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Ready, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- 初始化資料函式 (確保網頁一打開就有豆子) ---
def init_data():
    if Bean.query.first() is None:
        beans = [
            Bean(name="耶加雪菲", origin="衣索比亞", roast_level="淺焙", flavor="檸檬、花香、柑橘", price=150),
            Bean(name="曼特寧", origin="印尼", roast_level="深焙", flavor="藥草、黑巧克力、醇厚", price=120),
            Bean(name="肯亞 AA", origin="肯亞", roast_level="中焙", flavor="烏梅、黑醋栗、明亮酸質", price=160)
        ]
        db.session.add_all(beans)
        db.session.commit()
        print("初始化咖啡豆完成！")

# --- API 路由 (給客人用的) ---
@app.route('/api/menu',