from flask import Flask, request, jsonify
from request_tools import push, get
from get_mina_state import get_mina_ledger_state, get_mina_account_state
import requests
from auth_tools import get_headers
from constants import DB_NAME, URL, MOUNT

app = Flask(__name__)

class Args:
    def __init__(self, url="https://proxy.berkeley.minaexplorer.com/", address=None):
        self.url = url
        self.address = address

@app.route('/mina_ledger_state', methods=['GET'])
def handle_mina_ledger_state():
    url = request.args.get('url', default="https://proxy.berkeley.minaexplorer.com/")
    args = Args(url=url)
    result = get_mina_ledger_state(args)
    return jsonify(result)

@app.route('/mina_account_state', methods=['GET'])
def handle_mina_account_state():
    url = request.args.get('url', default="https://proxy.berkeley.minaexplorer.com/")
    address = request.args.get('address')
    if address is None:
        return jsonify({"message": "Mina public key of zkApp or user is required."}), 400
    args = Args(url=url, address=address)
    input_result, evm_res = get_mina_account_state(args)
    return jsonify({"input_result": input_result, "evm_res": evm_res})


@app.route('/request_tools', methods=['POST'])
def handle_post_request_tools():
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

@app.route('/request_tools', methods=['GET'])
def handle_get_request_tools():
    auth = request.args.get('auth')
    key = request.args.get('key')
    request_status = request.args.get('request_status')
    verbose = request.args.get('verbose', False)
    res = get(auth, key, request_status, verbose)
    if res:
        return jsonify(res)
    else:
        return jsonify({"message": "An error occurred while getting data."}), 400


@app.route('/get_proof', methods=['GET'])
def handle_get_proof():
    auth = request.args.get('auth')
    request_key = request.args.get('request_key')
    proof_key = request.args.get('proof_key')

    headers = get_headers(auth)
    url = URL + f"_db/{DB_NAME}/{MOUNT}/proof/"
    if request_key:
        url += f'?q=[{{"key" : "request_key", "value" : "{request_key}"}}]&full=true'
    elif proof_key:
        url += proof_key + "?full=true"
    res = requests.get(url=url, headers=headers)
    if res.status_code != 200:
        return {"status": "error", "code": res.status_code, "message": res.reason}, 400
    else:
        res_json = res.json()
        if proof_key is not None:
            res_json = res.json()[0]
        if "proof" in res_json:
            return {"status": "success", "proof": res_json["proof"]}, 200
        else:
            return {"status": "error", "message": "No proof found"}, 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)
