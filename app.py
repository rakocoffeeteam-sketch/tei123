from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)

# 允許跨來源資源共享 (讓前端可以連線後端)
CORS(app)

# 資料庫配置 (使用 SQLite)
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
    # 狀態：Pending -> Ready -> Completed
    status = db.Column(db.String(20), default='Pending') 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- 初始化資料函式 ---

def init_data():
    if Bean.query.first() is None:
        beans = [
            Bean(name="衣索比亞 耶加雪菲", origin="非洲", roast_level="淺焙", flavor="花香、檸檬、柑橘", price=180),
            Bean(name="曼特寧 G1", origin="印尼", roast_level="深焙", flavor="草本、奶油、黑巧克力", price=150),
            Bean(name="巴西 喜拉朵", origin="南美洲", roast_level="中焙", flavor="堅果、焦糖、低酸度", price=120)
        ]
        db.session.bulk_save_objects(beans)
        db.session.commit()
        print("初始化咖啡豆完成！")

# --- API 路由 ---

@app.route('/api/menu', methods=['GET'])
def get_menu():
    beans = Bean.query.all()
    return jsonify([{
        "id": b.id, 
        "name": b.name, 
        "origin": b.origin, 
        "roast_level": b.roast_level, 
        "flavor": b.flavor, 
        "price": b.price
    } for b in beans])

@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    # 這裡假設前端傳來 bean_name 和 price
    new_order = Order(
        items=data.get('bean_name'), 
        total_amount=data.get('price')
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "下單成功", "order_id": new_order.id})

@app.route('/api/order_status/<int:order_id>', methods=['GET'])
def get_order_status(order_id):
    order = db.session.get(Order, order_id)
    if order:
        return jsonify({"status": order.status})
    return jsonify({"message": "找不到訂單"}), 404

@app.route('/api/admin/orders', methods=['GET'])
def get_admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        "id": o.id, 
        "items": o.items, 
        "total_amount": o.total_amount, 
        "status": o.status, 
        "created_at": o.created_at.strftime('%H:%M:%S')
    } for o in orders])

@app.route('/api/admin/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    order = db.session.get(Order, order_id)
    if order:
        # 更新狀態邏輯
        if order.status == 'Pending':
            order.status = 'Ready'
        elif order.status == 'Ready':
            order.status = 'Completed'
        
        db.session.commit()
        return jsonify({"message": "狀態已更新", "new_status": order.status})
    return jsonify({"message": "更新失敗，找不到訂單"}), 404

# --- 啟動程式 ---

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_data()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- API 路由 (給客人用的) ---

@app.route('/api/menu',
