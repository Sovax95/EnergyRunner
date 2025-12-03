# app.py
from flask import Flask, request, jsonify
import uuid, datetime

app = Flask(__name__)

# --- Mock endpoints para o Master Dashboard ---

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

@app.route('/health/summary')
def health_summary():
    return jsonify({"status":"ok","summary":{"fatigue_avg":4.6,"users":1}}), 200

# --- Unified summary endpoint for COA dashboard ---

@app.route('/summary')
def get_summary():
    """
    Retorna uma visão consolidada (Single Source of Truth)
    para o Dashboard da Dinastia Borges.
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Leitura segura do STORE
    bills = STORE.get("bills", [])
    alerts = STORE.get("alerts", [])
    forecasts = STORE.get("forecasts", [])
    last_bill = bills[0] if bills else None

    # Mocks de dados que ainda não estão no STORE
    finance = {"status":"ok","summary":{"cashflow":"estável","balance":12500}}
    security = {"status":"ok","summary":{"threats":0,"last_scan":"2025-12-02T00:00:00Z"}}
    audit = {"status":"ok","summary":{"reports":[]}}
    health = {"status":"ok","summary":{"fatigue_avg":4.6,"users":1}}
    robotics = {"status":"ok","summary":{"lines": []}}

    energy = {
        "status": "ok" if last_bill else "empty",
        "last_bill": last_bill
    }

    payload = {
        "timestamp": now,
        "summary": {
            "robotics": robotics,
            "finance": finance,
            "security": security,
            "audit": audit,
            "health": health,
            "energy": energy,
            "alerts": alerts,       # Agora puxa corretamente do STORE
            "forecasts": forecasts,
            "bills": bills,
            "events": STORE.get("events", [])
        }
    }
    return jsonify(payload), 200

# --- Armazenamento em Memória (Volátil) ---
STORE = {
    "bills": [],
    "alerts": [],
    "forecasts": [],
    "events": []
}

# --- Rotas Funcionais ---

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
    
    # Lógica de Auditoria Automática
    if entry["flag"].lower() == "vermelha" and entry["total"] < 300:
        msg = f"Auditoria: Bandeira Vermelha com valor baixo (R$ {entry['total']})"
        entry["findings"].append(msg)
        
        # Inserir no sistema de alertas global
        new_alert = {"severity": "MED", "message": msg, "timestamp": entry["created_at"]}
        STORE["alerts"].insert(0, new_alert)

    STORE["bills"].insert(0, entry)
    return jsonify(entry), 201

@app.route('/alerts')
def get_alerts():
    # Retorna os alertas reais do STORE
    return jsonify(STORE["alerts"])

@app.route('/forecasts')
def forecasts():
    return jsonify([
        {"day":"amanhã","price":"alta"},
        {"day":"depois","price":"moderada"}
    ])

# --- Endpoint de Energia Robusto ---
@app.route('/energy')
def get_energy():
    if not STORE["bills"]:
        return jsonify({
            "last_bill": None,
            "status": "empty"
        })
    
    last = STORE["bills"][0]
    return jsonify({
        "last_bill": last,
        "status": "ok"
    })

@app.after_request
def cors(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    r.headers["Access-Control-Allow-Headers"] = "Content-Type"
    r.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return r

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8000)
