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

# Rota para listar os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM anuncios")
    ads = cursor.fetchall()
    conn.close()

    ad_list = [{"id": row[0], "image": row[1], "link": row[2], "description": row[3]} for row in ads]
    return jsonify(ad_list), 200

# Rota para adicionar um novo anúncio
@app.route("/ads", methods=["POST"])
def add_ad():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Requisição sem dados"}), 400  # Retorno correto

        image = data.get("image")
        link = data.get("link")
        description = data.get("description")

        if not image or not link or not description:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400  # Retorno correto

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO anuncios (image, link, description) VALUES (?, ?, ?)", (image, link, description))
        conn.commit()
        conn.close()

        return jsonify({"message": "Anúncio salvo com sucesso!"}), 201  # Retorno correto

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Retorno correto

if __name__ == "__main__":
    app.run(debug=True)
