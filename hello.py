from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# Bamboo details
BAMBOO_URL = "https://784cb36d0fe8.ngrok-free.app/rest/api/latest/queue/AUT-AUT"
BAMBOO_USER = "krian"
BAMBOO_PASS = "krian@1234"
 
# Jira Server details
JIRA_URL = "http://192.168.68.72:8080"
JIRA_USER = "krian"
JIRA_PASS = "krian@1234"                 # Replace with your Jira password

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({'error': 'Unsupported content type'}), 400

    data = request.get_json()

    if request.headers.get('X-GitHub-Event') == 'ping':
        print("✅ GitHub webhook ping received!")
        return jsonify({'message': 'Pong!'}), 200

    if request.headers.get('X-GitHub-Event') == 'push':
        repo = data.get('repository', {}).get('full_name', 'unknown')
        pusher = data.get('pusher', {}).get('name', 'unknown')
        commit_msg = data.get('head_commit', {}).get('message', 'No commit message')
        commit_id = data.get('head_commit', {}).get('id', '')
        branch = data.get('ref', '').split('/')[-1]

        print(f"📦 Repo: {repo}")
        print(f"👤 Pusher: {pusher}")
        print(f"💬 Commit message: {commit_msg}")
        print(f"🔀 Branch: {branch}")
        print(f"🔗 Commit ID: {commit_id}")

        # Extract Jira issue key
        match = re.search(r'([A-Z]+-\d+)', commit_msg)
        if match:
            issue_key = match.group(1)
            print(f"🪪 Found Jira issue key: {issue_key}")
        else:
            print("⚠️ No Jira issue key found in commit.")
            return jsonify({'message': 'No Jira issue key found'}), 200

        # Trigger Bamboo build
        bamboo_response = requests.post(
            BAMBOO_URL,
            auth=(BAMBOO_USER, BAMBOO_PASS),
            params={
                'bamboo.variable.commit': commit_id,
                'bamboo.variable.branch': branc
            }
        )
        print(f"🚀 Bamboo build trigger status: {bamboo_response.status_code}")

        # Post comment to Jira issue
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

        return jsonify({'message': 'Build triggered and Jira updated'}), 200

    return jsonify({'message': 'Unhandled event type'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
