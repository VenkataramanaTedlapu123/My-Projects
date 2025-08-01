from flask import Flask, request, jsonify
import requests
import re
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Bamboo details
BAMBOO_URL = "https://86f66e215a11.ngrok-free.app/rest/api/latest/queue/AUT-AUT"
BAMBOO_USER = "krian"
BAMBOO_PASS = "krian@1234"

# Jira Server details
JIRA_URL = "http://192.168.68.72:8080"
JIRA_USER = "krian"
JIRA_PASS = "krian@1234"

@app.route("/webhook", methods=["POST"])
def github_webhook():
    try:
        event = request.headers.get("X-GitHub-Event")
        print(f"Received event: {event}")

        if event == "ping":
            return jsonify({"msg": "pong"}), 200

        if event == "push":
            payload = request.json
            commits = payload.get("commits", [])
            branch = payload.get("ref", "unknown").split("/")[-1]
            commit_found = False

            for commit in commits:
                commit_msg = commit.get("message", "")
                commit_id = commit.get("id", "")[:7]
                print(f"Commit message: {commit_msg}")

                match = re.search(r'([A-Z]+-\d+)', commit_msg)
                if match:
                    issue_key = match.group(1)
                    print(f"🪪 Found Jira issue key: {issue_key}")
                    commit_found = True

                    # Trigger Bamboo build
                    print("Triggering Bamboo build...")
                    resp = requests.post(BAMBOO_URL, auth=HTTPBasicAuth(BAMBOO_USER, BAMBOO_PASS))
                    print(f"Bamboo response: {resp.status_code}, {resp.text}")

                    if resp.status_code not in [200, 202]:
                        return jsonify({"error": "Failed to trigger build", "details": resp.text}), 500

                    # Add comment to Jira
                    jira_comment = {
                        "body": f"🚧 Build started in Bamboo for commit `{commit_id}` on branch `{branch}`."
                    }
                    jira_response = requests.post(
                        f"{JIRA_URL}/rest/api/2/issue/{issue_key}/comment",
                        auth=(JIRA_USER, JIRA_PASS),
                        headers={"Content-Type": "application/json"},
                        json=jira_comment
                    )

                    if jira_response.status_code == 201:
                        print(f"📝 Comment added to Jira issue {issue_key}")
                    else:
                        print(f"❌ Failed to comment on Jira issue: {jira_response.status_code} - {jira_response.text}")
                        return jsonify({"error": "Failed to update Jira", "details": jira_response.text}), 500

                    return jsonify({'message': 'Build triggered and Jira updated'}), 200

            if not commit_found:
                print("⚠️ No Jira issue key found in commits.")
                return jsonify({'message': 'No Jira issue key found in any commit'}), 200

        return jsonify({"msg": "Event ignored"}), 200

    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == "__main__":
    print("Starting server...")
    app.run(port=5000, debug=True)
