from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json
import requests

app = Flask(__name__)

# 🔹 Configuração do Firebase (usando variável de ambiente do Render)
firebase_key_json = os.environ.get("FIREBASE_KEY")

if firebase_key_json:
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
    })
else:
    print("❌ ERRO: Variável FIREBASE_KEY não encontrada.")
    exit(1)

# 🔹 Configuração do Imgur
IMGUR_CLIENT_ID = "8823fb7cd2338d3"
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/upload"

# 🔹 Função para carregar anúncios do Firebase
def load_ads():
    ref = db.reference("ads")
    ads = ref.get()
    return list(ads.values()) if ads else []

# 🔹 Função para verificar código de pagamento
def validate_code(code):
    ref = db.reference("codes")
    codes = ref.get()
    if codes:
        for key, value in codes.items():
            if value.get("code") == code and value.get("valid", False):
                ref.child(key).update({"valid": False})  # Invalida o código
                return True
    return False

# 🔹 Função para fazer upload da imagem para o Imgur
def upload_to_imgur(image_path):
    try:
        with open(image_path, "rb") as image_file:
            headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
            files = {"image": image_file}
            response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files)

            if response.status_code == 200:
                return response.json()["data"]["link"]
            else:
                print(f"❌ Erro ao enviar imagem para Imgur: {response.json()}")
                return None
    except Exception as e:
        print(f"❌ Erro inesperado ao enviar imagem: {e}")
        return None

# 🔹 Rota para testar se a API está rodando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# 🔹 Rota para buscar todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ads = load_ads()
    return jsonify(ads), 200

# 🔹 Rota para adicionar um novo anúncio (valida código antes)
@app.route("/ads", methods=["POST"])
def add_ad():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400

        image_path = data.get("image")  # caminho local da imagem
        link = data.get("link")
        description = data.get("description")
        code = data.get("code")

        if not image_path or not link or not description or not code:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        if not validate_code(code):
            return jsonify({"error": "Código inválido ou já utilizado"}), 400

        image_url = upload_to_imgur(image_path)
        if not image_url:
            return jsonify({"error": "Erro ao fazer upload da imagem"}), 500

        ref = db.reference("ads")
        new_ad = ref.push({
            "image": image_url,
            "link": link,
            "description": description
        })

        return jsonify({"message": "Anúncio salvo com sucesso!", "id": new_ad.key}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Rota para adicionar novos códigos de pagamento ao Firebase
@app.route("/add_codes", methods=["POST"])
def add_codes():
    try:
        data = request.get_json()
        codes = data.get("codes")

        if not codes or not isinstance(codes, list):
            return jsonify({"error": "Formato inválido. Deve ser uma lista de códigos."}), 400

        ref = db.reference("codes")
        for code in codes:
            ref.push({"code": code, "valid": True})

        return jsonify({"message": "Códigos adicionados com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Rota para validar código separadamente (opcional para o app)
@app.route("/validate_code", methods=["POST"])
def validate_code_route():
    try:
        data = request.get_json()
        code = data.get("code")
        if not code:
            return jsonify({"error": "Código não informado"}), 400

        if validate_code(code):
            return jsonify({"message": "Código válido!"}), 200
        else:
            return jsonify({"error": "Código inválido ou já utilizado"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
