import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from smart_filter import prepare_final_list, generate_itinerary
from places_utils import search_google_place

app = Flask(__name__)
CORS(app)

@app.route("/")
def health():
    return "✅ Smart Travel Backend Running"

@app.route("/plan", methods=["POST"])
def plan():
    try:
        data = request.get_json()
        city = data.get("city")
        if not city:
            return jsonify({"error": "Missing city"}), 400

        print(f"📍 Planning for: {city}")
        places = search_google_place(city)
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
        print("❌ Error in /plan:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
