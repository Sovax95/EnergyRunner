# app.py
from flask import Flask, request, jsonify
import uuid, datetime

app = Flask(__name__)

STORE = {"bills": [], "alerts": [], "forecasts": []}

@app.route('/health')
def health():
    return jsonify({"runner":"EnergyRunner","status":"ok","timestamp":datetime.datetime.utcnow().isoformat()})

@app.route('/bills', methods=['GET'])
def get_bills():
    return jsonify(STORE["bills"])

@app.route('/bills', methods=['POST'])
def post_bill():
    data = request.get_json() or {}
    entry = {
        "id": str(uuid.uuid4()),
        "kwh": float(data.get("kwh",0)),
        "tariff": data.get("tariff","desconhecida"),
        "flag": data.get("flag","nenhuma"),
        "total": float(data.get("total",0)),
        "created_at": datetime.datetime.utcnow().isoformat(),
        "findings": []
    }
    if entry["flag"].lower()=="vermelha" and entry["total"]<300:
        entry["findings"].append("Possível cobrança incorreta da bandeira vermelha")
    STORE["bills"].insert(0,entry)
    return jsonify(entry),201

@app.route('/alerts')
def get_alerts():
    return jsonify(STORE["alerts"])

@app.route('/forecasts')
def forecasts():
    return jsonify([
        {"day":"amanhã","price":"alta"},
        {"day":"depois","price":"moderada"}
    ])

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    r.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return r

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8000)
