from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "ads.db"

# Inicializa o banco de dados SQLite
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS anuncios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image TEXT,
                link TEXT,
                description TEXT
            )
        """)
        conn.commit()
        conn.close()

init_db()

# Rota de teste (Hello, World!)
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})

# Rota para listar os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM anuncios")
    ads = cursor.fetchall()
    conn.close()

    ad_list = [{"id": row[0], "image": row[1], "link": row[2], "description": row[3]} for row in ads]
    return jsonify(ad_list)

# Rota para adicionar um novo anúncio
@app.route("/ads", methods=["POST"])
def add_ad():
    data = request.json
    image = data.get("image")
    link = data.get("link")
   
