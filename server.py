from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json
import requests
from datetime import datetime

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

# 🔹 Rota para testar se a API está rodando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# 🔹 Rota para buscar todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    ref = db.reference("ads")
    ads = ref.get()
    return jsonify(list(ads.values()) if ads else []), 200

# 🔹 Rota para adicionar um novo anúncio (valida código antes)
@app.route("/ads", methods=["POST"])
def add_ad():
    try:
        if request.content_type.startswith('multipart/form-data'):
            image_file = request.files.get('image')
            link = request.form.get('link')
            description = request.form.get('description')
            code = request.form.get('code')

            if not image_file or not link or not description or not code:
                return jsonify({"error": "Todos os campos são obrigatórios"}), 400

            # Faz o upload da imagem para o Imgur
            headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
            files = {"image": (image_file.filename, image_file.stream, image_file.mimetype)}
            response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files)

            if response.status_code != 200:
                return jsonify({"error": "Erro ao enviar imagem para o Imgur"}), 500

            image_url = response.json()["data"]["link"]

            # Salva os dados no Firebase
            ref = db.reference("ads")
            new_ad = ref.push({
                "image": image_url,
                "link": link,
                "description": description,
                "created_at": datetime.now().isoformat()
            })

            return jsonify({"message": "Anúncio salvo com sucesso!", "id": new_ad.key}), 201
        else:
            return jsonify({"error": "Tipo de conteúdo inválido. Use multipart/form-data."}), 415
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

        ref = db.reference("codes")
        codes = ref.get()
        if codes:
            for key, value in codes.items():
                if value.get("code") == code and value.get("valid", False):
                    ref.child(key).update({"valid": False})  # Invalida o código
                    return jsonify({"message": "Código válido!"}), 200
        return jsonify({"error": "Código inválido ou já utilizado"}), 400
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
