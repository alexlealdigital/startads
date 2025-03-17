from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Define o caminho do banco de dados SQLite
DB_PATH = "ads.db"

# Função para inicializar o banco de dados e a tabela
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

# Inicializa o banco de dados ao iniciar o servidor
init_db()

# Rota para obter todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM anuncios")
    ads = cursor.fetchall()
    conn.close()

    # Transforma os resultados em uma lista de dicionários
    ad_list = [{"id": row[0], "image": row[1], "link": row[2], "description": row[3]} for row in ads]
    return jsonify(ad_list)

# Rota para adicionar um novo anúncio
@app.route("/ads", methods=["POST"])
def add_ad():
    data = request.json
    image = data.get("image")
    link = data.get("link")
    description = data.get("description")

    if not image or not link or not description:
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO anuncios (image, link, description) VALUES (?, ?, ?)", (image, link, description))
    conn.commit()
    conn.close()

    return jsonify({"message": "Anúncio salvo com sucesso!"})

# Iniciar o servidor Flask
if __name__ == "__main__":
    app.run(port=5000, debug=True)
