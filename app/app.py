from flask import Flask, request, jsonify
from datetime import datetime, timezone
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import os

app = Flask(__name__)
CORS(app)

client = MongoClient(os.environ["MONGO_URI"]) #connexion mongoDB
db = client["events_db"]
events_collection = db["events"]

def check_id_exists(service_url, id_value, service, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(service_url + id_value, headers=headers)
        if resp.status_code != 200:
            return False, f"{service} ID does not exist"
        return True, None
    except requests.RequestException:
        return False, f"Service communication issue, check {service} API"

def verify_token(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post("http://proxy/auth/verify", headers=headers)
        if response.status_code != 200:
            return False
        return True
    except requests.RequestException:
        return False

@app.route("/deployments/<deployment_id>/events", methods=["GET"])
def events_deployment(deployment_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "Not authorized"}), 401
    
    deployment_events = list(events_collection.find({"deploymentId": deployment_id}, {"_id": 0})) #on recherche par déploiement_id sans récupérer l'id mongoDB
    return jsonify(deployment_events), 200

@app.route("/events", methods=["GET"])
def list_events():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "Not authorized"}), 401
    
    all_events = list(events_collection.find({}, {"_id": 0}))
    return jsonify(all_events), 200

@app.route("/events", methods=["POST"])
def create_event():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "Not authorized"}), 401
    
    data = request.json
    required = ["deploymentId", "type", "message"]
    for elem in required:
        if elem not in data:
            return jsonify({"message": "Missing required field"}), 400

    types = ["DEPLOYMENT_STARTED", "DEPLOYMENT_FINISHED", "DEPLOYMENT_ERROR", "ROLLBACK"]
    if data["type"] not in types:
        return jsonify({"message": "Invalid type"}), 400

    ok, msg = check_id_exists("http://proxy/deployments/", data["deploymentId"], "Deployment", token)
    if not ok:
        return jsonify({"message": msg}), 400

    if data.get("initiatedBy"):
        ok, msg = check_id_exists("http://proxy/users/", data["initiatedBy"], "User", token)
        if not ok:
            return jsonify({"message": msg}), 400

    event = {
        "deploymentId": data["deploymentId"],
        "type": data["type"],
        "message": data["message"],
        "data": data.get("data", {}),
        "initiatedBy": data.get("initiatedBy", ""),
        "createdAt": datetime.now(timezone.utc).isoformat()
    }

    result = events_collection.insert_one(event)
    event["id"] = str(result.inserted_id)  #on met une entrée id avec l'id de mongoDB
    return jsonify(event), 201

@app.route("/events/<event_id>", methods=["GET"])
def get_event(event_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not verify_token(token):
        return jsonify({"error": "Not authorized"}), 401

    try:
        event = events_collection.find_one({"_id": ObjectId(event_id)}) #conversion en type mongoDB pour son ID
    except:
        return jsonify({"message": "Invalid event ID format"}), 400

    if event:
        event["id"] = str(event["_id"])
        del event["_id"]
        return jsonify(event), 200
    
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