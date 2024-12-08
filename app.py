from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, MenuItem, Order
from forms import LoginForm

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def admin_login_page():
    return render_template('admin_login_page.html')  # İlk giriş sayfası

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Kullanıcı adı ve şifre kontrolü
        if username == 'mcstone' and password == 'thekiller':
            flash('Başarıyla giriş yapıldı!', 'success')
            return redirect(url_for('admin_home'))  # Giriş sonrası yönlendirme
        else:
            flash('Kullanıcı adı veya şifre yanlış!', 'danger')  
    return render_template('admin_login_page.html')  # Başarısız login durumunda

# Admin ana sayfası
@app.route('/admin/home')
def admin_home():
    return render_template('admin_home.html')  # Admin paneli ana sayfası

@app.route('/manage_menu')
def manage_menu():
    # Menü öğelerini veritabanından al
    menu_items = MenuItem.query.all()
    return render_template('manage_menu.html', menu_items=menu_items)

@app.route('/add_menu_item', methods=['POST'])
def add_menu_item():
    name = request.form.get('name')
    price = request.form.get('price')
    
    # Yeni ürün ekle
    new_item = MenuItem(name=name, price=price)
    db.session.add(new_item)
    db.session.commit()

    # Flash mesajı ve yönlendirme
    flash('Yeni ürün başarıyla eklendi!', 'success')
    return redirect(url_for('manage_menu'))

@app.route('/delete_menu_item/<int:item_id>')
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Ürün silindi!', 'success')
    return redirect(url_for('manage_menu'))

@app.route('/manage_orders')
def manage_orders():
    orders = Order.query.all()
    return render_template('manage_orders.html', orders=orders)

@app.route('/add_order', methods=['POST'])
def add_order():
    table_number = request.form.get('table_number')
    details = request.form.get('details')
    new_order = Order(table_number=table_number, details=details, status='Bekliyor')
    db.session.add(new_order)
    db.session.commit()
    flash('Sipariş başarıyla kaydedildi!', 'success')
    return redirect(url_for('manage_orders'))

@app.route('/complete_order/<int:order_id>')
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'Tamamlandı'
    db.session.commit()
    flash('Sipariş tamamlandı!', 'success')
    return redirect(url_for('manage_orders'))

@app.route('/cancel_order/<int:order_id>')
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Sipariş iptal edildi!', 'danger')
    return redirect(url_for('manage_orders'))

if __name__ == '__main__':
    app.run(debug=True)
