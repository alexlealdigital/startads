from flask import Flask, request, jsonify
import requests
import time
import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Inicializa o Firebase
def initialize_firebase():
    # Carrega a chave do Firebase a partir da variável de ambiente
    firebase_key = os.getenv('FIREBASE_KEY')
    if not firebase_key:
        raise ValueError("A variável de ambiente FIREBASE_KEY não está configurada.")

    try:
        # Converte a chave de string JSON para um dicionário
        firebase_key_dict = json.loads(firebase_key)

        # Configura o Firebase
        cred = credentials.Certificate(firebase_key_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://adsdados-default-rtdb.firebaseio.com/'  # URL do Realtime Database
        })
    except json.JSONDecodeError as e:
        raise ValueError("A chave do Firebase não é um JSON válido.") from e
    except ValueError as e:
        raise ValueError(f"Erro ao carregar a chave do Firebase: {str(e)}") from e

initialize_firebase()

app = Flask(__name__)

# Rota para a URL raiz
@app.route('/')
def index():
    return "Servidor Flask está rodando! 🚀"

# Substitua pelo seu Client-ID do Imgur
IMGUR_CLIENT_ID = '8823fb7cd2338d3'

@app.route('/ads', methods=['POST'])
def create_ad():
    # Verifica se todos os campos obrigatórios estão presentes
    required_fields = ['description', 'image', 'link', 'code']
    for field in required_fields:
        if field not in request.form:
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

    description = request.form['description']
    image_url = request.form['image']
    link = request.form['link']
    code = request.form['code']

    # Lógica para enviar a imagem para o Imgur
    try:
        # Envia a imagem para o Imgur
        headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
        data = {'image': image_url}
        response = requests.post(
            'https://api.imgur.com/3/upload',
            headers=headers,
            data=data
        )

        # Verifica se o limite de requisições foi excedido
        if response.status_code == 429:
            time.sleep(10)  # Aguarda 10 segundos antes de tentar novamente
            response = requests.post(
                'https://api.imgur.com/3/upload',
                headers=headers,
                data=data
            )

        # Verifica se a requisição foi bem-sucedida
        response.raise_for_status()
        imgur_data = response.json()
        image_url = imgur_data['data']['link']  # URL da imagem no Imgur
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"Erro ao enviar imagem para o Imgur: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500

    # Lógica para salvar os dados no Firebase Realtime Database
    ad_data = {
        'description': description,
        'image': image_url,
        'link': link,
        'code': code
    }

    try:
        # Salva os dados no Realtime Database
        ref = db.reference('ads')  # Referência para o nó 'ads'
        new_ad_ref = ref.push()  # Cria um novo nó com um ID único
        new_ad_ref.set(ad_data)  # Adiciona os dados ao nó
    except Exception as e:
        return jsonify({"error": f"Erro ao salvar no Firebase: {str(e)}"}), 500

    return jsonify({"message": "Anúncio criado com sucesso!", "data": ad_data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
