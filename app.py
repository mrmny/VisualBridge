# HU: Fő Streamlit alkalmazás modul a VisualBridge-hez
# EN: Main Streamlit application module for VisualBridge
import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv
from agents import VisualBridgeAgent
from skills import generate_non_verbal_quiz
from i18n import TranslationManager

# HU: Beolvassuk a .env fájlt
# EN: Load the .env file
load_dotenv()

# HU: Oldal konfigurációja (szép, széles elrendezés és gyerekbarát ikon)
# EN: Page configuration (clean, wide layout and kid-friendly icon)
st.set_page_config(page_title="VisualBridge - Vizuális Oktatás", page_icon="🌲", layout="wide")

# HU: Inicializáljuk a nyelvi managert a munkamenetben (Session State)
# EN: Initialize the translation manager in the Session State
if "trans_mgr" not in st.session_state:
    st.session_state.trans_mgr = TranslationManager()

if "result" not in st.session_state:
    st.session_state.result = None

if "current_lang" not in st.session_state:
    st.session_state.current_lang = "hu"

# HU: Biztosítjuk, hogy a trans_mgr nyelve szinkronban legyen
# EN: Ensure the trans_mgr language is in sync
st.session_state.trans_mgr.set_language(st.session_state.current_lang)

if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""

if "key_expiry_time" not in st.session_state:
    st.session_state.key_expiry_time = 0.0

if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = None


# HU: Fordítási segédfüggvény
# EN: Translation helper function
def _(text):
    return st.session_state.trans_mgr.gettext(text)


# HU: Segédfüggvény a kép MIME típusának meghatározásához kiterjesztés alapján
# EN: Helper function to determine the image MIME type based on extension
def get_image_mime_type(ext):
    if ext == ".svg":
        return "image/svg+xml"
    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        return f"image/{ext[1:]}"
    else:
        return "image"


# HU: Helyi képek beágyazása base64 formátumban a markdown tartalomban
# EN: Embed local images as base64 data URIs in markdown content
def embed_local_images(content):
    import base64
    import re
    pattern = r'!\[([^\]]*)\]\((assets/[^\)]+)\)'

    def replace_match(match):
        alt_text = match.group(1)
        relative_path = match.group(2)
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                ext = os.path.splitext(relative_path)[1].lower()
                mime = get_image_mime_type(ext)
                return f"![{alt_text}](data:{mime};base64,{encoded_string})"
            except Exception:
                pass
        return match.group(0)

    return re.sub(pattern, replace_match, content)


@st.dialog("VisualBridge", width="large")
def show_readme_dialog(lang):
    st.subheader(_("📖 Használati útmutató & Rendszerleírás"))
    readme_file = f"README_{lang}.md"
    if os.path.exists(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()

        content = embed_local_images(content)

        with st.container(height=650, key="readme_container"):
            st.markdown(content)
    else:
        st.error(f"File {readme_file} not found.")


@st.dialog("VisualBridge History", width="large")
def show_history_dialog(lang):
    st.subheader(_("💡 Projekt háttér & Ágensek a jóért"))
    history_file = f"HISTORY_{lang}.md"
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            content = f.read()

        content = embed_local_images(content)

        with st.container(height=650, key="history_container"):
            st.markdown(content)
    else:
        st.error(f"File {history_file} not found.")


# HU: Oldalsáv navigáció a két funkció között
# EN: Sidebar navigation between the two features
st.sidebar.subheader(_("🧭 Navigáció"))
selected_mode = st.sidebar.radio(
    _("Válasszon funkciót:"),
    options=["VisualBridge", "Text Simplifier"],
    format_func=lambda x: _(x),
    key="sidebar_nav"
)
st.sidebar.write("---")

# HU: "Olvass el" gomb a használati útmutató megnyitásához a nyelvválasztás felett
# EN: "Read me" button to open the user guide above the language selector
if st.sidebar.button(_("📖 Használati útmutató / Olvass el"), key="btn_readme_dialog", use_container_width=True):
    show_readme_dialog(st.session_state.current_lang)

# HU: "Miért ezt a projektet választottam?" gomb a projekt hátterének bemutatására
# EN: "Why I chose this project" button to show the project background
if st.sidebar.button(_("💡 Miért ezt a projektet választottam? / Projekt háttér"), key="btn_history_dialog", use_container_width=True):
    show_history_dialog(st.session_state.current_lang)


# HU: Nyelvválasztó a beállításokhoz
# EN: Language selector for settings
lang_options = ["Magyar", "English"]
default_idx = 0 if st.session_state.current_lang == "hu" else 1
selected_lang_label = st.sidebar.selectbox("Language / Nyelv", lang_options, index=default_idx)
lang_code = "hu" if selected_lang_label == "Magyar" else "en"

if st.session_state.current_lang != lang_code:
    st.session_state.current_lang = lang_code
    st.session_state.trans_mgr.set_language(lang_code)
    st.session_state.result = None
    st.rerun()


# HU: Beszédsebesség csúszka a gyermekeknek
# EN: Speech rate slider for children
st.sidebar.write("---")
st.sidebar.subheader(_("🔊 Beszédbeállítások"))
speech_rate = st.sidebar.slider(
    _("Beszéd sebessége (0.5 - lassú, 1.0 - normál):"),
    min_value=0.5,
    max_value=2.0,
    value=1.0,
    step=0.1,
    key="speech_rate"
)


# HU: API kulcs beállítások az oldalsávban (különösen hasznos saját kulcs megadásakor)
# EN: API key settings in the sidebar (especially useful for user-provided keys)
base_title = _("API kulcs beállításai")
if st.session_state.user_api_key.strip():
    if st.session_state.api_key_valid:
        expander_title = f"🟢 🔑 {base_title}"
    elif st.session_state.api_key_valid is not None:
        expander_title = f"🔴 🔑 {base_title}"
    else:
        expander_title = f"🟡 🔑 {base_title}"
else:
    expander_title = f"🔑 {base_title}"

with st.sidebar.expander(expander_title):
    st.write(_("Adja meg saját Gemini API kulcsát a teljes értékű mesterséges intelligencia (szöveg-egyszerűsítés és piktogram-leképezés) használatához. A kulcs kizárólag a böngésző munkamenet memóriájában tárolódik."))

    user_api_key_input = st.text_input(
        _("Gemini API kulcs:"),
        type="password",
        value=st.session_state.user_api_key,
        key="temp_api_key_input"
    )

    if user_api_key_input != st.session_state.user_api_key:
        st.session_state.user_api_key = user_api_key_input
        st.session_state.api_key_valid = None  # Reset key validation status
        if user_api_key_input.strip():
            import time
            st.session_state.key_expiry_time = time.time() * 1000 + 30 * 60 * 1000
            if "agent" not in st.session_state:
                st.session_state.agent = VisualBridgeAgent()
            st.session_state.agent.update_api_key(user_api_key_input)
        else:
            st.session_state.key_expiry_time = 0.0
            if "agent" in st.session_state:
                st.session_state.agent.update_api_key("")
        st.rerun()

    # HU: Vizuális kulcs-státusz kijelzése
    # EN: Visual key status indicator
    if st.session_state.user_api_key.strip():
        if st.session_state.key_expiry_time > 0.0:
            import time
            remaining_mins = max(0.0, (st.session_state.key_expiry_time - time.time() * 1000) / 60000.0)
            st.success(_("Saját kulcs aktív (hátralévő idő: {mins:.1f} perc).").format(mins=remaining_mins))
        else:
            st.success(_("Saját kulcs aktív."))
    elif os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "a_te_valodi_gemini_api_kulcsod":
        st.info(_("Rendszer alapértelmezett kulcs aktív."))
    else:
        st.warning(_("Szimulációs (Mock) mód aktív."))

# HU: Premium vizuális stílusok és Bootstrap beillesztése
# EN: Premium visual styles and Bootstrap stylesheet injection
bootstrap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "bootstrap", "css", "bootstrap.min.css")
if os.path.exists(bootstrap_path):
    with open(bootstrap_path, "r", encoding="utf-8") as f:
        bootstrap_css = f.read()
    st.markdown(f"<style>{bootstrap_css}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
    /* HU: Munkamenet hosszabbító rejtett gombok és konténereik elrejtése */
    /* EN: Hide session extension hidden buttons and their containers */
    div.st-key-btn_expire,
    div.st-key-btn_extend_5,
    div.st-key-btn_extend_10,
    div.st-key-btn_extend_15,
    div.st-key-btn_extend_30,
    .st-key-btn_expire,
    .st-key-btn_extend_5,
    .st-key-btn_extend_10,
    .st-key-btn_extend_15,
    .st-key-btn_extend_30 {
        display: none !important;
    }

    /* HU: README és HISTORY modal görgetősáv és méret korlátozás */
    /* EN: README and HISTORY modal scrollbar and size constraint */
    div.st-key-readme_container,
    div.st-key-history_container {
        max-height: 65vh !important;
        height: auto !important;
    }

    /* HU: Bootstrap testreszabása, hogy ne írja felül a Streamlit hátterét és színeit */
    /* EN: Prevent Bootstrap from overriding Streamlit's base layout backgrounds and colors */
    body {
        background-color: transparent !important;
        color: inherit !important;
    }

    /* HU: Fejlécek formázása */
    /* EN: Style headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', 'Inter', sans-serif;
        color: var(--text-color) !important;
    }

    /* HU: Egyedi fejléc banner gradienssel */
    /* EN: Add a custom gradient title banner */
    .banner {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .banner h1 {
        color: white !important;
        margin: 0;
        font-size: 2.2rem;
        border-bottom: none;
    }
    .banner p {
        color: white !important;
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* HU: Oszlopok rendezése kártya-szerű dobozokba a Streamlit témaszínei alapján */
    /* EN: Style columns as clean theme-adaptive cards */
    div[data-testid="stColumn"] {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        margin-bottom: 20px;
    }

    /* HU: Beágyazott oszlopok visszaállítása (hogy ne legyenek kártyák a kártyában) */
    /* EN: Reset nested columns to prevent card-in-card nesting */
    div[data-testid="stColumn"] div[data-testid="stColumn"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin-bottom: 0px !important;
    }

    /* HU: Elsődleges akciógombok stílusa */
    /* EN: Style for buttons */
    button[kind="primary"] {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
        transition: all 0.2s ease-in-out;
        color: white !important;
    }
    button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
        transform: scale(1.02);
    }

    /* HU: Piktogram alatti felirat stílusa */
    /* EN: Custom style for pictogram labels */
    .pic-label {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        color: #1e293b !important;
        opacity: 0.9;
        margin-top: 8px;
    }

    /* HU: Gyermek felületén a mondatkártya stílusa */
    /* EN: Style child visual block */
    .child-card-sentence {
        background-color: rgba(128, 128, 128, 0.08);
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid var(--primary-color);
        margin-bottom: 15px;
        color: var(--text-color);
    }

    /* HU: Gyermek tábla (Game Board) stílusa a jobb oldali oszlophoz */
    /* EN: Game Board container for the child in the right-side column */
    div[data-testid="stColumn"]:has(#child-panel-anchor) {
        background-color: rgba(245, 158, 11, 0.05) !important;
        border: 4px dashed rgba(245, 158, 11, 0.3) !important;
        border-radius: 24px !important;
        padding: 24px !important;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.05);
    }

    /* HU: Piktogram kártya stílusa lebegő animációval */
    /* EN: Pictogram card style with hover animation */
    .pic-card {
        background-color: #e2e8f0 !important;
        border: 2px solid rgba(128, 128, 128, 0.15) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        text-align: center !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
        margin-bottom: 12px;
    }
    .pic-card:hover {
        transform: translateY(-6px) scale(1.03) !important;
        box-shadow: 0 10px 20px -3px rgba(59, 130, 246, 0.15) !important;
        border-color: var(--primary-color) !important;
    }

    /* HU: Kvízgombok buborékos stílusa a gyermekfelületen */
    /* EN: Bubbly quiz buttons on the child board */
    div[data-testid="stColumn"]:has(#child-panel-anchor) button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        padding: 12px 20px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        min-height: 50px !important;
    }
    div[data-testid="stColumn"]:has(#child-panel-anchor) button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 15px rgba(16, 185, 129, 0.4) !important;
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# HU: Inicializáljuk az ágenst a munkamenetben (Session State)
# EN: Initialize the agent in Session State to prevent recreation on every rerun
if "agent" not in st.session_state or not hasattr(st.session_state.agent, "is_mock"):
    st.session_state.agent = VisualBridgeAgent()

if selected_mode == "VisualBridge":
    # HU: Egyedi fejléc banner renderelése
    # EN: Render custom header banner
    st.markdown(f"""
    <div class="banner">
        <h1>{_('🌲 VisualBridge – Vizuális Akadálymentesítő Asszisztens')}</h1>
        <p>{_('Segítség az autizmus spektrumzavarral és beszédfogyatékossággal élő gyermekek oktatásában.')}</p>
    </div>
    """, unsafe_allow_html=True)

    # HU: Ellenőrizzük, hogy az ágens szimulációs módban fut-e
    # EN: Check if the agent is running in mock/simulation mode
    if st.session_state.agent.is_mock:
        st.info(_("ℹ️ Szimulációs (Mock) mód aktív: Az ágens API kulcs nélkül, helyi szimulációval működik."))


    # HU: Konstansok a SonarLint figyelmeztetések kiküszöbölésére
    # EN: Constants to resolve SonarLint duplicate literal warnings
    CHOCOLATE_HU = "csokoládé"

    # HU: Sablonok a különböző célcsoportokhoz
    # EN: Templates for different target profiles
    TEMPLATES = {
        "neutral": {
            "hu": {
                "text": "A tölgyfa hatalmas koronájával árnyékot ad. A tölgyfa vizet iszik a földből a gyökereivel.",
                "correct": "víz",
                "dist1": "autó",
                "dist2": CHOCOLATE_HU,
                "icon": "🧒"
            },
            "en": {
                "text": "The oak tree provides shade with its huge crown. The oak tree drinks water from the soil with its roots.",
                "correct": "water",
                "dist1": "car",
                "dist2": "chocolate",
                "icon": "🧒"
            }
        },
        "boy": {
            "hu": {
                "text": "A piros autó nagyon gyorsan száguld, a sárga busz pedig megáll.",
                "correct": "autó",
                "dist1": "busz",
                "dist2": "vonat",
                "icon": "👦"
            },
            "en": {
                "text": "The red car goes fast, but the yellow bus stops.",
                "correct": "car",
                "dist1": "bus",
                "dist2": "train",
                "icon": "👦"
            }
        },
        "girl": {
            "hu": {
                "text": "A kislány a szép babával játszik, miközben a pöttyös labda elgurul.",
                "correct": "baba",
                "dist1": "labda",
                "dist2": "maci",
                "icon": "👧"
            },
            "en": {
                "text": "The little girl plays with the beautiful doll, while the polka dot ball rolls away.",
                "correct": "doll",
                "dist1": "ball",
                "dist2": "teddy bear",
                "icon": "👧"
            }
        }
    }

    # HU: Felület felosztása két oszlopra (Bal oldal: Tanár/Szülő, Jobb oldal: Gyermek)
    # EN: Partition layout into two columns (Left: Teacher/Parent, Right: Child)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header(_("🪪 Pedagógus / Szülő felület"))

        # HU: Profilválasztó legördülő
        # EN: Target profile selectbox
        profile_options = {
            "neutral": _("Semleges (Tölgyfa / Víz)"),
            "boy": _("Fiú (Autó / Busz)"),
            "girl": _("Lány (Baba / Labda)")
        }

        selected_profile = st.selectbox(
            _("Célcsoport profilja (sablon):"),
            options=list(profile_options.keys()),
            format_func=lambda x: profile_options[x]
        )

        if "current_profile" not in st.session_state:
            st.session_state.current_profile = "neutral"

        # HU: Ha változott a profil, frissítjük az állapotot és ürítjük a korábbi eredményt
        # EN: If the profile changed, update state and clear past result
        if selected_profile != st.session_state.current_profile:
            st.session_state.current_profile = selected_profile
            st.session_state.result = None

        st.write("---")
        st.subheader(_("Írja be a nyers tananyagot vagy utasítást:"))

        # HU: Aktuális sablon kiválasztása nyelv és profil alapján
        # EN: Select current template based on language and profile
        template = TEMPLATES[st.session_state.current_profile][lang_code]

        # HU: Dinamikus kulcsok, hogy a widgetek frissüljenek profilváltáskor
        # EN: Dynamic keys to trigger widget refresh upon profile change
        input_key = f"user_input_{lang_code}_{st.session_state.current_profile}"
        correct_key = f"correct_w_{lang_code}_{st.session_state.current_profile}"
        dist1_key = f"dist1_{lang_code}_{st.session_state.current_profile}"
        dist2_key = f"dist2_{lang_code}_{st.session_state.current_profile}"

        user_input = st.text_area(_("Bemeneti szöveg:"), value=template["text"], height=150, key=input_key)

        # HU: Kvíz beállítási lehetőségek a szülőnek
        # EN: Quiz setup configuration for parents
        st.subheader(_("🎲 Kvíz beállításai (Szövegértés ellenőrzése)"))
        if st.session_state.current_profile == "boy":
            correct_label = _("Helyes válasz szava (pl. mi száguld gyorsan?):")
        elif st.session_state.current_profile == "girl":
            correct_label = _("Helyes válasz szava (pl. mivel játszik a kislány?):")
        else:
            correct_label = _("Helyes válasz szava (pl. mi kell a fának?):")
        correct_w = st.text_input(correct_label, value=template["correct"], key=correct_key)
        distractor_1 = st.text_input(_("1. Rossz opció (Tévesztő):"), value=template["dist1"], key=dist1_key)
        distractor_2 = st.text_input(_("2. Rossz opció (Tévesztő):"), value=template["dist2"], key=dist2_key)

        generate_button = st.button(_("🚀 Vizuális anyag generálása"), type="primary")

    with col2:
        st.markdown('<div id="child-panel-anchor"></div>', unsafe_allow_html=True)
        child_icon = TEMPLATES[st.session_state.current_profile][lang_code]["icon"]
        st.header(f"{child_icon} {_('Gyermek felület')}")

        if generate_button and user_input:
            with st.spinner(_("Az ágens dolgozik, tőmondatokat és piktogramokat készít...")):
                try:
                    # HU: Futtatjuk a teljes ágens folyamatot (Pipeline) a kiválasztott nyelven
                    # EN: Run the full agent pipeline in the selected language
                    st.session_state.result = st.session_state.agent.process_pipeline(user_input, lang=lang_code)
                    if st.session_state.user_api_key.strip():
                        st.session_state.api_key_valid = True
                except Exception as e:
                    if st.session_state.user_api_key.strip():
                        st.session_state.api_key_valid = False
                    error_msg = _("Hiba történt a feldolgozás során: {e}").format(e=e)
                    st.error(error_msg)
                    st.info(_("Kérjük, ellenőrizze, hogy az API kulcsa érvényes-e és van-e internetkapcsolat."))

        if st.session_state.result:
            st.success(_("Elkészült a vizuális tananyag!"))
            st.write("---")

            # HU: Végigmegyünk a feldolgozott történet mondatain
            # EN: Loop through sentences of the processed story
            for item in st.session_state.result.get("processed_story", []):
                # HU: Megjelenítjük a letisztult, Könnyen Érthető tőmondatot hangfelolvasó gombbal
                # EN: Display the clean, Easy-to-Read simplified sentence with a Read Aloud button
                sentence_text = item.get("sentence", "")
                speech_lang = "hu-HU" if lang_code == "hu" else "en-US"
                btn_tooltip = _("🔊 Felolvasás")

                # HU: Egyedi HTML/CSS kártya beágyazása a böngésző natív felolvasójával, Bootstrap osztályokkal
                # EN: Embed custom HTML/CSS card with browser-native text-to-speech using Bootstrap classes
                bootstrap_tag = f"<style>{bootstrap_css}</style>" if 'bootstrap_css' in globals() else ""
                card_html = f"""
                {bootstrap_tag}
                <style>
                    body {{
                        margin: 0;
                        padding: 4px;
                        background: transparent;
                    }}
                    .card {{
                        background-color: #e2e8f0 !important;
                        border-color: rgba(128, 128, 128, 0.15) !important;
                    }}
                    /* Custom styles for gradient, shadows, hover animations */
                    .speak-btn-custom {{
                        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
                        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
                        transition: transform 0.2s, filter 0.2s;
                        border: none !important;
                    }}
                    .speak-btn-custom:hover {{
                        transform: scale(1.08);
                        filter: brightness(1.1);
                    }}
                </style>
                <div class="card p-3 d-flex flex-row justify-content-between align-items-center border-start border-primary border-4 shadow-sm">
                    <div class="fs-5 fw-bold" style="color: #1e293b !important;">{sentence_text}</div>
                    <button class="btn btn-primary rounded-circle d-flex align-items-center justify-content-center speak-btn-custom"
                            style="width: 44px; height: 44px; min-width: 44px; min-height: 44px; font-size: 18px;"
                            id="speak-btn"
                            title="{btn_tooltip}">🔊</button>
                </div>
                <script>
                    document.getElementById('speak-btn').addEventListener('click', function() {{
                        window.speechSynthesis.cancel();
                        var utterance = new SpeechSynthesisUtterance({repr(sentence_text)});
                        var speechLang = '{speech_lang}';
                        utterance.lang = speechLang;
                        utterance.rate = {speech_rate};

                        var voices = window.speechSynthesis.getVoices();
                        var matchingVoice = null;

                        // 1. Try exact match (e.g., hu-HU or en-US)
                        for (var i = 0; i < voices.length; i++) {{
                            if (voices[i].lang.toLowerCase() === speechLang.toLowerCase()) {{
                                matchingVoice = voices[i];
                                break;
                            }}
                        }}

                        // 2. Try prefix match (e.g., hu or en)
                        if (!matchingVoice) {{
                            var langPrefix = speechLang.split('-')[0].toLowerCase();
                            for (var i = 0; i < voices.length; i++) {{
                                if (voices[i].lang.toLowerCase().startsWith(langPrefix)) {{
                                    matchingVoice = voices[i];
                                    break;
                                }}
                            }}
                        }}

                        if (matchingVoice) {{
                            utterance.voice = matchingVoice;
                        }}
                        window.speechSynthesis.speak(utterance);
                    }});
                </script>
                """
                components.html(card_html, height=95)

                # HU: Kirakjuk egymás mellé a mondathoz tartozó piktogramokat hangfelolvasással
                # EN: Place pictograms side-by-side below the sentence with click-to-speak
                tokens = item.get("tokens_with_pics", [])
                if tokens:
                    speech_lang = "hu-HU" if lang_code == "hu" else "en-US"
                    bootstrap_tag = f"<style>{bootstrap_css}</style>" if 'bootstrap_css' in globals() else ""

                    pics_html = f"""
                    {bootstrap_tag}
                    <style>
                        body {{
                            margin: 0;
                            padding: 10px 4px;
                            background: transparent;
                            overflow: hidden;
                        }}
                        .pic-card {{
                            background-color: #e2e8f0 !important;
                            border: 2px solid rgba(128, 128, 128, 0.15) !important;
                            border-radius: 16px !important;
                            padding: 12px !important;
                            text-align: center !important;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
                            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
                            margin-bottom: 12px;
                            cursor: pointer;
                            display: inline-block;
                            width: 130px;
                        }}
                        .pic-card:hover {{
                            transform: translateY(-6px) scale(1.03) !important;
                            box-shadow: 0 10px 20px -3px rgba(59, 130, 246, 0.15) !important;
                            border-color: #3b82f6 !important;
                        }}
                        .pic-label {{
                            font-family: 'Inter', sans-serif;
                            font-size: 13px;
                            font-weight: bold;
                            text-align: center;
                            text-transform: uppercase;
                            color: #1e293b !important;
                            opacity: 0.9;
                            margin-top: 8px;
                            word-wrap: break-word;
                        }}
                        .pics-container {{
                            display: flex;
                            flex-wrap: wrap;
                            gap: 15px;
                            justify-content: flex-start;
                        }}
                    </style>
                    <div class="pics-container">
                    """
                    for idx, token in enumerate(tokens):
                        word_escaped = token['word'].replace("'", "\\'")
                        pics_html += f"""
                        <div class="pic-card" onclick="speakWord('{word_escaped}')" title="{_('🔊 Felolvasás')}">
                            <img src="{token['image_url']}" style="width: 100px; height: 100px; object-fit: contain;" />
                            <div class="pic-label">{token['word'].upper()}</div>
                        </div>
                        """
                    pics_html += f"""
                    </div>
                    <script>
                        function speakWord(word) {{
                            window.speechSynthesis.cancel();
                            var utterance = new SpeechSynthesisUtterance(word);
                            utterance.lang = '{speech_lang}';
                            utterance.rate = {speech_rate};

                            var voices = window.speechSynthesis.getVoices();
                            var matchingVoice = null;
                            for (var i = 0; i < voices.length; i++) {{
                                if (voices[i].lang.toLowerCase() === utterance.lang.toLowerCase()) {{
                                    matchingVoice = voices[i];
                                    break;
                                }}
                            }}
                            if (!matchingVoice) {{
                                var prefix = utterance.lang.split('-')[0].toLowerCase();
                                for (var i = 0; i < voices.length; i++) {{
                                    if (voices[i].lang.toLowerCase().startsWith(prefix)) {{
                                        matchingVoice = voices[i];
                                        break;
                                    }}
                                }}
                            }}
                            if (matchingVoice) {{
                                utterance.voice = matchingVoice;
                            }}
                            window.speechSynthesis.speak(utterance);
                        }}
                    </script>
                    """
                    height = 185 if len(tokens) <= 4 else 360
                    components.html(pics_html, height=height)
                st.write("---")

            # HU: ---------------- INTERAKTÍV KVÍZ SZAKASZ ----------------
            # EN: ---------------- INTERACTIVE QUIZ SECTION ----------------
            st.header(_("🧩 Ügyes vagy! Válaszolj a kérdésre:"))

            # HU: Legeneráljuk a kvíz adatait a megadott szavakból a skills.py segítségével, nyelv-specifikusan
            # EN: Generate quiz data from inputs using skills.py, localized
            quiz_data = generate_non_verbal_quiz(correct_w, [distractor_1, distractor_2], locale=lang_code)

            st.subheader(quiz_data["question"])

            # HU: Megjelenítjük a 3 válaszlehetőséget piktogramként, gombokkal
            # EN: Show the 3 quiz choices as pictograms with action buttons
            quiz_cols = st.columns(3)
            for idx, option in enumerate(quiz_data["options"]):
                with quiz_cols[idx]:
                    speech_lang = "hu-HU" if lang_code == "hu" else "en-US"
                    bootstrap_tag = f"<style>{bootstrap_css}</style>" if 'bootstrap_css' in globals() else ""
                    word_escaped = option['word'].replace("'", "\\'")

                    quiz_card_html = f"""
                    {bootstrap_tag}
                    <style>
                        body {{
                            margin: 0;
                            padding: 4px;
                            background: transparent;
                            overflow: hidden;
                        }}
                        .pic-card {{
                            background-color: #e2e8f0 !important;
                            border: 2px solid rgba(128, 128, 128, 0.15) !important;
                            border-radius: 16px !important;
                            padding: 12px !important;
                            text-align: center !important;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
                            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
                            cursor: pointer;
                            height: 148px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }}
                        .pic-card:hover {{
                            transform: translateY(-4px) scale(1.02) !important;
                            box-shadow: 0 10px 20px -3px rgba(59, 130, 246, 0.15) !important;
                            border-color: #3b82f6 !important;
                        }}
                    </style>
                    <div class="pic-card" onclick="speakWord('{word_escaped}')" title="{_('🔊 Felolvasás')}">
                        <img src="{option['url']}" style="width: 120px; height: 120px; object-fit: contain;" />
                    </div>
                    <script>
                        function speakWord(word) {{
                            window.speechSynthesis.cancel();
                            var utterance = new SpeechSynthesisUtterance(word);
                            utterance.lang = '{speech_lang}';
                            utterance.rate = {speech_rate};
                            var voices = window.speechSynthesis.getVoices();
                            var matchingVoice = null;
                            for (var i = 0; i < voices.length; i++) {{
                                if (voices[i].lang.toLowerCase() === utterance.lang.toLowerCase()) {{
                                    matchingVoice = voices[i];
                                    break;
                                }}
                            }}
                            if (!matchingVoice) {{
                                var prefix = utterance.lang.split('-')[0].toLowerCase();
                                for (var i = 0; i < voices.length; i++) {{
                                    if (voices[i].lang.toLowerCase().startsWith(prefix)) {{
                                        matchingVoice = voices[i];
                                        break;
                                    }}
                                }}
                            }}
                            if (matchingVoice) {{
                                utterance.voice = matchingVoice;
                            }}
                            window.speechSynthesis.speak(utterance);
                        }}
                    </script>
                    """
                    components.html(quiz_card_html, height=160)

                    # HU: Ha a gyermek rákattint a gombra (a gomb felirata fordított)
                    # EN: Triggered when child clicks answer button (translated label)
                    btn_label = _("Ez a(z) {word}").format(word=option['word'])
                    if st.button(btn_label, key=f"btn_{idx}"):
                        if option["is_correct"]:
                            st.balloons() # HU: Látványos animáció / EN: Fun balloons animation
                            st.success(_("🌟 Szuper! Ez a helyes válasz! 🌟"))
                        else:
                            st.error(_("❌ Próbáld meg még egyszer! ❌"))
        else:
            st.info(_("Kattints a bal oldalon a 'Vizuális anyag generálása' gombra a kezdéshez."))


elif selected_mode == "Text Simplifier":
    st.markdown(f"""
    <div class="banner">
        <h1>{_('✍️ VisualBridge – Könnyen Érthető Szövegegyszerűsítő')}</h1>
        <p>{_('Komplex szövegek átalakítása egyszerű tőmondatokká a könnyebb megértés érdekében.')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.agent.is_mock:
        st.warning(_("A Szövegegyszerűsítő használatához valós Gemini API kulcs szükséges."))
        st.info(_("Kérjük, adjon meg egy kulcsot a hozzáférés feloldásához."))

        page_api_key_input = st.text_input(
            _("Adja meg a Gemini API kulcsot itt:"),
            type="password",
            key="page_api_key_input"
        )
        if st.button(_("Kulcs mentése"), key="btn_save_page_key", type="primary"):
            if page_api_key_input.strip():
                import time
                st.session_state.user_api_key = page_api_key_input
                st.session_state.api_key_valid = None
                st.session_state.key_expiry_time = time.time() * 1000 + 30 * 60 * 1000
                st.session_state.agent.update_api_key(page_api_key_input)
                st.rerun()
    else:
        if "simplifier_input" not in st.session_state:
            st.session_state.simplifier_input = ""

        simplifier_input_text = st.text_area(
            _("Adja meg a bonyolult szöveget az egyszerűsítéshez:"),
            value=st.session_state.simplifier_input,
            height=200,
            key="simplifier_text_area"
        )
        simplify_btn = st.button(_("🚀 Szöveg egyszerűsítése"), key="btn_simplify_text", type="primary")

        if simplify_btn and simplifier_input_text:
            st.session_state.simplifier_input = simplifier_input_text
            with st.spinner(_("Az ágens dolgozik, egyszerűsíti a szöveget...")):
                try:
                    simplified_sentences = st.session_state.agent.simplify_text(simplifier_input_text, lang=lang_code)
                    st.session_state.simplified_result = simplified_sentences
                    st.success(_("Sikeres egyszerűsítés!"))
                except Exception as e:
                    st.error(_("Hiba történt a feldolgozás során: {e}").format(e=e))

        if "simplified_result" in st.session_state and st.session_state.simplified_result:
            st.write("---")
            st.subheader(_("Egyszerűsített mondatok"))

            for idx, sentence_text in enumerate(st.session_state.simplified_result):
                speech_lang = "hu-HU" if lang_code == "hu" else "en-US"
                btn_tooltip = _("🔊 Felolvasás")
                bootstrap_tag = f"<style>{bootstrap_css}</style>" if 'bootstrap_css' in os.environ or 'bootstrap_css' in globals() else ""

                card_html = f"""
                {bootstrap_tag}
                <style>
                    body {{
                        margin: 0;
                        padding: 4px;
                        background: transparent;
                    }}
                    .card {{
                        background-color: #e2e8f0 !important;
                        border-color: rgba(128, 128, 128, 0.15) !important;
                    }}
                    .speak-btn-custom {{
                        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
                        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
                        transition: transform 0.2s, filter 0.2s;
                        border: none !important;
                    }}
                    .speak-btn-custom:hover {{
                        transform: scale(1.08);
                        filter: brightness(1.1);
                    }}
                </style>
                <div class="card p-3 d-flex flex-row justify-content-between align-items-center border-start border-primary border-4 shadow-sm">
                    <div class="fs-5 fw-bold" style="color: #1e293b !important;">{sentence_text}</div>
                    <button class="btn btn-primary rounded-circle d-flex align-items-center justify-content-center speak-btn-custom"
                            style="width: 44px; height: 44px; min-width: 44px; min-height: 44px; font-size: 18px;"
                            id="speak-btn-simp-{idx}"
                            title="{btn_tooltip}">🔊</button>
                </div>
                <script>
                    document.getElementById('speak-btn-simp-{idx}').addEventListener('click', function() {{
                        window.speechSynthesis.cancel();
                        var utterance = new SpeechSynthesisUtterance({repr(sentence_text)});
                        var speechLang = '{speech_lang}';
                        utterance.lang = speechLang;
                        utterance.rate = {speech_rate};
                        var voices = window.speechSynthesis.getVoices();
                        var matchingVoice = null;
                        for (var i = 0; i < voices.length; i++) {{
                            if (voices[i].lang.toLowerCase() === speechLang.toLowerCase()) {{
                                matchingVoice = voices[i];
                                break;
                            }}
                        }}
                        if (!matchingVoice) {{
                            var langPrefix = speechLang.split('-')[0].toLowerCase();
                            for (var i = 0; i < voices.length; i++) {{
                                if (voices[i].lang.toLowerCase().startsWith(langPrefix)) {{
                                    matchingVoice = voices[i];
                                    break;
                                }}
                            }}
                        }}
                        if (matchingVoice) {{
                            utterance.voice = matchingVoice;
                        }}
                        window.speechSynthesis.speak(utterance);
                    }});
                </script>
                """
                components.html(card_html, height=95)

            st.write("---")
            st.subheader(_("Másolható egyszerűsített szöveg"))
            combined_text = "\n".join(st.session_state.simplified_result)
            st.text_area("", value=combined_text, height=150, key="copyable_simplified_output")



# ==============================================================================
# HU: Munkamenet időzítő és lejárati események (JS alapú modal overlay és rejtett gombok)
# EN: Session timer and expiration events (JS-based modal overlay and hidden buttons)
# ==============================================================================

# HU: Rejtett gombok a JavaScript események fogadásához (CSS segítségével elrejtve a DOM-ban)
# EN: Hidden buttons to capture JavaScript events (hidden in DOM using CSS)

if st.button("session_expire_trigger", key="btn_expire"):
    st.session_state.user_api_key = ""
    st.session_state.key_expiry_time = 0.0
    if "agent" in st.session_state:
        st.session_state.agent.update_api_key("")
    st.rerun()

if st.button("extend_5_trigger", key="btn_extend_5"):
    import time
    st.session_state.key_expiry_time = max(time.time() * 1000, st.session_state.key_expiry_time) + 5 * 60 * 1000
    st.rerun()

if st.button("extend_10_trigger", key="btn_extend_10"):
    import time
    st.session_state.key_expiry_time = max(time.time() * 1000, st.session_state.key_expiry_time) + 10 * 60 * 1000
    st.rerun()

if st.button("extend_15_trigger", key="btn_extend_15"):
    import time
    st.session_state.key_expiry_time = max(time.time() * 1000, st.session_state.key_expiry_time) + 15 * 60 * 1000
    st.rerun()

if st.button("extend_30_trigger", key="btn_extend_30"):
    import time
    st.session_state.key_expiry_time = max(time.time() * 1000, st.session_state.key_expiry_time) + 30 * 60 * 1000
    st.rerun()

# HU: Csak akkor ágyazzuk be a JS-t, ha van érvényes lejárati idő a sessionben
# EN: Embed the JS component only if there is a valid expiry time in the session
expiry_time = st.session_state.get("key_expiry_time", 0.0)

if expiry_time > 0.0:
    modal_title = _("Munkamenet meghosszabbítása")
    modal_desc = _("Az API kulcs munkamenete hamarosan lejár. Szeretné meghosszabbítani?")
    dismiss_txt = _("Elutasítás és bezárás")
    time_left_txt = _("Hátralévő idő: ") if lang_code == "hu" else "Time left: "

    js_code = f"""
    <style>
        .modal-backdrop {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(8px);
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: 'Outfit', 'Inter', sans-serif;
            animation: fadeIn 0.3s ease-out;
        }}
        .modal-box {{
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            width: 90%;
            max-width: 450px;
            padding: 30px;
            text-align: center;
            border: 1px solid rgba(226, 232, 240, 0.8);
            transform: scale(0.9);
            animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }}
        @media (prefers-color-scheme: dark) {{
            .modal-box {{
                background: #1e293b;
                color: #f8fafc;
                border-color: rgba(51, 65, 85, 0.8);
            }}
        }}
        .modal-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: #0f172a;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        @media (prefers-color-scheme: dark) {{
            .modal-title {{
                color: #f8fafc;
            }}
        }}
        .modal-desc {{
            font-size: 1rem;
            color: #475569;
            margin-bottom: 25px;
            line-height: 1.5;
        }}
        @media (prefers-color-scheme: dark) {{
            .modal-desc {{
                color: #cbd5e1;
            }}
        }}
        .timer-badge {{
            background: #fee2e2;
            color: #ef4444;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 1.1rem;
            display: inline-block;
            margin-bottom: 20px;
            border: 1px solid #fca5a5;
            animation: pulse 1s infinite;
        }}
        @media (prefers-color-scheme: dark) {{
            .timer-badge {{
                background: rgba(239, 68, 68, 0.2);
                color: #fca5a5;
                border-color: rgba(239, 68, 68, 0.4);
            }}
        }}
        .btn-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .btn-opt {{
            background: #f1f5f9;
            color: #334155;
            border: 1px solid #cbd5e1;
            padding: 12px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.95rem;
        }}
        .btn-opt:hover {{
            background: #e2e8f0;
            transform: translateY(-2px);
        }}
        @media (prefers-color-scheme: dark) {{
            .btn-opt {{
                background: #334155;
                color: #f1f5f9;
                border-color: #475569;
            }}
            .btn-opt:hover {{
                background: #475569;
            }}
        }}
        .btn-primary-action {{
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
            color: white !important;
            border: none !important;
        }}
        .btn-primary-action:hover {{
            filter: brightness(1.1);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }}
        .btn-dismiss {{
            background: transparent;
            color: #64748b;
            border: none;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: underline;
            margin-top: 10px;
            display: inline-block;
        }}
        .btn-dismiss:hover {{
            color: #475569;
        }}
        @media (prefers-color-scheme: dark) {{
            .btn-dismiss {{
                color: #94a3b8;
            }}
            .btn-dismiss:hover {{
                color: #cbd5e1;
            }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes scaleIn {{
            from {{ transform: scale(0.9); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
    </style>
    <div id="modal" class="modal-backdrop" style="display: none;">
        <div class="modal-box">
            <div class="modal-title">🔑 {modal_title}</div>
            <div class="modal-desc">{modal_desc}</div>
            <div id="timer-badge" class="timer-badge">00:60</div>
            <div class="btn-grid">
                <button class="btn-opt btn-primary-action" onclick="extend(5)">+5 Min</button>
                <button class="btn-opt btn-primary-action" onclick="extend(10)">+10 Min</button>
                <button class="btn-opt btn-primary-action" onclick="extend(15)">+15 Min</button>
                <button class="btn-opt btn-primary-action" onclick="extend(30)">+30 Min</button>
            </div>
            <button class="btn-dismiss" onclick="dismiss()">{dismiss_txt}</button>
        </div>
    </div>

    <script>
    const expiryTime = {expiry_time};
    const timeLeftTxt = "{time_left_txt}";

    function setIframeActive(active) {{
        const frame = window.frameElement;
        if (!frame) return;
        if (active) {{
            frame.style.position = 'fixed';
            frame.style.top = '0';
            frame.style.left = '0';
            frame.style.width = '100vw';
            frame.style.height = '100vh';
            frame.style.zIndex = '999999';
            frame.style.border = 'none';
            frame.style.background = 'transparent';
        }} else {{
            frame.style.position = 'absolute';
            frame.style.width = '0';
            frame.style.height = '0';
            frame.style.border = 'none';
        }}
    }}

    setIframeActive(false);

    if (expiryTime > 0) {{
        const dismissedExpiry = sessionStorage.getItem('dismissed_expiry');
        let isDismissed = (dismissedExpiry === String(expiryTime));

        const interval = setInterval(() => {{
            const now = Date.now();
            const timeLeft = expiryTime - now;

            if (timeLeft <= 0) {{
                clearInterval(interval);
                setIframeActive(false);
                triggerParentButton('session_expire_trigger');
                return;
            }}

            if (timeLeft <= 60000 && !isDismissed) {{
                setIframeActive(true);
                document.getElementById('modal').style.display = 'flex';

                const secondsLeft = Math.ceil(timeLeft / 1000);
                document.getElementById('timer-badge').innerText = timeLeftTxt + secondsLeft + 's';
            }} else {{
                document.getElementById('modal').style.display = 'none';
                setIframeActive(false);
            }}
        }}, 1000);
    }}

    function extend(minutes) {{
        setIframeActive(false);
        document.getElementById('modal').style.display = 'none';
        triggerParentButton('extend_' + minutes + '_trigger');
    }}

    function dismiss() {{
        setIframeActive(false);
        document.getElementById('modal').style.display = 'none';
        if (expiryTime > 0) {{
            sessionStorage.setItem('dismissed_expiry', String(expiryTime));
        }}
    }}

    function triggerParentButton(btnText) {{
        try {{
            const buttons = window.parent.document.querySelectorAll("button");
            for (const btn of buttons) {{
                if (btn.innerText.trim() === btnText) {{
                    btn.click();
                    break;
                }}
            }}
        }} catch (e) {{
            console.error("Error triggering parent button:", e);
        }}
    }}
    </script>
    """
    components.html(js_code, height=0, width=0)
