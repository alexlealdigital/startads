from flask import Flask, jsonify

app = Flask(__name__)  # Certifique-se de que essa linha existe

# Rota de teste
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})

if __name__ == "__main__":
    app.run(debug=True)
