from flask import Flask, request, jsonify
import requests
import time
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa o Firebase
cred = credentials.Certificate('caminho/para/sua/chave-firebase.json')  # Substitua pelo caminho da sua chave
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

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

    # Lógica para salvar os dados no Firebase
    ad_data = {
        'description': description,
        'image': image_url,
        'link': link,
        'code': code
    }

    try:
        # Adiciona os dados ao Firestore
        db.collection('ads').add(ad_data)
    except Exception as e:
        return jsonify({"error": f"Erro ao salvar no Firebase: {str(e)}"}), 500

    return jsonify({"message": "Anúncio criado com sucesso!", "data": ad_data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
