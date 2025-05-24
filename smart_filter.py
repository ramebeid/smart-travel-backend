from places_utils import fetch_google_places

def inject_must_see_places(city):
    all_places = fetch_google_places(city)
    must_keywords = ["museum", "temple", "pyramids", "landmark", "cathedral", "castle", "palace", "heritage", "historic"]
    must_see = []

    for place in all_places:
        name = place.get("name", "").lower()
        desc = place.get("formatted_address", "").lower()
        if any(k in name or k in desc for k in must_keywords):
            must_see.append(place)

    return must_see[:3]

def get_reviews_for_place(_):
    return [
        "Great spot", "Favorite part of the trip", "Absolutely amazing!", "Must see again"
    ]

def filter_places(places, interests, avoid_crowds):
    interest_keywords = [kw.lower() for kw in interests if kw.strip()]
    good = []

    for p in places:
        name = p.get("name", "").lower()
        desc = p.get("formatted_address", "").lower()
        rating = p.get("rating", 0)
        reviews = get_reviews_for_place(p.get("place_id", ""))
        total = p.get("user_ratings_total", 0)

        if rating < 4.6 or total < 10:
            continue
        if any(bad in r.lower() for r in reviews for bad in ["worst", "never again", "dirty", "closed", "avoid"]):
            continue
        if avoid_crowds and total > 1000:
            continue
        if interest_keywords and not any(k in name or k in desc for k in interest_keywords):
            continue

        good.append(p)

    return good[:20]
