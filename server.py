@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello, World!"})
