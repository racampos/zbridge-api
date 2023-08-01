from flask import Flask, request, jsonify
from request_tools import push, get

app = Flask(__name__)

@app.route('/push', methods=['POST'])
def handle_push():
    data = request.json
    auth = data.get('auth')
    key = data.get('key')
    state = data.get('state')
    cost = data.get('cost')
    verbose = data.get('verbose', False)
    res = push(auth, key, state, cost, verbose)
    if res:
        return jsonify(res)
    else:
        return jsonify({"message": "An error occurred while pushing data."}), 400

@app.route('/get', methods=['GET'])
def handle_get():
    auth = request.args.get('auth')
    key = request.args.get('key')
    request_status = request.args.get('request_status')
    verbose = request.args.get('verbose', False)
    res = get(auth, key, request_status, verbose)
    if res:
        return jsonify(res)
    else:
        return jsonify({"message": "An error occurred while getting data."}), 400

if __name__ == "__main__":
    app.run(debug=True)
