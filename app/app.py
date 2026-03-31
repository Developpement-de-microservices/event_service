from flask import Flask, request, jsonify
from datetime import datetime, timezone
from flask_cors import CORS #pour try sur swagger
import requests
import uuid
import json

app = Flask(__name__)
CORS(app)

def load_events():
    try:
        with open("./data.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_events(events):
    with open("./data.json", "w") as file:
        json.dump(events, file)

def check_id_exists(service_url, id_value, service, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(service_url+id_value,headers=headers)
        if resp.status_code != 200:
            return False, f"{service} ID does not exist"
        return True, None
    except requests.RequestException:
        return False, f"Service communication issue, check {service} API"

@app.route("/deployments/<deployment_id>/events", methods=["GET"])
def events_deployement(deployment_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401
    
    events = load_events()
    deployment_events = []

    for event in events.values():
        if event["deploymentId"] == deployment_id:
            deployment_events.append(event)

    return jsonify(deployment_events), 200

@app.route("/events", methods=["GET"])
def list_events():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401
    
    events = load_events()
    return jsonify(list(events.values())), 200 #retourne notre dictionnaire sous forme de json -> passage par liste obligé

@app.route("/events", methods=["POST"])
def create_event():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401
    
    events = load_events()
    data = request.json

    required = ["deploymentId", "type", "message"]
    for elem in required:
        if not elem in data:
            return jsonify({"message": "Missing required field"}), 400
        
    types = ["DEPLOYMENT_STARTED", "DEPLOYMENT_FINISHED", "DEPLOYMENT_ERROR", "ROLLBACK"]
    if not data["type"] in types:
        return jsonify({"message": "Invalid type"}), 400
    
    ok, msg = check_id_exists("http://proxy/deployments/", data["deploymentId"], "Deployment", token)
    if not ok: #id non existant ou service non attegnable
        return jsonify({"message": msg}), 400

    if data.get("initiatedBy"): #argument faculatif
        ok, msg = check_id_exists("http://proxy/users/", data["initiatedBy"], "User", token)
        if not ok:
            return jsonify({"message": msg}), 400

    event_id = str(uuid.uuid4()) #nombre aléatoire
    
    event = {
        "id": event_id,
        "deploymentId": data["deploymentId"],
        "type": data["type"],
        "message": data["message"],
        "data": data.get("data", {}), #si vide alors {}
        "initiatedBy": data.get("initiatedBy", ""),
        "createdAt": datetime.now(timezone.utc).isoformat()
    } #dico d'event

    events[event_id] = event # dico pour ne pas a faire de boucle for lors des get
    save_events(events)
    return jsonify(event), 201

@app.route("/events/<event_id>", methods=["GET"])
def get_event(event_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Not authorized"}), 401
    except requests.RequestException:
        return jsonify({"error": "Unable to check token, check /auth API"}), 401
    
    events = load_events()
    if event_id in events:
        return jsonify(events[event_id]), 200
    
    return jsonify({"message": "Event not found"}), 404

@app.route("/events/health", methods=["GET"])
def get_health_events():
    response = {
        "status": "ok",
        "service": "Events",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
