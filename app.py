from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 資料庫配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coffee_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 資料模型 ---
class Bean(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    origin = db.Column(db.String(50))
    roast_level = db.Column(db.String(20))
    flavor = db.Column(db.String(200))
    price = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items = db.Column(db.String(100))
    total_amount = db.Column(db.Integer)
    status = db.Column(db.String(20), default='Pending') # Pending -> Ready -> Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- 初始化豆單 (如果資料庫是空的) ---
def init_data():
    if Bean.query.first() is None:
        beans = [
            Bean(name="衣索比亞 耶加雪菲", origin="非洲", roast_level="淺焙", flavor="花香、檸檬、柑橘", price=180),
            Bean(name="曼特寧 G1", origin="印尼", roast_level="深焙", flavor="草本、奶油、黑巧克力", price=150),
            Bean(name="巴西 喜拉朵", origin="南美洲", roast_level="中焙", flavor="堅果、焦糖、低酸度", price=120)
        ]
        db.session.bulk_save_objects(beans)
        db.session.commit()

# --- API 路由 ---
@app.route('/api/menu', methods=['GET'])
def get_menu():
    beans = Bean.query.all()
    return jsonify([{"id": b.id, "name": b.name, "origin": b.origin, "roast_level": b.roast_level, "flavor": b.flavor, "price": b.price} for b in beans])

@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    new_order = Order(items=data.get('bean_name'), total_amount=data.get('price'))
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "下單成功", "order_id": new_order.id})

@app.route('/api/order_status/<int:order_id>', methods=['GET'])
def get_order_status(order_id):
    order = Order.query.get(order_id)
    return jsonify({"status": order.status}) if order else ({"message": "找不到"}, 404)

@app.route('/api/admin/orders', methods=['GET'])
def get_admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([{
        "id": o.id, "items": o.items, "total_amount": o.total_amount, 
        "status": o.status, "created_at": o.created_at.strftime('%H:%M:%S')
    } for o in orders])

@app.route('/api/admin/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    order = Order.query.get(order_id)
    if order:
        order.status = 'Ready' if order.status == 'Pending' else 'Completed'
        db.session.commit()
        return jsonify({"message": "狀態已更新"})
    return jsonify({"message": "失敗"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_data()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)