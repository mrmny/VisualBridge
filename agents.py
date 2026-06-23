# HU: Ágens logika és Google GenAI API hívások kezelése
# EN: Agent logic and Google GenAI API integration
import os
import json

# HU: Új importok a .env kezeléséhez
# EN: Imports for handling .env files
from dotenv import load_dotenv

# HU: Azonnal beolvassuk a .env fájlt, még a kliens indulása előtt
# EN: Load the .env file immediately, before client initialization
load_dotenv()

# HU: Konstansok a SonarLint figyelmeztetések kiküszöbölésére
# EN: Constants to resolve SonarLint duplicate literal warnings
OAK_TREE_HU = "tölgyfa"


# HU: Az új, hivatalos Google GenAI SDK importálása
# EN: Import the official Google GenAI SDK
from google import genai
from google.genai import types

# HU: Importáljuk az előbb megírt piktogram-kereső képességet
# EN: Import the pictogram lookup skill
from skills import fetch_pictogram_by_keyword

class VisualBridgeAgent:
    """
    HU: VisualBridge ágens koordinátor az egyszerűsítéshez és a vizualizációhoz.
    EN: VisualBridge agent coordinator for text simplification and visualization mapping.
    """
    def __init__(self):
        # HU: Ellenőrizzük, hogy van-e valós API kulcs
        # EN: Check if there is a real API key configured
        api_key = os.getenv("GEMINI_API_KEY")
        self.is_mock = not api_key or api_key == "a_te_valodi_gemini_api_kulcsod"

        if not self.is_mock:
            try:
                self.client = genai.Client()
            except Exception as e:
                print(f"Hiba a Google GenAI Client inicializálásakor: {e}")
                self.is_mock = True

    def update_api_key(self, api_key: str):
        """
        HU: Dinamikusan frissíti a használt API kulcsot és újra-inicializálja a klienst.
        EN: Dynamically updates the API key and re-initializes the client.
        """
        self.is_mock = not api_key or api_key == "a_te_valodi_gemini_api_kulcsod"
        if not self.is_mock:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"Hiba a Google GenAI Client frissítésekor: {e}")
                self.is_mock = True
        else:
            self.client = None

    def simplify_text(self, complex_text: str, lang: str = "hu") -> list:
        """
        HU: 1. MODUL: Szöveg-egyszerűsítő ágens (Gemini vagy Mock verzió).
            Könnyen Érthető Kommunikációvá alakítja a bemeneti szöveget.
        EN: MODULE 1: Text simplification agent (Gemini or Mock version).
            Converts input text into Easy-to-Read Communication.
        """
        if self.is_mock:
            return self._mock_simplify_text(complex_text, lang)

        if lang == "hu":
            system_prompt = (
                "Ön egy autizmus spektrumzavarra és beszédfogyatékosságra szakosodott gyógypedagógus.\n"
                "FELADAT: Alakítsa át a megadott szöveget a Könnyen Érthető Kommunikáció szabályai szerint.\n"
                "SZABÁLYOK:\n"
                "1. Csak nagyon egyszerű tőmondatokat használjon (Alany + Állítmány + Tárgy/Határozó).\n"
                "2. Kerülje a metaforákat, absztrakt kifejezéseket, névmásokat és kötőszavakat (pl. 'mert', 'bár', 'ezért').\n"
                "3. Bontsa le a folyamatokat időrendi lépésekre.\n"
                "4. Minden mondat külön sorba kerüljön.\n"
                "5. Csak az átalakított mondatokat adja vissza, semmi mást."
            )
        else:
            system_prompt = (
                "You are a special education teacher specializing in autism spectrum disorder and speech impairment.\n"
                "TASK: Transform the given text according to the rules of Easy-to-Read Communication.\n"
                "RULES:\n"
                "1. Use only very simple sentences (Subject + Verb + Object/Adverbial).\n"
                "2. Avoid metaphors, abstract expressions, pronouns, and conjunctions (e.g., 'because', 'although', 'therefore').\n"
                "3. Break down processes into chronological steps.\n"
                "4. Each sentence must be on a new line.\n"
                "5. Return only the transformed sentences, nothing else."
            )

        # HU: A legújabb, ajánlott Gemini modell használata (gyors és kiváló strukturált feladatokra)
        # EN: Use the latest recommended Gemini model (fast and excellent for structured tasks)
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=complex_text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3
            )
        )
        raw_output = response.text.strip()

        # HU: Soronként szétszedjük a mondatokat egy listába
        # EN: Split sentences line by line into a list
        sentences = [s.strip() for s in raw_output.split("\n") if s.strip()]
        return sentences

    def _mock_simplify_hu(self, cleaned_text: str) -> list:
        # HU tölgyfa példa / HU oak example
        if OAK_TREE_HU in cleaned_text and "koronájával" in cleaned_text:
            return [
                f"A {OAK_TREE_HU} árnyékot ad.",
                f"A {OAK_TREE_HU} vizet iszik."
            ]
        # HU jármű példa / HU vehicle example
        elif "autó" in cleaned_text or "busz" in cleaned_text:
            return [
                "Az autó megy.",
                "A busz megáll."
            ]
        # HU kislány példa / HU girl example
        elif "kislány" in cleaned_text or "baba" in cleaned_text or "labda" in cleaned_text:
            return [
                "A kislány játszik.",
                "A baba szép.",
                "A labda elgurul."
            ]
        return []

    def _mock_simplify_en(self, cleaned_text: str) -> list:
        # EN oak example
        if "oak tree" in cleaned_text and "shade" in cleaned_text:
            return [
                "The oak tree provides shade.",
                "The oak tree drinks water."
            ]
        # EN vehicle example
        elif "car" in cleaned_text or "bus" in cleaned_text:
            return [
                "The car goes.",
                "The bus stops."
            ]
        # EN girl example
        elif "little girl" in cleaned_text or "doll" in cleaned_text or "ball" in cleaned_text:
            return [
                "The girl plays.",
                "The doll is beautiful.",
                "The ball rolls away."
            ]
        return []

    def _mock_simplify_text(self, complex_text: str, lang: str = "hu") -> list:
        """
        HU: Szövegegyszerűsítés szimulációja (Mock).
        EN: Mock text simplification simulation.
        """
        cleaned_text = complex_text.strip().lower()

        if lang == "hu":
            res = self._mock_simplify_hu(cleaned_text)
        else:
            res = self._mock_simplify_en(cleaned_text)

        if res:
            return res

        # HU: Fallback általános bemenetekre
        # EN: Fallback for generic inputs
        import re
        sentences = re.split(r'[.!?]+', complex_text)
        result = []
        for s in sentences:
            s_clean = s.strip()
            if s_clean:
                # Keep simple sentences as is (mock simplified)
                result.append(s_clean + ".")
        return result


    def extract_keywords_to_json(self, sentences: list, lang: str = "hu") -> dict:
        """
        HU: 2. MODUL: Piktogram-leképező ágens (Gemini vagy Mock verzió).
            Kigyűjti a kulcsszavakat, és felépíti a végső strukturált JSON-t.
        EN: MODULE 2: Pictogram mapping agent (Gemini or Mock version).
            Extracts keywords and constructs the final structured JSON object.
        """
        if self.is_mock:
            return self._mock_extract_keywords_to_json(sentences, lang)

        sentences_str = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

        if lang == "hu":
            system_prompt = (
                "Ön egy vizuális kódoló ágens, aki segít nem-verbális, autista gyermekeknek piktogramokat találni.\n"
                "FELADAT: A kapott sorszámozott mondatokból gyűjtse ki azokat a kulcsszavakat (főnevek, igék, alapvető tulajdonságok), "
                "amelyekhez egyértelmű vizuális piktogram rendelhető az ARASAAC rendszerben.\n"
                "KIMENETI FORMÁTUM: Kizárólag egy tiszta JSON objektumot adjon vissza az alábbi struktúrában, markdown kódblokkok nélkül:\n"
                "{\n"
                "  'processed_story': [\n"
                "    {\n"
                "      'sentence': 'A mondat szövege',\n"
                "      'keywords': ['kulcsszó1', 'kulcsszó2']\n"
                "    }\n"
                "  ]\n"
                "}"
            )
        else:
            system_prompt = (
                "You are a visual coding agent who helps non-verbal children with autism find pictograms.\n"
                "TASK: From the provided numbered sentences, extract the keywords (nouns, verbs, basic attributes) "
                "that can be mapped to clear visual pictograms in the ARASAAC system.\n"
                "OUTPUT FORMAT: Return only a clean JSON object in the following structure, without markdown code blocks:\n"
                "{\n"
                "  'processed_story': [\n"
                "    {\n"
                "      'sentence': 'The text of the sentence',\n"
                "      'keywords': ['keyword1', 'keyword2']\n"
                "    }\n"
                "  ]\n"
                "}"
            )

        # HU: Gemini kényszerítése strukturált JSON kimenetre (Structured Outputs)
        # EN: Force Gemini to output structured JSON (Structured Outputs)
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=sentences_str,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

    def _heuristic_keywords(self, s_lower: str, stopwords: set) -> list:
        import re
        keywords = []
        words = re.findall(r'\b\w+\b', s_lower)
        for w in words:
            if len(w) > 2 and w not in stopwords:
                keywords.append(w)
        return keywords

    def _mock_extract_keywords_to_json(self, sentences: list, lang: str = "hu") -> dict:
        """
        HU: Kulcsszavak kigyűjtésének szimulációja (Mock).
        EN: Mock keyword extraction simulation.
        """
        processed_story = []

        # HU: Stopwords szavak a felesleges kulcsszavak kiszűrésére
        # EN: Stopwords to filter out non-pictogram keywords
        stopwords = {
            "hu": {"a", "az", "egy", "és", "de", "vagy", "hogy", "is", "ha", "csak", "nem", "sem", "meg", "el", "ki", "be", "le", "fel"},
            "en": {"a", "an", "the", "and", "but", "or", "because", "so", "if", "not", "is", "are", "was", "were", "to", "in", "on", "at", "of", "for", "with", "provides", "drinks", "from", "its"}
        }.get(lang, set())

        # HU: Lefejtjük az előre meghatározott kulcsszavakat a kognitív komplexitás csökkentése érdekében
        # EN: Define predefined keyword mappings to reduce cognitive complexity
        mock_keywords_map = {
            "hu": {
                f"{OAK_TREE_HU} árnyékot ad": [OAK_TREE_HU, "árnyék"],
                f"{OAK_TREE_HU} vizet iszik": [OAK_TREE_HU, "víz", "iszik"],
                "autó megy": ["autó", "megy"],
                "busz megáll": ["busz", "megáll"],
                "kislány játszik": ["lány", "játszik"],
                "baba szép": ["baba"],
                "labda elgurul": ["labda", "gurul"]
            },
            "en": {
                "oak tree provides shade": ["oak", "shade"],
                "oak tree drinks water": ["oak", "water", "drink"],
                "car goes": ["car", "go"],
                "bus stops": ["bus", "stop"],
                "girl plays": ["girl", "play"],
                "doll is beautiful": ["doll"],
                "ball rolls away": ["ball", "roll"]
            }
        }.get(lang, {})

        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue

            s_lower = s_clean.lower()
            keywords = []

            # HU: Megkeressük, hogy a mondat tartalmaz-e előre definiált kifejezést
            # EN: Check if the sentence contains any predefined mapping key
            matched = False
            for key, val in mock_keywords_map.items():
                if key in s_lower:
                    keywords = val
                    matched = True
                    break

            if not matched:
                keywords = self._heuristic_keywords(s_lower, stopwords)

            processed_story.append({
                "sentence": s_clean,
                "keywords": keywords
            })

        return {"processed_story": processed_story}

    def process_pipeline(self, raw_text: str, lang: str = "hu") -> dict:
        """
        HU: A teljes ágens folyamatot (pipeline) összekötő motor.
        EN: Main engine connecting the full multi-agent pipeline.
        """
        simple_sentences = self.simplify_text(raw_text, lang)
        json_structure = self.extract_keywords_to_json(simple_sentences, lang)

        for item in json_structure.get("processed_story", []):
            mapped_tokens = []
            for word in item.get("keywords", []):
                pic_data = fetch_pictogram_by_keyword(word, locale=lang)
                if pic_data["success"]:
                    mapped_tokens.append({
                        "word": word,
                        "image_url": pic_data["image_url"]
                    })
            item["tokens_with_pics"] = mapped_tokens

        return json_structure


# HU: Gyors teszt
# EN: Quick test runner
if __name__ == "__main__":
    print("Google Gemini Ágens tesztelése indul...")
    if os.getenv("GEMINI_API_KEY"):
        agent = VisualBridgeAgent()
        teszt_szöveg = "A sűrű erdőben élő barna medvék télen hosszú álomba merülnek a barlangjukban."
        try:
            eredmeny = agent.process_pipeline(teszt_szöveg)
            print(json.dumps(eredmeny, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Hiba történt: {e}")
    else:
        print("Nem futtatható: hiányzik a GEMINI_API_KEY környezeti változó.")
