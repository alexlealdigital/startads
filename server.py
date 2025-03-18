import os
import json
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify

# 🔹 Configurações do Firebase
firebase_config = os.environ.get("FIREBASE_KEY")

if firebase_config:
    cred = credentials.Certificate(json.loads(firebase_config))
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
    })
else:
    print("❌ Erro: Chave do Firebase não encontrada. Configure a variável FIREBASE_KEY.")
    exit(1)

# 🔹 Inicializa o Flask
app = Flask(__name__)

# 🔹 Função para buscar todos os anúncios do Firebase
def load_ads():
    ref = db.reference("/ads")
    ads = ref.get()

    if ads is None:
        return []  # Se não houver anúncios, retorna lista vazia
    else:
        return [{"id": key, **value} for key, value in ads.items()]  # 🔹 Inclui o ID único do Firebase

# 🔹 Função para salvar um novo anúncio sem sobrescrever os antigos
def save_ad(data):
    ref = db.reference("/ads")  # 🔹 Caminho correto no banco de dados
    new_ad_ref = ref.push()  # 🔹 Garante que cada anúncio é único
    new_ad_ref.set(data)  # 🔹 Salva o anúncio no Firebase

# 🔹 Rota raiz para testar a API
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# 🔹 Rota para listar os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ads = load_ads()
    return jsonify(ads), 200

# 🔹 Rota para adicionar um novo anúncio sem apagar os anteriores
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

        new_ad = {
            "image": image,
            "link": link,
            "description": description
        }

        save_ad(new_ad)  # 🔹 Agora os anúncios são adicionados corretamente

        return jsonify({"message": "Anúncio salvo com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Rota para deletar um anúncio por ID (opcional)
@app.route("/ads/<ad_id>", methods=["DELETE"])
def delete_ad(ad_id):
    try:
        ref = db.reference(f"/ads/{ad_id}")
        if ref.get() is None:
            return jsonify({"error": "Anúncio não encontrado"}), 404
        
        ref.delete()
        return jsonify({"message": "Anúncio deletado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Iniciar servidor Flask na porta correta
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
