from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins for simplicity

@app.route('/greet', methods=['POST'])
def greet():
    data = request.get_json()
    name = data.get('name')
    if name:
        return jsonify({"message": f"Hello, {name}!"})
    else:
        return jsonify({"error": "Name not provided"}), 400

if __name__ == '__main__':
    app.run(debug=True)