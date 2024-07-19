from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Load the mapping file
import json
with open('mapping.json') as f:
    mapping = json.load(f)

# GitHub webhook handler
@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    payload = request.json
    modified_files = [commit['modified'] for commit in payload['commits']]
    modified_files = [item for sublist in modified_files for item in sublist]

    for file in modified_files:
        for tag, file_path in mapping.items():
            if file_path in file:
                update_confluence(tag)

    return jsonify({'status': 'success'}), 200

def update_confluence(tag):
    # Confluence API URL and authentication
    confluence_url = 'https://your-confluence-instance/rest/api/content/{content_id}'
    auth = ('reid@forcetherapeutics.com', 'ATATT3xFfGF0wnwW7UFHPyaLQv5eLYvbfP6lWZlLq36-nSlSejOg4-dEyUkzU-hkUZEeOAcnLCRHavhHQYooWTeRfKmhWDbVr9JQXLx393HqmCvh_Y4Gvpz9a_0oAWipfvpm4baDOdcM2YUZpJlgYdZmNxekfUxb4O5F3MfiiUSdwcXytEawegw=564413B0')

    # Fetch the existing content
    response = requests.get(confluence_url, auth=auth)
    content = response.json()

    # Update the content
    updated_content = content['body']['storage']['value'] + f"<p>Code updated for section: {tag}</p>"

    update_data = {
        'version': {
            'number': content['version']['number'] + 1
        },
        'body': {
            'storage': {
                'value': updated_content,
                'representation': 'storage'
            }
        }
    }

    response = requests.put(confluence_url, json=update_data, auth=auth)
    return response.status_code

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
