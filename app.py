from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
from config import DEFAULT_TIMEZONE
from models import get_daily_sales_summary, get_hourly_sales_summary, get_period_comparison, get_data_quality_report

def error_response(message, code=400, error="Bad Request"):
    return jsonify({
        "error": error,
        "message": message,
        "code": code,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), code

# Initialize the app
app = Flask(__name__)
CORS(app)

# Define routes
@app.route("/api/sales/daily", methods=["GET"])
def sales_daily():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    timezone = request.args.get("timezone", DEFAULT_TIMEZONE)

    if not start_date or not end_date:
        return error_response("start_date and end_date are required", code=400, error="Missing query parameters")

    try:
        result = get_daily_sales_summary(start_date, end_date, timezone)
        return jsonify(result)
    except Exception as e:
        return error_response("start_date must be in YYYY-MM-DD format", code=400, error="Invalid date format")


@app.route("/api/sales/hourly", methods=["GET"])
def sales_hourly():
    date = request.args.get("date")
    timezone = request.args.get("timezone", DEFAULT_TIMEZONE)

    if not date:
        return jsonify({"error": "date is required"}), 400

    try:
        result = get_hourly_sales_summary(date, timezone)
        return jsonify(result)
    except Exception as e:
        return error_response("date must be in YYYY-MM-DD format", code=400, error="Invalid date format")


@app.route("/api/sales/compare", methods=["GET"])
def sales_compare():
    period1 = request.args.get("period1")  # Format: YYYY-MM
    period2 = request.args.get("period2")
    timezone = request.args.get("timezone", DEFAULT_TIMEZONE)

    if not period1 or not period2:
        return jsonify({"error": "period1 and period2 are required"}), 400

    try:
        result = get_period_comparison(period1, period2, timezone)
        return jsonify(result)
    except Exception as e:
        return error_response("period1 and period2 must be in YYYY-MM format", code=400, error="Invalid period format")


@app.route("/api/data-quality", methods=["GET"])
def data_quality():
    try:
        result = get_data_quality_report()
        return jsonify(result)
    except Exception as e:
        return error_response("Failed to retrieve data quality report", code=500, error="Internal Server Error")

# App entry point
if __name__ == "__main__":
    app.run(debug=True)