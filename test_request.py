import requests

response = requests.post("http://127.0.0.1:5000/plan", json={
    "city": "Cairo",
    "days": 2,
    "interests": ["local food", "ancient history", "relaxing"],
    "avoid_crowds": True
})

print("\n--- AI-Generated Itinerary ---\n")
print(response.json()["itinerary"])

