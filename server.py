from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os
import json
import requests
from datetime import datetime
import time

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

# 🔹 Função para fazer upload da imagem para o Imgur
def upload_to_imgur(image_file):
    try:
        headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
        files = {"image": (image_file.filename, image_file.stream, image_file.mimetype)}
        response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files)

        if response.status_code == 200:
            return response.json()["data"]["link"]
        elif response.status_code == 429:  # Too Many Requests
            print("❌ Limite de requisições excedido no Imgur. Aguardando 10 segundos...")
            time.sleep(10)  # Aguarda 10 segundos antes de tentar novamente
            return upload_to_imgur(image_file)  # Tenta novamente
        else:
            print(f"❌ Erro ao enviar imagem para Imgur: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro inesperado ao enviar imagem: {e}")
        return None

# 🔹 Rota para adicionar um novo anúncio
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
            image_url = upload_to_imgur(image_file)
            if not image_url:
                return jsonify({"error": "Erro ao fazer upload da imagem"}), 500

            # Salva os dados no Firebase
            ref = db.reference("ads")
            new_ad = ref.push({
                "image": image_url,
                "link": link,
                "description": description,
                "created_at": datetime.now().isoformat()  # Adiciona a data de criação
            })

            return jsonify({"message": "Anúncio salvo com sucesso!", "id": new_ad.key}), 201

        else:
            return jsonify({"error": "Tipo de conteúdo inválido. Use multipart/form-data."}), 415

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
