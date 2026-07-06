# Ismert Problémák és Megoldások / Known Issues and Troubleshooting

## 1. Web Speech API (Text-to-Speech) Hangproblémák / Audio Issues

### HU: Miért nincs hang egyes böngészőkben?

A hangfelolvasás a böngészők beépített **Web Speech API** (JavaScript `window.speechSynthesis`) technológiájára támaszkodik. Az, hogy egyes böngészőkben nem hallható hang, az alábbi okok miatt fordulhat elő:

1. **Hiányzó nyelvi csomagok (TTS hangok)**: A Web Speech API nem távoli szerverről játssza le a hangot, hanem a felhasználó eszközére és böngészőjébe telepített felolvasó hangokat használja. Ha az eszközön vagy a böngészőben nincs telepítve/engedélyezve magyar nyelvű felolvasó hangcsomag, a böngésző nem tudja megszólaltatni a szöveget.
2. **Aszinkron hangbetöltés**: Sok böngészőben (pl. Chrome) a telepített hangok listája aszinkron módon, késleltetve töltődik be az oldal megnyitása után. Ha a gombra kattintás pillanatában a böngésző még nem fejezte be a hangok betöltését, a hanglista üres lehet.
3. **Autoplay / Interakciós korlátozások**: A modern böngészők biztonsági okokból letiltják az automatikus hanghatásokat (Autoplay Policy) mindaddig, amíg a felhasználó közvetlenül interakcióba nem lép a dokumentummal (kattintás).
4. **Iframe Sandbox korlátozások**: Mivel a kód egy iframe-ben fut, egyes böngészők biztonsági okokból blokkolják a beágyazott elemek hozzáférését a beszédmotorhoz.

---

### EN: Why is there no sound in some browsers?

The text-to-speech features rely on the browser-native **Web Speech API** (JavaScript `window.speechSynthesis`). If audio playback fails in a browser, it is typically caused by one of the following reasons:

1. **Missing TTS Language Packs**: The Web Speech API does not steam audio from a remote server; instead, it uses the text-to-speech voices installed on the host device. If a Hungarian (or the target language) voice pack is not installed/enabled on your system or browser, it will remain silent.
2. **Asynchronous Voice Loading**: In many browsers (like Chrome), the list of available voices is loaded asynchronously after the page opens. If you trigger the text-to-speech button before the browser finishes loading these voices, the speech queue might remain empty.
3. **Autoplay/Interaction Policies**: Modern browsers restrict automatic audio playback (Autoplay Policy) until the user has directly interacted with the document (clicked/tapped).
4. **Iframe Sandbox Restrictions**: Because the component is rendered inside an iframe, some browser security policies block sandboxed frames from accessing the system's speech synthesis engine.
