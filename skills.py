# HU: Ágens képességek és külső API hívások kezelése
# EN: Agent skills and external API call integrations
import requests
import os
import json

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arasaac_cache.json")

_cache_data = None

def load_cache() -> dict:
    """
    HU: Betölti a gyorsítótárat a helyi JSON fájlból vagy a memóriából.
    EN: Loads the cache from the local JSON file or memory.
    """
    global _cache_data
    if _cache_data is not None:
        return _cache_data

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache_data = json.load(f)
                return _cache_data
        except Exception as e:
            print(f"Hiba a gyorsítótár betöltésekor: {e}")
            _cache_data = {}
            return _cache_data
    _cache_data = {}
    return _cache_data

def save_cache(cache: dict):
    """
    HU: Elmenti a gyorsítótárat a helyi JSON fájlba és a memóriába.
    EN: Saves the cache to the local JSON file and memory.
    """
    global _cache_data
    _cache_data = cache
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Hiba a gyorsítótár mentésekor: {e}")

def fetch_pictogram_by_keyword(keyword: str, locale: str = "hu") -> dict:
    """
    HU: Lekéri egy kulcsszóhoz tartozó piktogram adatait az ARASAAC API-ból (vagy a gyorsítótárból).
    EN: Retrieves pictogram data associated with a keyword from the ARASAAC API (or cache).

    Args:
        keyword (str): HU: A keresett szó. / EN: The keyword search term.
        locale (str): HU: A nyelv kódja. / EN: Language locale code.

    Returns:
        dict: HU: Piktogram szótár URL-lel és ID-val. / EN: Pictogram dict with URL and ID.
    """
    # HU: Tisztítsuk meg a kulcsszót (kisbetűsítés, szóközök eltávolítása)
    # EN: Clean up the keyword (lowercasing, trimming spaces)
    keyword = keyword.strip().lower()
    locale = locale.strip().lower()

    # HU: Ellenőrizzük a gyorsítótárat
    # EN: Check the local cache
    cache = load_cache()
    cache_key = f"{locale}:{keyword}"
    if cache_key in cache:
        return cache[cache_key]

    # HU: ARASAAC kereső végpont
    # EN: ARASAAC search endpoint
    search_url = f"https://api.arasaac.org/api/pictograms/{locale}/search/{keyword}"

    try:
        response = requests.get(search_url, timeout=10)

        # HU: Ha a kérés sikeres és van találat
        # EN: If the request is successful and has results
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # HU: Kiválasztjuk az első (legrelevánsabb) találatot
                # EN: Select the first (most relevant) match
                best_match = data[0]
                pic_id = best_match.get("_id")

                # HU: Összerakjuk a közvetlen kép URL-jét (színes piktogram formátumban)
                # EN: Construct the direct image URL (colored pictogram format)
                image_url = f"https://api.arasaac.org/api/pictograms/{pic_id}"

                result = {
                    "word": keyword,
                    "id": pic_id,
                    "image_url": image_url,
                    "success": True
                }

                # HU: Elmentjük a gyorsítótárba
                # EN: Save to local cache
                cache[cache_key] = result
                save_cache(cache)

                return result
    except Exception as e:
        print(f"Hiba az API hívás során ({keyword}): {e}")

    # HU: Ha nincs találat vagy hiba történt, egy üres vázat adunk vissza
    # EN: If no match or error occurred, return empty structure
    return {
        "word": keyword,
        "id": None,
        "image_url": None,
        "success": False
    }

def generate_non_verbal_quiz(correct_word: str, distractors: list, locale: str = "hu") -> dict:
    """
    HU: Létrehoz egy 3 opciós vizuális kvízkérdést.
    EN: Generates a 3-option visual quiz question.

    Args:
        correct_word (str): HU: A helyes válasz szava. / EN: The correct answer word.
        distractors (list): HU: Tévesztő szavak. / EN: List of distractor words.
        locale (str): HU: Nyelvi kód. / EN: Language locale code.
    """
    options = []

    # HU: Helyes válasz piktogramjának lekérése
    # EN: Fetch pictogram for the correct answer
    correct_pic = fetch_pictogram_by_keyword(correct_word, locale=locale)
    if correct_pic["success"]:
        options.append({"word": correct_word, "url": correct_pic["image_url"], "is_correct": True})

    # HU: Tévesztők lekérése
    # EN: Fetch distractors
    for word in distractors[:2]:
        pic = fetch_pictogram_by_keyword(word, locale=locale)
        if pic["success"]:
            options.append({"word": word, "url": pic["image_url"], "is_correct": False})

    # HU: Helyileg fordított kérdés szöveg összerakása
    # EN: Build localized question text
    question_text = f"Melyik a(z) {correct_word}?" if locale == "hu" else f"Which one is {correct_word}?"
    return {
        "question": question_text,
        "options": options
    }

# HU: Gyors tesztelési lehetőség, ha magát a fájlt futtatod
# EN: Quick test runner option when executing the script directly
if __name__ == "__main__":
    print("Teszteljük az ARASAAC képességet...")
    teszt = fetch_pictogram_by_keyword("kutya")
    print("Eredmény:", teszt)
