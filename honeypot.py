from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

@app.route('/api/v1/admin/login', methods=['POST'])
def fake_login():
    data = request.json
    # Captured 'attacker' data
    user_agent = request.headers.get('User-Agent')
    source_ip = request.remote_addr
    
    print(f"!!! ALERT: HONEYPOT TRIGGERED !!!")
    print(f"TIME: {datetime.datetime.now()}")
    print(f"SOURCE IP: {source_ip}")
    print(f"ATTEMPTED CREDS: {data}")
    print(f"USER AGENT: {user_agent}")
    print("-" * 30)

    # Always return a generic failure to keep the attacker trying
    return jsonify({"status": "error", "message": "Invalid database credentials"}), 401

if __name__ == '__main__':
    # Running on port 8080 inside the container
    app.run(host='0.0.0.0', port=8080)
