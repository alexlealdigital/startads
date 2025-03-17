from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DB_FILE = "ads.json"

# Função para carregar os anúncios do JSON
def load_ads():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)
    
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Função para salvar os anúncios no JSON
def save_ads(ads):
    with open(DB_FILE, "w") as f:
        json.dump(ads, f, indent=4)

# Rota raiz para testar se a API está rodando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# Rota para listar os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ads = load_ads()
    return jsonify(ads), 200

# Rota para adicionar um novo anúncio
@app.route("/ads", methods=["POST"])
def add_ad():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Requisição sem dados"}), 400

        image = data.get("image")
        link = data.get("link")
        description = data.get("description")

        if not image or not link or not description:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        ads = load_ads()
        new_ad = {
            "id": len(ads) + 1,
            "image": image,
            "link": link,
            "description": description
        }
        ads.append(new_ad)
        save_ads(ads)

        return jsonify({"message": "Anúncio salvo com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Corrigindo a porta
    app.run(host="0.0.0.0", port=port, debug=True)
