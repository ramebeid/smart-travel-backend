import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from places_utils import fetch_google_places
from smart_filter import prepare_final_list, generate_itinerary

app = Flask(__name__)
CORS(app)

@app.route("/")
def health():
    return "Backend is alive!"

@app.route("/plan", methods=["POST"])
def plan():
    try:
        data = request.get_json()
        city = data.get("city")
        if not city:
            return jsonify({"error": "Missing city"}), 400

        places = fetch_google_places(city)
        if not places:
            return jsonify({"error": "No places found"}), 404

        filtered = prepare_final_list(city, places)
        if not filtered:
            return jsonify({"error": "No suitable places"}), 404

        itinerary = generate_itinerary(filtered)
        if not itinerary:
            return jsonify({"error": "Failed to generate itinerary"}), 500

        return jsonify({"itinerary": itinerary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
