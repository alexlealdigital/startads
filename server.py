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
def validate_and_invalidate_code(code):
    ref = db.reference("codes")
    
    try:
        # Busca o código específico
        query = ref.order_by_child("code").equal_to(code).get()
        
        if not query:
            return False
            
        for key, value in query.items():
            if isinstance(value, dict) and value.get("valid", False):
                # SOLUÇÃO DEFINITIVA - Atualização direta no caminho completo
                db.reference(f"codes/{key}/valid").set(False)
                return True
                
        return False
        
    except Exception as e:
        print(f"Erro ao invalidar código: {str(e)}")
        return False

# 🔹 Função para fazer upload da imagem para o Imgur
def upload_to_imgur(image_url):
    try:
        with open(image_url, "rb") as image_file:
            headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
            files = {"image": image_file}
            response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files)

            if response.status_code == 200:
                return response.json()["data"]["link"]
            else:
                print(f"❌ Erro ao enviar imagem: {response.json()}")
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

        image = data.get("image")
        link = data.get("link")
        description = data.get("description")
        payment_code = data.get("code")

        if not image or not link or not description or not payment_code:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        # 🔹 Verificar código de pagamento
        if not validate_code(payment_code):
            return jsonify({"error": "Código inválido ou já utilizado"}), 400

        # 🔹 Fazer upload da imagem para Imgur antes de salvar no Firebase
        uploaded_image_url = upload_to_imgur(image)
        if not uploaded_image_url:
            return jsonify({"error": "Falha ao fazer upload da imagem"}), 500

        # 🔹 Salvar anúncio no Firebase
        ref = db.reference("ads")
        new_ad_ref = ref.push({
            "image": uploaded_image_url,
            "link": link,
            "description": description
        })

        return jsonify({"message": "Anúncio salvo com sucesso!", "id": new_ad_ref.key}), 201

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
            ref.child(code).set(True)

        return jsonify({"message": "Códigos adicionados com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
