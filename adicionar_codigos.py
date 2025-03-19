import firebase_admin
from firebase_admin import credentials, db
import os
import json

# 🔹 Obtendo a chave do Firebase do ambiente (Render)
firebase_key_json = os.environ.get("FIREBASE_KEY")

if not firebase_key_json:
    print("❌ ERRO: A variável FIREBASE_KEY não foi encontrada.")
    exit(1)

try:
    # 🔹 Carregando a chave corretamente (mesma lógica do server.py)
    cred_dict = json.loads(firebase_key_json)
    cred = credentials.Certificate(cred_dict)

    # 🔹 Inicializando o Firebase (se ainda não estiver inicializado)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
        })

    # 🔹 Criando a referência ao nó "codes" no Firebase
    codes_ref = db.reference("codes")

    # 🔹 Lista de códigos que serão armazenados
    codes = ["ABC123", "XYZ789", "QWE456", "RTY567", "UIO678"]

    for code in codes:
        codes_ref.child(code).set(True)  # Armazena o código como ativo (True)

    print("✅ Códigos adicionados com sucesso!")

except json.JSONDecodeError as e:
    print(f"❌ ERRO ao decodificar JSON: {e}")
except Exception as e:
    print(f"❌ ERRO inesperado: {e}")
