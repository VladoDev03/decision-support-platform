from flask import Flask, render_template, request, jsonify
from algorithms.borda import borda_count, borda_winner
from algorithms.nanson import nanson
from algorithms.electre import electre_i
from algorithms.cbim import run_cbim
from algorithms.topsis import run_topsis

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    votes = data.get("votes", [])
    if not votes:
        return jsonify({"error": "No input data provided"}), 400

    borda_scores = borda_count(votes)
    borda_result = borda_winner(votes)
    nanson_result = nanson(votes)

    return jsonify({
        "borda": {
            "scores": borda_scores,
            "winner": borda_result,
        },
        "nanson": {
            "rounds": nanson_result["rounds"],
            "winner": nanson_result["winner"],
        },
        "paradox": borda_result != nanson_result["winner"]
    })


@app.route("/topsis", methods=["POST"])
def topsis_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    alternatives = data.get("alternatives", [])
    weights = data.get("weights", [])
    criteria_types = data.get("criteria_types", [])

    if not alternatives:
        return jsonify({"error": "No alternatives provided"}), 400
    if not weights:
        return jsonify({"error": "No weights provided"}), 400
    if not criteria_types:
        return jsonify({"error": "No criteria_types provided"}), 400
    if len(weights) != len(criteria_types):
        return jsonify({"error": "weights and criteria_types must have the same length"}), 400

    try:
        results = run_topsis(alternatives, weights, criteria_types)
        return jsonify({"results": results})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/electre", methods=["POST"])
def electre_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    alternatives = data.get("alternatives", [])
    weights = data.get("weights", [])
    criteria_types = data.get("criteria_types", [])

    if not alternatives:
        return jsonify({"error": "No alternatives provided"}), 400
    if not weights:
        return jsonify({"error": "No weights provided"}), 400
    if not criteria_types:
        return jsonify({"error": "No criteria_types provided"}), 400
    if len(weights) != len(criteria_types):
        return jsonify({"error": "weights and criteria_types must have the same length"}), 400

    try:
        c_threshold = float(data.get("c_threshold", 0.6))
        d_threshold = float(data.get("d_threshold", 0.4))
    except (TypeError, ValueError):
        return jsonify({"error": "c_threshold and d_threshold must be numbers"}), 400

    result = electre_i(alternatives, weights, criteria_types, c_threshold, d_threshold)

    if "error" in result:
        return jsonify({"error": result["error"]}), 400

    return jsonify(result)


@app.route("/api/cbim", methods=["POST"])
def api_cbim():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body"}), 400

    required_fields = ["matrix", "alternatives", "criteria_types", "base_idx", "preferences"]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "error": f"Missing required field: '{field}'"}), 400

    try:
        matrix = data["matrix"]
        alternatives = data["alternatives"]
        criteria_types = data["criteria_types"]
        base_idx = int(data["base_idx"])
        preferences = data["preferences"]
        l_count = int(data.get("l_count", 3))

        if not matrix or not alternatives:
            return jsonify({"success": False, "error": "matrix and alternatives must not be empty"}), 400
        if len(matrix) != len(alternatives):
            return jsonify({"success": False, "error": "matrix rows must match number of alternatives"}), 400
        if base_idx < 0 or base_idx >= len(alternatives):
            return jsonify({"success": False, "error": "base_idx is out of range"}), 400

        results = run_cbim(matrix, alternatives, criteria_types, base_idx, preferences, l_count)
        return jsonify({"success": True, "results": results})
    except (TypeError, ValueError) as e:
        return jsonify({"success": False, "error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
