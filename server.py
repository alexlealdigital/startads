from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# 🔹 Configuração do Firebase
cred = credentials.Certificate("firebase_key.json")  # Seu arquivo de credenciais do Firebase
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://SEU_PROJETO.firebaseio.com/"  # Substituir pelo seu URL do Firebase
})

# 🔹 Função para carregar anúncios do Firebase
def load_ads():
    ref = db.reference("ads")
    ads = ref.get()
    return ads if ads else []

# 🔹 Função para salvar anúncios no Firebase
def save_ad(image, link, description):
    ref = db.reference("ads")
    new_ad = {
        "id": ref.push().key,  # 🔹 Gera um ID único para cada anúncio
        "image": image,
        "link": link,
        "description": description
    }
    ref.child(new_ad["id"]).set(new_ad)
    return new_ad

# 🔹 Rota para listar os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ads = load_ads()
    return jsonify(ads), 200

# 🔹 Rota para adicionar um novo anúncio
@app.route("/ads", methods=["POST"])
def add_ad():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    image = data.get("image")
    link = data.get("link")
    description = data.get("description")

    if not image or not link or not description:
        return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    new_ad = save_ad(image, link, description)

    return jsonify({"message": "Anúncio salvo com sucesso!", "ad": new_ad}), 201

# 🔹 Teste da API
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando com Firebase!"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
