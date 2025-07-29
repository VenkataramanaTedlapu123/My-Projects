from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

BAMBOO_URL = "https://bf4174fea07f.ngrok-free.app/rest/api/latest/queue/AUT-AUT"
BAMBOO_USER = "krian"
BAMBOO_PASS = "krian@1234"

@app.route("/webhook", methods=["POST"])
def github_webhook():
    try:
        event = request.headers.get("X-GitHub-Event")
        print(f"Received event: {event}")

        if event == "ping":
            return jsonify({"msg": "pong"}), 200

        if event == "push":
            print("Push event received. Triggering Bamboo build...")
            resp = requests.post(BAMBOO_URL, auth=HTTPBasicAuth(BAMBOO_USER, BAMBOO_PASS))
            print(f"Bamboo response: {resp.status_code}, {resp.text}")
            if resp.status_code in [200, 202]:
                return jsonify({"msg": "Build triggered"}), 200
            else:
                return jsonify({"error": "Failed to trigger build", "details": resp.text}), 500

        return jsonify({"msg": "Event ignored"}), 200
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    print("hello world")
    print("How are you")
    app.run(port=5000, debug=True)
