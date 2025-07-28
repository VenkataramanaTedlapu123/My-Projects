
print("hello world")
print("How are you")
from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Bamboo build queue API URL
BAMBOO_URL = "https://bf4174fea07f.ngrok-free.app/rest/api/latest/queue/AUT-AUT"
BAMBOO_USER = "krian"
BAMBOO_PASS = "krian@1234"

@app.route("/webhook", methods=["POST"])
def github_webhook():
    event = request.headers.get("X-GitHub-Event")
    
    if event == "ping":
        # Respond to ping event from GitHub webhook setup
        return jsonify({"msg": "pong"}), 200

    if event == "push":
        # Trigger Bamboo build
        try:
            resp = requests.post(BAMBOO_URL, auth=HTTPBasicAuth(BAMBOO_USER, BAMBOO_PASS))
        except Exception as e:
            return jsonify({"error": "Exception when triggering build", "details": str(e)}), 500

        if resp.status_code in (200, 202):
            return jsonify({"msg": "Build triggered", "bamboo_response": resp.text}), 200
        else:
            return jsonify({
                "error": "Failed to trigger build",
                "status_code": resp.status_code,
                "details": resp.text
            }), 500

    # Ignore other event types gracefully
    print("Done")
    return jsonify({"msg": "Event ignored"}), 200


if __name__ == "__main__":
    # Run Flask app on port 5000
    app.run(port=5000)

