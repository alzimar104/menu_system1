# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime

# # Flask uygulaması oluştur
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # Mevcut tablolar
# class MenuItem(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     price = db.Column(db.Float, nullable=False)

# class Order(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     table_number = db.Column(db.Integer, nullable=False)
#     details = db.Column(db.JSON, nullable=False)
#     status = db.Column(db.String(50), nullable=False, default='Bekliyor')

#     @property
#     def total_price(self):
#         if not self.details:
#             return 0.0
#         return sum(item['price'] * item['quantity'] for item in self.details)

# # Yeni tablo tanımı
# class CompletedOrder(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     table_number = db.Column(db.Integer, nullable=False)
#     details = db.Column(db.JSON, nullable=False)
#     total_price = db.Column(db.Float, nullable=False)
#     completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# # Tabloları oluştur
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         print("Tablolar başarıyla oluşturuldu.")



from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Veritabanına bağlan
engine = create_engine('sqlite:///instance/restaurant.db')
Base = declarative_base()

# Menü Tablosunu Tanımla
class Menu(Base):
    __tablename__ = 'menus'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

# Tabloyu oluştur
Base.metadata.create_all(engine)

# Oturum oluştur
Session = sessionmaker(bind=engine)
session = Session()

# Menüleri ekle
menus = ["Sıcak İçecekler", "Soğuk İçecekler", "Tatlılar"]
for menu_name in menus:
    menu = Menu(name=menu_name)
    session.add(menu)

# Değişiklikleri kaydet
session.commit()

# Eklenen menüleri kontrol et
added_menus = session.query(Menu).all()
for menu in added_menus:
    print(f"Menü ID: {menu.id}, Menü Adı: {menu.name}")

