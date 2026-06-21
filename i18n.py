# HU: i18n modul a fordítások kezeléséhez
# EN: i18n module for handling translations
import os

class TranslationManager:
    """
    HU: Fordításokat kezelő osztály, amely beolvassa a PO fájlokat és lefordítja a szövegeket.
    EN: Translation manager class that loads PO files and translates texts.
    """
    def __init__(self, langs_dir="langs"):
        # HU: Inicializálja a fordítási könyvtárat és betölti a nyelveket
        # EN: Initialize the translation directory and load languages
        self.langs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), langs_dir)
        self.translations = {}
        self.current_lang = "hu"
        self.load_translations()

    def load_translations(self):
        """
        HU: Beolvassa az összes PO fájlt a langs könyvtárból.
        EN: Reads all PO files from the langs directory.
        """
        if not os.path.exists(self.langs_dir):
            return

        for file_name in os.listdir(self.langs_dir):
            if file_name.endswith(".po"):
                lang = file_name[:-3]
                file_path = os.path.join(self.langs_dir, file_name)
                self.translations[lang] = self.parse_po(file_path)

    def parse_po(self, file_path):
        """
        HU: Feldolgoz egy egyedi PO fájlt és visszaadja a fordítási szótárat.
        EN: Parses an individual PO file and returns the translation dictionary.
        """
        trans = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # HU: Elemzési állapot tárolása
            # EN: Parsing state storage
            state = {
                "current_key": None,
                "current_val": None,
                "in_msgid": False,
                "in_msgstr": False,
                "trans": trans
            }

            for line in lines:
                self._parse_line(line, state)

            # HU: Elmenti az utolsó bejegyzést a fájl végén
            # EN: Save the last entry at the end of the file
            self._save_entry(state["trans"], state["current_key"], state["current_val"])

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        return trans

    def _parse_line(self, line, state):
        """
        HU: Feldolgoz egy egyedi sort a PO fájlból és frissíti a megadott állapotot.
        EN: Processes a single line from the PO file and updates the given state.
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return

        if line.startswith('msgid '):
            self._save_entry(state["trans"], state["current_key"], state["current_val"])
            state["current_key"] = self._clean_quotes(line[6:])
            state["current_val"] = None
            state["in_msgid"] = True
            state["in_msgstr"] = False
        elif line.startswith('msgstr '):
            state["current_val"] = self._clean_quotes(line[7:])
            state["in_msgid"] = False
            state["in_msgstr"] = True
        elif line.startswith('"') and line.endswith('"'):
            self._append_string_segment(line, state)

    def _append_string_segment(self, line, state):
        """
        HU: Összefűzi a többsoros sztring szegmenst a megfelelő kulccsal vagy értékkel.
        EN: Appends a multiline string segment to the appropriate key or value.
        """
        cleaned = self._clean_quotes(line)
        if state["in_msgid"]:
            state["current_key"] += cleaned
        elif state["in_msgstr"]:
            state["current_val"] += cleaned

    def _save_entry(self, trans, current_key, current_val):
        """
        HU: Elment egy egyedi fordítási kulcs-érték párt a szótárba.
        EN: Saves an individual translation key-value pair to the dictionary.
        """
        if current_key is not None and current_val is not None:
            key = self._unescape(current_key)
            val = self._unescape(current_val)
            if key:  # HU: Kihagyja a fejlécet / EN: Skip header (msgid "")
                trans[key] = val

    def _clean_quotes(self, s):
        """
        HU: Eltávolítja az elejéről és végéről a szóközöket és az idézőjeleket.
        EN: Removes whitespace and wrapping quotes from a line segment.
        """
        s = s.strip()
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        return s

    def _unescape(self, s):
        """
        HU: Feloldja a PO fájlokban lévő escape-karaktereket.
        EN: Unescapes standard escape sequences used in PO files.
        """
        return (s.replace("\\n", "\n")
                 .replace('\\"', '"')
                 .replace("\\\\", "\\")
                 .replace("\\t", "\t"))

    def set_language(self, lang):
        """
        HU: Beállítja az aktív nyelvet.
        EN: Sets the active language.
        """
        self.current_lang = lang

    def gettext(self, text):
        """
        HU: Visszaadja a megadott szöveg fordítását, vagy az eredetit, ha nincs találat.
        EN: Returns the translation of the given text, or the original if not found.
        """
        lang_trans = self.translations.get(self.current_lang, {})
        return lang_trans.get(text, text)
