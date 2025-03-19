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

# 🔹 Função para carregar os anúncios do Firebase
def load_ads():
    ref = db.reference("ads")
    ads = ref.get()
    return list(ads.values()) if ads else []  # Retorna lista vazia se não houver anúncios

# 🔹 Rota para testar se a API está rodando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# 🔹 Rota para buscar todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ads = load_ads()
    return jsonify(ads), 200

# 🔹 Rota para adicionar um novo anúncio (verifica código antes)/////////////////////////////////////////////////
@app.route("/validate_code", methods=["POST"])
def validate_code():
    data = request.get_json()
    user_code = data.get("code")

    if not user_code:
        return jsonify({"error": "Código não fornecido"}), 400

    # Referência ao banco de dados
    codes_ref = db.reference("codes")
    codes_data = codes_ref.get()

    if not codes_data:
        return jsonify({"error": "Nenhum código encontrado"}), 404

    # Verifica se o código existe dentro de algum dos registros
    for key, value in codes_data.items():
        if value.get("code") == user_code and value.get("valid", False):
            # Código encontrado, marcamos como inválido (já utilizado)
            codes_ref.child(key).update({"valid": False})
            return jsonify({"message": "Código válido!", "status": "success"}), 200

    return jsonify({"error": "Código inválido ou já utilizado"}), 400


# 🔹 Rota para adicionar códigos de pagamento ao Firebase//////////////////////////////////////////////////////////////////
@app.route("/add_codes", methods=["POST"])
def add_codes():
    try:
        data = request.get_json()
        codes = data.get("codes", [])

        if not codes:
            return jsonify({"error": "Nenhum código fornecido"}), 400

        codes_ref = db.reference("codes")

        for code in codes:
            codes_ref.child(code).set(True)  # Salva o código no Firebase

        return jsonify({"message": "✅ Códigos adicionados com sucesso!", "codes": codes}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
