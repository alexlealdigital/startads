from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json

app = Flask(__name__)

# 🔹 Configuração do Firebase (usando variável de ambiente do Render)
firebase_key_json = os.environ.get("FIREBASE_KEY")

if firebase_key_json:
    cred_dict = json.loads(firebase_key_json)  # Converte JSON para dicionário
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
    })
else:
    print("❌ ERRO: Variável FIREBASE_KEY não encontrada.")
    exit(1)

# 🔹 Referências do Firebase
ads_ref = db.reference("ads")  # Banco de anúncios
codes_ref = db.reference("codes")  # Banco de códigos PIX

# 🔹 Função para carregar os anúncios do Firebase
def load_ads():
    ads = ads_ref.get()
    return list(ads.values()) if ads else []

# 🔹 Função para carregar os códigos PIX válidos
def load_valid_codes():
    codes = codes_ref.get()
    return set(codes.keys()) if codes else set()  # Retorna um conjunto de códigos válidos

# 🔹 Rota para testar se a API está rodando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# 🔹 Rota para buscar todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ads = load_ads()
    return jsonify(ads), 200

# 🔹 Rota para validar código PIX
@app.route("/validate_code", methods=["POST"])
def validate_code():
    data = request.get_json()
    code = data.get("code")

    valid_codes = load_valid_codes()

    if code in valid_codes:
        codes_ref.child(code).delete()  # Remove código do Firebase
        return jsonify({"message": "✅ Código válido! Envio liberado."}), 200
    return jsonify({"error": "❌ Código inválido ou já utilizado!"}), 400

# 🔹 Rota para adicionar um novo anúncio (AGORA COM CÓDIGO PIX)
@app.route("/ads", methods=["POST"])
def add_ad():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400

        code = data.get("code")  # Código PIX fornecido pelo usuário
        image = data.get("image")
        link = data.get("link")
        description = data.get("description")

        if not code or not image or not link or not description:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        valid_codes = load_valid_codes()
        if code not in valid_codes:
            return jsonify({"error": "❌ Código inválido ou já utilizado!"}), 400

        # 🔹 Remove código PIX após uso
        codes_ref.child(code).delete()

        # 🔹 Salva o anúncio no Firebase
        new_ad_ref = ads_ref.push({
            "image": image,
            "link": link,
            "description": description
        })

        return jsonify({"message": "✅ Anúncio salvo com sucesso!", "id": new_ad_ref.key}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
