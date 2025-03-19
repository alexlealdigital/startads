import firebase_admin
from firebase_admin import credentials, db
import os
import json

# 🔹 Carregar a chave do Firebase do ambiente
firebase_key_json = os.environ.get("FIREBASE_KEY")
cred_dict = json.loads(firebase_key_json)

# 🔹 Inicializar o Firebase
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
})

# 🔹 Referência para os códigos de ativação
codes_ref = db.reference("codes")

# 🔹 Criando um código de teste
test_code = "TESTE123"

# 🔹 Salvando no Firebase
codes_ref.child(test_code).set(True)

print(f"✅ Código de teste '{test_code}' adicionado com sucesso ao Firebase!")
