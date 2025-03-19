from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json

app = Flask(__name__)

# 🔹 Configuração do Firebase (usando variável de ambiente do Render)
firebase_key_json = os.environ.get("FIREBASE_KEY")

if firebase_key_json:
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)

    # 🔹 Evita múltiplas inicializações do Firebase
    if not firebase_admin._apps:
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

# 🔹 Função para verificar se o código de pagamento é válido
def is_valid_code(code):
    ref = db.reference("codes")
    code_exists = ref.child(code).get()
    return code_exists is not None  # Retorna True se o código existir no Firebase

# 🔹 Função para remover o código do Firebase após o uso
def remove_code(code):
    ref = db.reference("codes")
    ref.child(code).delete()

# 🔹 Rota para testar se a API está rodando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# 🔹 Rota para buscar todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ads = load_ads()
    return jsonify(ads), 200

# 🔹 Rota para validar o código antes de permitir envio de anúncio
@app.route("/validate-code", methods=["POST"])
def validate_code():
    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"error": "Código não fornecido."}), 400

    if is_valid_code(code):
        return jsonify({"message": "Código válido!"}), 200
    else:
        return jsonify({"error": "Código inválido ou já usado."}), 400

# 🔹 Rota para adicionar um novo anúncio (agora exige um código válido)
@app.route("/ads", methods=["POST"])
def add_ad():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400

        code = data.get("code")  # Novo campo obrigatório
        image = data.get("image")
        link = data.get("link")
        description = data.get("description")

        if not code or not image or not link or not description:
