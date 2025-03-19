import firebase_admin
from firebase_admin import credentials, db
import os
import json

# 🔹 Carrega a chave do Firebase do ambiente
firebase_key_json = os.environ.get("FIREBASE_KEY")
cred_dict = json.loads(firebase_key_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://adsdados-default-rtdb.firebaseio.com/"
})

codes_ref = db.reference("codes")

# 🔹 Lista de códigos PIX válidos
codes = ["ABC123", "XYZ789", "QWE456", "RTY567", "UIO678"]

# 🔹 Adiciona os códigos ao Firebase
for code in codes:
    codes_ref.child(code).set(True)

print("✅ Códigos adicionados com sucesso!")
