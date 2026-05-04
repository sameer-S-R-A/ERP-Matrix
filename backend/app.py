from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

url: str = "https://zwbhlmdcvaifkwgufezj.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp3YmhsbWRjdmFpZmt3Z3VmZXpqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzczOTQzNzksImV4cCI6MjA5Mjk3MDM3OX0.yCuUcSIQgSL0H3rGGkFQEErH_FBpjnr0KcIx3Cp39xw"
supabase: Client = create_client(url, key)


# ── Health ──────────────────────────────────────────────────────────────────

@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "ERP Management API"})


# ── Sites ────────────────────────────────────────────────────────────────────

@app.route("/sites", methods=["GET"])
def get_sites():
    response = supabase.table("sites").select("*").execute()
    return jsonify(response.data)


@app.route("/sites", methods=["POST"])
def add_site():
    body = request.get_json()
    required = ["name", "short", "location"]
    for field in required:
        if not body.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    data = {
        "name":     body["name"],
        "short":    body["short"],
        "location": body["location"],
        "status":   body.get("status", "active"),
    }
    response = supabase.table("sites").insert(data).execute()
    return jsonify(response.data[0]), 201


@app.route("/sites/<int:site_id>", methods=["GET"])
def get_site(site_id):
    response = supabase.table("sites").select("*").eq("id", site_id).execute()
    if not response.data:
        return jsonify({"error": "Site not found"}), 404
    return jsonify(response.data[0])


@app.route("/sites/<int:site_id>", methods=["PUT"])
def update_site(site_id):
    body = request.get_json()
    response = supabase.table("sites").update(body).eq("id", site_id).execute()
    if not response.data:
        return jsonify({"error": "Site not found"}), 404
    return jsonify(response.data[0])


@app.route("/sites/<int:site_id>", methods=["DELETE"])
def delete_site(site_id):
    response = supabase.table("sites").delete().eq("id", site_id).execute()
    if not response.data:
        return jsonify({"error": "Site not found"}), 404
    return jsonify({"message": "Site deleted"})


# ── Departments ──────────────────────────────────────────────────────────────

@app.route("/departments", methods=["GET"])
def get_departments():
    response = supabase.table("departments").select("*").execute()
    return jsonify(response.data)


@app.route("/departments", methods=["POST"])
def add_department():
    body = request.get_json()
    if not body.get("name"):
        return jsonify({"error": "'name' is required"}), 400

    data = {"name": body["name"], "description": body.get("description", "")}
    response = supabase.table("departments").insert(data).execute()
    return jsonify(response.data[0]), 201


@app.route("/departments/<int:dept_id>", methods=["GET"])
def get_department(dept_id):
    response = supabase.table("departments").select("*").eq("id", dept_id).execute()
    if not response.data:
        return jsonify({"error": "Department not found"}), 404
    return jsonify(response.data[0])


@app.route("/departments/<int:dept_id>", methods=["PUT"])
def update_department(dept_id):
    body = request.get_json()
    response = supabase.table("departments").update(body).eq("id", dept_id).execute()
    if not response.data:
        return jsonify({"error": "Department not found"}), 404
    return jsonify(response.data[0])


@app.route("/departments/<int:dept_id>", methods=["DELETE"])
def delete_department(dept_id):
    response = supabase.table("departments").delete().eq("id", dept_id).execute()
    if not response.data:
        return jsonify({"error": "Department not found"}), 404
    return jsonify({"message": "Department deleted"})


# ── Employees ────────────────────────────────────────────────────────────────

@app.route("/employees", methods=["GET"])
def get_employees():
    query = supabase.table("employees").select("*")

    site_id    = request.args.get("site_id")
    dept_id    = request.args.get("department_id")
    status     = request.args.get("status")
    search     = request.args.get("search")

    if site_id:
        query = query.eq("site_id", site_id)
    if dept_id:
        query = query.eq("department_id", dept_id)
    if status:
        query = query.eq("status", status)
    if search:
        query = query.ilike("name", f"%{search}%")

    response = query.execute()
    return jsonify(response.data)


@app.route("/employees", methods=["POST"])
def add_employee():
    body = request.get_json()
    required = ["name", "role", "phone", "site_id", "joining_date", "wage_per_day"]
    for field in required:
        if body.get(field) is None:
            return jsonify({"error": f"'{field}' is required"}), 400

    # Auto-generate employee ID (EMP001, EMP002 …)
    all_emps = supabase.table("employees").select("id").execute().data
    nums = []
    for e in all_emps:
        try:
            nums.append(int(e["id"].replace("EMP", "")))
        except Exception:
            pass
    next_num = (max(nums) + 1) if nums else 1
    emp_id = f"EMP{next_num:03d}"

    data = {
        "id":                emp_id,
        "name":              body["name"],
        "role":              body["role"],
        "phone":             body["phone"],
        "status":            body.get("status", "active"),
        "address":           body.get("address", ""),
        "site_id":           int(body["site_id"]),
        "department_id":     int(body["department_id"]) if body.get("department_id") else None,
        "joining_date":      body["joining_date"],
        "wage_per_day":      int(body["wage_per_day"]),
        "aadhaar":           body.get("aadhaar", ""),
        "bank_account":      body.get("bank_account", ""),
        "emergency_contact": body.get("emergency_contact", ""),
    }
    response = supabase.table("employees").insert(data).execute()
    return jsonify(response.data[0]), 201


@app.route("/employees/<emp_id>", methods=["GET"])
def get_employee(emp_id):
    response = supabase.table("employees").select("*").eq("id", emp_id).execute()
    if not response.data:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(response.data[0])


@app.route("/employees/<emp_id>", methods=["PUT"])
def update_employee(emp_id):
    body = request.get_json()
    response = supabase.table("employees").update(body).eq("id", emp_id).execute()
    if not response.data:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(response.data[0])


@app.route("/employees/<emp_id>", methods=["DELETE"])
def delete_employee(emp_id):
    response = supabase.table("employees").delete().eq("id", emp_id).execute()
    if not response.data:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify({"message": "Employee deleted"})


@app.route("/employees/<emp_id>/relocate", methods=["PUT"])
def relocate_employee(emp_id):
    body = request.get_json()
    if not body.get("site_id"):
        return jsonify({"error": "'site_id' is required"}), 400

    updates = {"site_id": int(body["site_id"])}
    if "department_id" in body:
        updates["department_id"] = int(body["department_id"]) if body["department_id"] else None

    response = supabase.table("employees").update(updates).eq("id", emp_id).execute()
    if not response.data:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(response.data[0])


# ── Attendance ───────────────────────────────────────────────────────────────

@app.route("/attendance/<emp_id>", methods=["GET"])
def get_attendance(emp_id):
    response = (
        supabase.table("attendance")
        .select("*")
        .eq("emp_id", emp_id)
        .order("date", desc=True)
        .execute()
    )
    return jsonify(response.data)


@app.route("/attendance", methods=["POST"])
def save_attendance():
    body = request.get_json()
    records = body if isinstance(body, list) else [body]

    for r in records:
        required = ["emp_id", "date", "status"]
        for field in required:
            if not r.get(field):
                return jsonify({"error": f"Each record needs '{field}'"}), 400
        r.setdefault("hours", 9 if r["status"] == "present" else 4 if r["status"] == "half_day" else 0)

    # Upsert so re-submitting the same day overwrites
    response = supabase.table("attendance").upsert(records, on_conflict="emp_id,date").execute()
    return jsonify({"saved": len(response.data)}), 201


# ── Payments ─────────────────────────────────────────────────────────────────

@app.route("/payments", methods=["GET"])
def get_payments():
    emp_id = request.args.get("emp_id")
    query  = supabase.table("payments").select("*").order("date", desc=True)
    if emp_id:
        query = query.eq("emp_id", emp_id)
    response = query.execute()
    return jsonify(response.data)


@app.route("/payments", methods=["POST"])
def add_payment():
    body = request.get_json()
    required = ["emp_id", "date", "type", "amount"]
    for field in required:
        if body.get(field) is None:
            return jsonify({"error": f"'{field}' is required"}), 400

    data = {
        "emp_id": body["emp_id"],
        "date":   body["date"],
        "type":   body["type"],
        "amount": int(body["amount"]),
        "note":   body.get("note", ""),
    }
    response = supabase.table("payments").insert(data).execute()
    return jsonify(response.data[0]), 201


if __name__ == "__main__":
    app.run(debug=True, port=5001)
