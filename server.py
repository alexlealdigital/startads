from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json

app = Flask(__name__)

# 🔹 Configuração do Firebase
firebase_config = os.environ.get("FIREBASE_KEY")

if firebase_config:
    cred = credentials.Certificate(json.loads(firebase_config))
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
    })
else:
    print("❌ Erro: Chave do Firebase não encontrada. Configure a variável FIREBASE_KEY.")
    exit(1)  # Finaliza a execução caso não encontre a chave

# 🔹 Rota de teste para ver se a API está rodando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando com Firebase!"}), 200

# 🔹 Rota para listar todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ref = db.reference("ads")
    ads = ref.get()
    
    if ads is None:
        return jsonify([]), 200  # Retorna uma lista vazia se não houver anúncios

    return jsonify(ads), 200

# 🔹 Rota para adicionar um novo anúncio
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

        ref = db.reference("ads")
        new_ad_ref = ref.push()  # Cria um novo ID único no Firebase
        new_ad = {
            "id": new_ad_ref.key,  # ID gerado automaticamente pelo Firebase
            "image": image,
            "link": link,
            "description": description
        }
        new_ad_ref.set(new_ad)  # Salva os dados no Firebase

        return jsonify({"message": "Anúncio salvo com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Usa a porta definida no Render ou a 10000
    app.run(host="0.0.0.0", port=port, debug=True)
