# HU: Ágens logika és Google GenAI API hívások kezelése (ADK keretrendszerrel)
# EN: Agent logic and Google GenAI API integration using Google ADK
import os
import json
from dotenv import load_dotenv

# HU: Google GenAI és ADK importok
# EN: Google GenAI and ADK imports
from google.genai import types

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.models.google_llm import Gemini
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, StdioServerParameters

from skills import fetch_pictogram_by_keyword

# HU: Beolvassuk a .env fájlt
# EN: Load the .env file
load_dotenv()

# HU: Az ADK elvárja a GOOGLE_API_KEY környezeti változót is
# EN: ADK also expects the GOOGLE_API_KEY environment variable
api_key = os.getenv("GEMINI_API_KEY")
if api_key and api_key != "a_te_valodi_gemini_api_kulcsod":
    os.environ["GOOGLE_API_KEY"] = api_key

OAK_TREE_HU = "tölgyfa"

class VisualBridgeAgent:
    """
    HU:
        VisualBridge ágens koordinátor az egyszerűsítéshez és a vizualizációhoz (ADK alapú).
    EN:
        VisualBridge agent coordinator for text simplification and visualization mapping (ADK-based).
    """
    def __init__(self):
        # HU: Ellenőrizzük, hogy van-e valós API kulcs
        # EN: Check if there is a real API key configured
        api_key_val = os.getenv("GEMINI_API_KEY")
        self.is_mock = not api_key_val or api_key_val == "a_te_valodi_gemini_api_kulcsod"

        # HU: Biztonsági beállítások (Security features)
        # EN: Safety/Security configurations
        self.safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            ),
        ]

        # HU: MCP Szerver és Toolset konfiguráció
        # EN: MCP Server and Toolset configuration
        self.mcp_server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
        self.connection_params = StdioConnectionParams(
            server_params=StdioServerParameters(
                command="python3",
                args=[self.mcp_server_path],
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
        )
        self.mcp_toolset = McpToolset(connection_params=self.connection_params)

    def update_api_key(self, api_key_str: str):
        """
        HU: Dinamikusan frissíti a használt API kulcsot.
        EN: Dynamically updates the API key.
        """
        self.is_mock = not api_key_str or api_key_str == "a_te_valodi_gemini_api_kulcsod"
        if not self.is_mock:
            os.environ["GEMINI_API_KEY"] = api_key_str
            os.environ["GOOGLE_API_KEY"] = api_key_str
        else:
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]
            if "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]

    def simplify_text(self, complex_text: str, lang: str = "hu") -> list:
        """
        HU: 1. MODUL: Szöveg-egyszerűsítő ágens (ADK & gemini-3.5-flash).
        EN: MODULE 1: Text simplification agent (ADK & gemini-3.5-flash).
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

        # HU: ADK Ágens inicializálása a legújabb gemini-3.5-flash modellel
        # EN: Initialize ADK Agent using the latest gemini-3.5-flash model
        simp_agent = Agent(
            name="simplifier_agent",
            model=Gemini(model="gemini-3.5-flash"),
            instruction=system_prompt,
            generate_content_config=types.GenerateContentConfig(
                safety_settings=self.safety_settings,
                temperature=0.3
            )
        )

        runner = InMemoryRunner(agent=simp_agent)
        session = runner.session_service.create_session(app_name="visual_bridge", user_id="streamlit_user")

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=complex_text)]
        )

        response_text = ""
        generator = runner.run(user_id=session.user_id, session_id=session.id, new_message=content)
        for event in generator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        sentences = [s.strip() for s in response_text.strip().split("\n") if s.strip()]
        return sentences

    def extract_keywords_to_json(self, sentences: list, lang: str = "hu") -> dict:
        """
        HU: 2. MODUL: Piktogram-leképező ágens (ADK & gemini-3.5-flash).
        EN: MODULE 2: Pictogram mapping agent (ADK & gemini-3.5-flash).
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

        # HU: ADK Ágens inicializálása strukturált JSON kimenettel
        # EN: Initialize ADK Agent with structured JSON output configuration
        keyword_agent = Agent(
            name="keyword_agent",
            model=Gemini(model="gemini-3.5-flash"),
            instruction=system_prompt,
            generate_content_config=types.GenerateContentConfig(
                safety_settings=self.safety_settings,
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        runner = InMemoryRunner(agent=keyword_agent)
        session = runner.session_service.create_session(app_name="visual_bridge", user_id="streamlit_user")

        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=sentences_str)]
        )

        response_text = ""
        generator = runner.run(user_id=session.user_id, session_id=session.id, new_message=content)
        for event in generator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        return json.loads(response_text)

    def process_pipeline(self, raw_text: str, lang: str = "hu") -> dict:
        """
        HU: A teljes ágens folyamatot (pipeline) összekötő motor. Az MCP toolset segítségével kéri le a piktogramokat.
        EN: Main engine connecting the full multi-agent pipeline. Uses MCP toolset for pictogram fetching.
        """
        simple_sentences = self.simplify_text(raw_text, lang)
        json_structure = self.extract_keywords_to_json(simple_sentences, lang)

        # HU: Ha szimulációs módban vagyunk, a lekérdezést közvetlenül a helyi API skill futtatja
        # EN: If in mock/simulation mode, the pictogram mapping runs directly via local skill
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

    # HU: MOCK segédfüggvények teszteléshez API kulcs nélkül
    # EN: MOCK helper functions for testing without API keys
    def _mock_simplify_hu(self, cleaned_text: str) -> list:
        if OAK_TREE_HU in cleaned_text and "koronájával" in cleaned_text:
            return [
                f"A {OAK_TREE_HU} árnyékot ad.",
                f"A {OAK_TREE_HU} vizet iszik."
            ]
        elif "autó" in cleaned_text or "busz" in cleaned_text:
            return [
                "Az autó megy.",
                "A busz megáll."
            ]
        elif "kislány" in cleaned_text or "baba" in cleaned_text or "labda" in cleaned_text:
            return [
                "A kislány játszik.",
                "A baba szép.",
                "A labda elgurul."
            ]
        return []

    def _mock_simplify_en(self, cleaned_text: str) -> list:
        if "oak tree" in cleaned_text and "shade" in cleaned_text:
            return [
                "The oak tree provides shade.",
                "The oak tree drinks water."
            ]
        elif "car" in cleaned_text or "bus" in cleaned_text:
            return [
                "The car goes.",
                "The bus stops."
            ]
        elif "little girl" in cleaned_text or "doll" in cleaned_text or "ball" in cleaned_text:
            return [
                "The girl plays.",
                "The doll is beautiful.",
                "The ball rolls away."
            ]
        return []

    def _mock_simplify_text(self, complex_text: str, lang: str = "hu") -> list:
        cleaned_text = complex_text.strip().lower()
        if lang == "hu":
            res = self._mock_simplify_hu(cleaned_text)
        else:
            res = self._mock_simplify_en(cleaned_text)

        if res:
            return res

        import re
        sentences = re.split(r'[.!?]+', complex_text)
        result = []
        for s in sentences:
            s_clean = s.strip()
            if s_clean:
                result.append(s_clean + ".")
        return result

    def _extract_keywords_from_sentence(self, s_clean: str, mock_keywords_map: dict, stopwords: set) -> list:
        s_lower = s_clean.lower()
        for key, val in mock_keywords_map.items():
            if key in s_lower:
                return val

        import re
        words = re.findall(r'\b\w+\b', s_lower)
        return [w for w in words if len(w) > 2 and w not in stopwords]

    def _mock_extract_keywords_to_json(self, sentences: list, lang: str = "hu") -> dict:
        processed_story = []
        stopwords = {
            "hu": {"a", "az", "egy", "és", "de", "vagy", "hogy", "is", "ha", "csak", "nem", "sem", "meg", "el", "ki", "be", "le", "fel"},
            "en": {"a", "an", "the", "and", "but", "or", "because", "so", "if", "not", "is", "are", "was", "were", "to", "in", "on", "at", "of", "for", "with", "provides", "drinks", "from", "its"}
        }.get(lang, set())

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
            if s_clean:
                keywords = self._extract_keywords_from_sentence(s_clean, mock_keywords_map, stopwords)
                processed_story.append({
                    "sentence": s_clean,
                    "keywords": keywords
                })

        return {"processed_story": processed_story}

if __name__ == "__main__":
    print("Google Gemini ADK Ágens tesztelése...")
    if os.getenv("GEMINI_API_KEY"):
        agent = VisualBridgeAgent()
        teszt_szöveg = "A sűrű erdőben élő barna medvék télen hosszú álomba merülnek a barlangjukban."
        try:
            eredmeny = agent.process_pipeline(teszt_szöveg)
            print(json.dumps(eredmeny, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Hiba történt: {e}")
    else:
        print("Mock mód tesztelése (nincs API kulcs):")
        agent = VisualBridgeAgent()
        eredmeny = agent.process_pipeline("A piros autó nagyon gyorsan száguld, a sárga busz pedig megáll.", lang="hu")
        print(json.dumps(eredmeny, indent=2, ensure_ascii=False))
