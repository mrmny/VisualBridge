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


# HU: Nyelvválasztó a beállításokhoz
# EN: Language selector for settings
selected_lang_label = st.sidebar.selectbox("Language / Nyelv", ["Magyar", "English"])
lang_code = "hu" if selected_lang_label == "Magyar" else "en"
st.session_state.trans_mgr.set_language(lang_code)

if st.session_state.current_lang != lang_code:
    st.session_state.current_lang = lang_code
    st.session_state.result = None


# HU: Fordítási segédfüggvény
# EN: Translation helper function
def _(text):
    return st.session_state.trans_mgr.gettext(text)

# HU: Premium vizuális stílusok és Bootstrap beillesztése
# EN: Premium visual styles and Bootstrap stylesheet injection
bootstrap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "bootstrap", "css", "bootstrap.min.css")
if os.path.exists(bootstrap_path):
    with open(bootstrap_path, "r", encoding="utf-8") as f:
        bootstrap_css = f.read()
    st.markdown(f"<style>{bootstrap_css}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
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
        color: var(--text-color);
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
        background-color: var(--background-color) !important;
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
            "dist1": "víz",
            "dist2": CHOCOLATE_HU,
            "icon": "👦"
        },
        "en": {
            "text": "The red car goes fast, but the yellow bus stops.",
            "correct": "car",
            "dist1": "water",
            "dist2": "chocolate",
            "icon": "👦"
        }
    },
    "girl": {
        "hu": {
            "text": "A kislány a szép babával játszik, miközben a pöttyös labda elgurul.",
            "correct": "baba",
            "dist1": "víz",
            "dist2": CHOCOLATE_HU,
            "icon": "👧"
        },
        "en": {
            "text": "The little girl plays with the beautiful doll, while the polka dot ball rolls away.",
            "correct": "doll",
            "dist1": "water",
            "dist2": "chocolate",
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
    correct_w = st.text_input(_("Helyes válasz szava (pl. mi kell a fának?):"), value=template["correct"], key=correct_key)
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
            except Exception as e:
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
                /* Custom styles for gradient, shadows, hover animations and dark mode support */
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
                @media (prefers-color-scheme: dark) {{
                    .card {{
                        background-color: #1e293b !important;
                        border-color: #334155 !important;
                    }}
                    .card div {{
                        color: #f8fafc !important;
                    }}
                }}
            </style>
            <div class="card p-3 d-flex flex-row justify-content-between align-items-center border-start border-primary border-4 shadow-sm">
                <div class="fs-5 fw-bold text-dark">{sentence_text}</div>
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

            # HU: Kirakjuk egymás mellé a mondathoz tartozó piktogramokat
            # EN: Place pictograms side-by-side below the sentence
            tokens = item.get("tokens_with_pics", [])
            if tokens:
                # HU: Dinamikus oszlopok a képeknek a mondaton belül
                # EN: Dynamic columns for images inside the sentence
                img_cols = st.columns(len(tokens))
                for idx, token in enumerate(tokens):
                    with img_cols[idx]:
                        # HU: Megjelenítjük a piktogram kártyát lebegő stílussal
                        # EN: Render the pictogram card with hover styling
                        st.markdown(f"""
                        <div class="pic-card">
                            <img src="{token['image_url']}" style="width: 100px; height: 100px; object-fit: contain; margin-bottom: 8px;" />
                            <div class="pic-label">{token['word'].upper()}</div>
                        </div>
                        """, unsafe_allow_html=True)
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
                st.markdown(f"""
                <div class="pic-card" style="margin-bottom: 15px;">
                    <img src="{option['url']}" style="width: 120px; height: 120px; object-fit: contain;" />
                </div>
                """, unsafe_allow_html=True)
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
