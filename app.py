from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SECRET_KEY'] = 'secret_key_here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Veritabanı Modelleri
class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    items = db.relationship('MenuItem', backref='menu', lazy=True)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    details = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Bekliyor')

    @property
    def total_price(self):
        if not self.details:
            return 0.0
        return sum(item['price'] * item['quantity'] for item in self.details)

class CompletedOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    details = db.Column(db.JSON, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)



def get_all_orders():
    # Siparişleri veritabanından çek
    orders = Order.query.order_by(Order.id.desc()).all()
    order_list = []

    # Siparişleri düzenle
    for order in orders:
        if isinstance(order.details, str):
            order.details = json.loads(order.details)  # Detayları JSON formatına dönüştür
        order_list.append({
            'id': order.id,
            'table_number': order.table_number,
            'details': order.details,
            'status': order.status,
            'total_price': order.total_price
        })

    return order_list


@app.route('/')
def index():
    return redirect(url_for('admin_login'))  # Uygulama başladığında admin giriş sayfasına yönlendiriyor.


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'mcstone' and password == 'thekiller':
            flash('Başarıyla giriş yapıldı!', 'success')
            return redirect(url_for('admin_home'))
        else:
            flash('Kullanıcı adı veya şifre yanlış!', 'danger')
    return render_template('admin_login_page.html')

@app.route('/menu')
def show_menu():
    menus = Menu.query.all()  # Tüm menüleri getir
    return render_template('index.html', menus=menus)


@app.route('/admin/home')
def admin_home():
    return render_template('admin_home.html')

@app.route('/manage_menu', methods=['GET'])
def manage_menu():
    filter_menu_id = request.args.get('filter_menu_id')
    if filter_menu_id:
        menu_items = MenuItem.query.filter_by(menu_id=filter_menu_id).all()
    else:
        menu_items = MenuItem.query.all()

    menus = Menu.query.all()
    return render_template('manage_menu.html', menu_items=menu_items, menus=menus)


@app.route('/manage_tables')
def manage_tables():
    return render_template('manage_tables.html')

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    name = request.form['name']
    price = request.form['price']
    menu_id = request.form['menu_id']
    # Menü öğesini veritabanına ekle
    new_item = MenuItem(name=name, price=price, menu_id=menu_id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('manage_menu'))

@app.route('/initialize_menus')
def initialize_menus():
    menus = ["Sıcak İçecekler", "Soğuk İçecekler", "Tatlılar"]
    for menu_name in menus:
        if not Menu.query.filter_by(name=menu_name).first():
            new_menu = Menu(name=menu_name)
            db.session.add(new_menu)
    db.session.commit()
    return "Menüler başarıyla oluşturuldu!"


@app.route('/delete_menu_item/<int:item_id>')
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Ürün başarıyla silindi!', 'success')
    return redirect(url_for('manage_menu'))

@app.route('/manage_orders')
def manage_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    for order in orders:
        if isinstance(order.details, str):
            order.details = json.loads(order.details)
    return render_template('manage_orders.html', orders=orders)

@app.route('/complete_order/<int:order_id>')
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)

    try:
        if isinstance(order.details, str):
            order.details = json.loads(order.details)

        completed_order = CompletedOrder(
            table_number=order.table_number,
            details=order.details,
            total_price=order.total_price
        )
        db.session.add(completed_order)
        db.session.delete(order)
        db.session.commit()

        flash('Sipariş başarıyla tamamlandı!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Sipariş tamamlanırken bir hata oluştu: {str(e)}', 'danger')

    return redirect(url_for('manage_orders'))

@app.route('/sicak-icecekler')
def sicak_icecekler():
    # SQLAlchemy kullanarak menu_id = 1 olanları al
    menu_items = MenuItem.query.filter_by(menu_id=1).all()
    return render_template('sicak-icecekler.html', menu_items=menu_items)

@app.route('/soguk-icecekler')
def soguk_icecekler():
    menu_items = MenuItem.query.filter_by(menu_id=2).all()
    return render_template('soguk-icecekler.html', menu_items=menu_items)

@app.route('/tatlilar')
def tatlilar():
    menu_items = MenuItem.query.filter_by(menu_id=3).all()
    return render_template('tatlilar.html', menu_items=menu_items)


@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Sipariş başarıyla iptal edildi!', 'danger')
    return redirect(url_for('manage_orders'))

@app.route('/add_order', methods=['POST'])
def add_order():
    data = request.get_json()
    table_number = data.get('table_number')
    details = data.get('details')

    if not table_number or not details:
        return jsonify({"error": "Masa numarası ve sipariş detayları zorunludur."}), 400

    new_order = Order(
        table_number=table_number,
        details=details,
        status='Bekliyor'
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "Sipariş başarıyla kaydedildi."}), 201

@app.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.get_json()
    table_number = data.get('table_number')
    cart = data.get('details')

    if not table_number or not cart:
        return jsonify({'message': 'Eksik bilgi! Masa numarası ve ürün bilgileri gerekli.'}), 400

    try:
        new_order = Order(
            table_number=table_number,
            details=cart,
            status='Bekliyor',
        )
        db.session.add(new_order)
        db.session.commit()

        return jsonify({'message': 'Sipariş başarıyla kaydedildi!', 'total_price': new_order.total_price}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Hata oluştu: {str(e)}'}), 500

@app.route('/api/completed_orders')
def get_completed_orders():
    completed_orders = CompletedOrder.query.order_by(CompletedOrder.completed_at.desc()).all()
    data = [
        {
            "id": order.id,
            "table_number": order.table_number,
            "details": json.loads(order.details) if isinstance(order.details, str) else order.details,
            "total_price": order.total_price,
            "completed_at": order.completed_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for order in completed_orders
    ]
    return jsonify(data)


@app.route('/api/delete_table', methods=['POST'])
def delete_table():
    data = request.get_json()
    table_number = data.get('table_number')

    if not table_number:
        return jsonify({"error": "Masa numarası belirtilmedi."}), 400

    try:
        # İlgili masa numarasına ait siparişleri sil
        orders = CompletedOrder.query.filter_by(table_number=table_number).all()
        for order in orders:
            db.session.delete(order)
        db.session.commit()
        return jsonify({"message": f"Masa {table_number} başarıyla silindi."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Hata oluştu: {str(e)}"}), 500

@app.route('/api/orders')
def get_orders():
    orders = get_all_orders()  # Veritabanınızdan tüm siparişleri döndürür
    return jsonify(orders)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
