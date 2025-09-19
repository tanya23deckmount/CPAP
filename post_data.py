# import requests

# url = "https://deckmount.in/api/web/tanya.php"

# payload = {
#     "user_id": "1",
#     "name": "Tanya",
#     "age": "21 Year",
#     "status": "1",
#     "file_name": "DATA1001.TXT"
# }

# response = requests.post(url, data=payload)

# print(response.json())
from flask import Flask, jsonify, request

app = Flask(__name__)

# Example route
@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello Tanya, your API is running!"})

# Example POST route
@app.route('/add', methods=['POST'])
def add_numbers():
    data = request.get_json()
    a = data.get("a", 0)
    b = data.get("b", 0)
    return jsonify({"sum": a + b})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
