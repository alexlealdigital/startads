import os
import json
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify

# 🔹 Inicializa o Flask
app = Flask(__name__)

# 🔹 Obtém a chave do Firebase a partir da variável de ambiente
firebase_config = os.environ.get("FIREBASE_KEY")

if firebase_config:
    try:
        # 🔹 Converte a string JSON da variável de ambiente em um dicionário
        cred_dict = json.loads(firebase_config)
        
        # 🔹 Cria um arquivo temporário para armazenar a chave do Firebase
        temp_key_file = "firebase_key_temp.json"
        with open(temp_key_file, "w") as f:
            json.dump(cred_dict, f)

        # 🔹 Inicializa o Firebase usando o arquivo temporário
        cred = credentials.Certificate(temp_key_file)
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
        })

        # 🔹 Remove o arquivo temporário após a inicialização
        os.remove(temp_key_file)

        print("✅ Firebase inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar o Firebase: {e}")
        exit(1)
else:
    print("❌ Erro: Chave do Firebase não encontrada. Configure a variável FIREBASE_KEY.")
    exit(1)  # Finaliza o programa se a chave não for encontrada

# 🔹 Rota raiz para testar se a API está funcionando
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API está rodando!"}), 200

# 🔹 Rota para obter todos os anúncios
@app.route("/ads", methods=["GET"])
def get_ads():
    try:
        ref = db.reference("ads")  # Referência ao nó 'ads' no Firebase
        ads = ref.get()  # Obtém os anúncios

        if not ads:
            return jsonify([]), 200  # Retorna uma lista vazia se não houver anúncios

        # 🔹 Converte os anúncios para lista
        ads_list = [{"id": key, **value} for key, value in ads.items()]
        return jsonify(ads_list), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao buscar anúncios: {str(e)}"}), 500

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

        ref = db.reference("ads")  # Referência ao nó 'ads' no Firebase
        new_ad_ref = ref.push()  # Cria um novo registro

        # 🔹 Estrutura do novo anúncio
        new_ad = {
            "image": image,
            "link": link,
            "description": description
        }

        new_ad_ref.set(new_ad)  # Salva no Firebase

        return jsonify({"message": "Anúncio salvo com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": f"Erro ao salvar anúncio: {str(e)}"}), 500

# 🔹 Inicia o servidor Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Define a porta
    app.run(host="0.0.0.0", port=port, debug=True)
