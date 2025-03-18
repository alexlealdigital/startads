import requests
import json
import os
import firebase_admin
from firebase_admin import credentials, db
from tkinter import Tk, filedialog
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "API está rodando!"

# 🔹 Configurações do Imgur
IMGUR_CLIENT_ID = "8823fb7cd2338d3"
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/upload"

# 🔹 Carregar chave do Firebase do ambiente
firebase_key_json = os.environ.get("FIREBASE_KEY")

if firebase_key_json:
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
    })
else:
    print("❌ ERRO: A variável de ambiente FIREBASE_KEY não foi encontrada.")
    exit(1)

# 📌 Função para selecionar imagem
def select_image():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
    return file_path

# 📌 Função para fazer upload da imagem para o Imgur
def upload_to_imgur(image_path):
    try:
        with open(image_path, "rb") as image_file:
            headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
            files = {"image": image_file}
            response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files)
            
            if response.status_code == 200:
                return response.json()["data"]["link"]
            else:
                print(f"❌ Erro no Imgur: {response.status_code} - {response.json()}")
                return None
    except Exception as e:
        print(f"❌ Erro inesperado ao enviar imagem: {e}")
        return None

# 📌 Função para salvar anúncio no Firebase
def save_to_firebase(image_url, description, link):
    try:
        ref = db.reference("ads")
        ref.push({
            "image": image_url,
            "description": description,
            "link": link
        })
        print("✅ Anúncio salvo no Firebase com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar no Firebase: {e}")

# 🚀 Fluxo do Programa
def main():
    print("📌 Selecione uma imagem para o anúncio")
    image_path = select_image()
    
    if not image_path:
        print("❌ Nenhuma imagem selecionada.")
        return
    
    print("⏳ Fazendo upload para o Imgur...")
    image_url = upload_to_imgur(image_path)
    
    if not image_url:
        print("❌ Falha ao obter URL da imagem. Encerrando processo.")
        return
    
    description = input("📝 Digite a descrição do anúncio (máx. 55 caracteres): ")[:55]
    link = input("🔗 Digite o link do botão: ")
    
    print("⏳ Salvando anúncio no Firebase...")
    save_to_firebase(image_url, description, link)
    
    print(f"🎉 Anúncio criado com sucesso! \n🖼 {image_url} \n📝 {description} \n🔗 {link}")

if __name__ == "__main__":
    main()
