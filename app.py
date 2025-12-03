# app.py
from flask import Flask, request, jsonify
import uuid, datetime

app = Flask(__name__)
# --- Mock endpoints para o Master Dashboard (tempo de dev) ---
@app.route('/robotics')
def robotics_summary():
    return jsonify({"status":"ok","summary":{"machines":2,"idle":2,"active":0,"alerts":0}}), 200

@app.route('/finance')
def finance_summary():
    return jsonify({"status":"ok","summary":{"cashflow":"estável","balance":12500}}), 200

@app.route('/security')
def security_summary():
    return jsonify({"status":"ok","summary":{"threats":0,"last_scan":"2025-12-02T00:00:00Z"}}), 200

@app.route('/audit')
def audit_summary():
    return jsonify({"status":"ok","summary":{"reports":[]}}), 200
# --- Unified summary endpoint for COA dashboard ---
from flask import jsonify
import datetime

@app.route('/summary')
def get_summary():
    """
    Return a consolidated view with all runners and important lists:
    {
      "timestamp": "...",
      "summary": {
         "robotics": {...},
         "finance": {...},
         "security": {...},
         "audit": {...},
         "health": {...},
         "energy": {...},
         "alerts": [...],
         "forecasts": [...],
         "bills": [...],
         "events": [...]
      }
    }
    """

    now = datetime.datetime.utcnow().isoformat() + "Z"
    # safe-read helpers
    bills = STORE.get("bills", [])
    alerts = STORE.get("alerts", [])
    forecasts = STORE.get("forecasts", [])
    last_bill = STORE.get("last_bill") or (bills[0] if bills else None)

    # If you already have functions that return summaries, call them (they return Response objects).
    # To keep this patch safe and independent, read STORE directly and use existing mock summaries:
    finance = {"status":"ok","summary":{"cashflow":"estável","balance":12500}}
    security = {"status":"ok","summary":{"threats":0,"last_scan":"2025-12-02T00:00:00Z"}}
    audit = {"status":"ok","summary":{"reports":[]}}
    health = {"status":"ok","summary":{"fatigue_avg":4.6,"users":1}}
    robotics = {"status":"ok","summary":{"lines": []}}  # placeholder — extend if you track robotics in STORE

    energy = {
        "status": "ok" if last_bill else "empty",
        "last_bill": last_bill
    }

    # consolidated object
    payload = {
        "timestamp": now,
        "summary": {
            "robotics": robotics,
            "finance": finance,
            "security": security,
            "audit": audit,
            "health": health,
            "energy": energy,
            "alerts": alerts,
            "forecasts": forecasts,
            "bills": bills,
            # events can be a log/stream if you keep it:
            "events": STORE.get("events", [])
        }
    }
    return jsonify(payload), 200

@app.route('/health/summary')
def health_summary():
    return jsonify({"status":"ok","summary":{"fatigue_avg":4.6,"users":1}}), 200

@app.route('/energy')
def energy_summary():
    # exemplo: devolve última fatura rápida
    bills = STORE.get("bills", [])
    last = bills[0] if bills else {}
    return jsonify({"status":"ok","last_bill": last}), 200
# --- fim mocks ---

STORE = {
    "bills": [],
    "alerts": [],
    "forecasts": [],
    "last_bill": None
}


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
# --- NEW ENDPOINT: /energy ---
@app.route('/energy')
def get_energy():
    # se não houver conta ainda, retorna estado padrão
    if not STORE["bills"]:
        return jsonify({
            "last_bill": None,
            "status": "empty"
        })
    
    # pegar a última conta
    last = STORE["bills"][0]
    return jsonify({
        "last_bill": last,
        "status": "ok"
    })

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8000)
