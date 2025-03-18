import requests
import json
import firebase_admin
from firebase_admin import credentials, db
from tkinter import Tk, filedialog

# 🔹 Configurações do Imgur
IMGUR_CLIENT_ID = "8823fb7cd2338d3"
IMGUR_UPLOAD_URL = "https://api.imgur.com/3/upload"

# 🔹 Configuração do Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
})

# 📌 Função para selecionar imagem
def select_image():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
    return file_path

# 📌 Função para fazer upload da imagem para o Imgur
def upload_to_imgur(image_path):
    with open(image_path, "rb") as image_file:
        headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
        files = {"image": image_file}
        response = requests.post(IMGUR_UPLOAD_URL, headers=headers, files=files)
        
        if response.status_code == 200:
            return response.json()["data"]["link"]
        else:
            print("❌ Erro ao enviar imagem para o Imgur:", response.json())
            return None

# 📌 Função para salvar anúncio no Firebase
def save_to_firebase(image_url, description, link):
    ref = db.reference("ads")
    new_ad = ref.push({
        "image": image_url,
        "description": description,
        "link": link
    })
    print("✅ Anúncio salvo no Firebase com sucesso!")

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
