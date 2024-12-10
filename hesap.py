from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Flask uygulaması oluştur
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mevcut tablolar
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

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

# Yeni tablo tanımı
class CompletedOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    details = db.Column(db.JSON, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tabloları oluştur
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tablolar başarıyla oluşturuldu.")

