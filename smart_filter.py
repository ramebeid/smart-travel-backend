def get_reviews_for_place(place_id):
    # Dummy reviews (replace with real API if needed)
    return [
        "Our favorite stop!",
        "Amazing experience.",
        "Definitely coming back!",
        "One of the best parts of the trip!"
    ]

def inject_must_see_places(city):
    from places_utils import fetch_google_places
    all_places = fetch_google_places(city)
    must_keywords = ["museum", "pyramids", "temple", "castle", "cathedral", "palace", "historic"]
    must_see = []
    for p in all_places:
        name = p.get("name", "").lower()
        desc = p.get("formatted_address", "").lower()
        if any(k in name or k in desc for k in must_keywords):
            must_see.append(p)
    return must_see[:4]

def filter_places(places, interests, avoid_crowds=False):
    keywords = [k.lower() for k in interests if k.strip()]
    good = []

    for place in places:
        name = place.get("name", "").lower()
        desc = place.get("formatted_address", "").lower()
        rating = place.get("rating", 0)
        reviews = get_reviews_for_place(place.get("place_id", ""))

        if rating < 4.6:
            continue
        if any("1 star" in r.lower() or "worst" in r.lower() or "never again" in r.lower() for r in reviews):
            continue
        if keywords and not any(k in name or k in desc for k in keywords):
            continue

        good.append(place)

    if not good:
        sorted_places = sorted(places, key=lambda x: x.get("rating", 0), reverse=True)
        good = sorted_places[:5]

    print(f"✅ Final selection: {len(good)} / {len(places)}")
    return good
