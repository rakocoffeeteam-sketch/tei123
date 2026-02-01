import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 資料庫配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coffee_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 資料模型 ---
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
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- 初始化功能 ---
def init_data():
    if Bean.query.first() is None:
        beans = [
            Bean(name="耶加雪菲", origin="衣索比亞", roast_level="淺焙", flavor="檸檬、花香", price=150),
            Bean(name="曼特寧", origin="印尼", roast_level="深焙", flavor="藥草、巧克力", price=120)
        ]
        db.session.bulk_save_objects(beans)
        db.session.commit()

# --- API 路由 ---
@app.route('/api/menu', methods=['GET'])
def get_menu():
    beans = Bean.query.all()
    return jsonify([{"id": b.id, "name": b.name, "price": b.price} for b in beans])

@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    if not data: return jsonify({"error": "No data"}), 400
    new_order = Order(items=data.get('bean_name'), total_amount=data.get('price'))
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Success", "order_id": new_order.id})

# --- 啟動設定 ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_data()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)