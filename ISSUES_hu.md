# Ismert Problémák és Hibaelhárítás

## 1. Web Speech API (Text-to-Speech) Hangproblémák

### Miért nincs hang egyes böngészőkben?

A hangfelolvasás a böngészők beépített **Web Speech API** (JavaScript `window.speechSynthesis`) technológiájára támaszkodik. Az, hogy egyes böngészőkben nem hallható hang, az alábbi okok miatt fordulhat elő:

1. **Hiányzó nyelvi csomagok (TTS hangok)**: A Web Speech API nem távoli szerverről játssza le a hangot, hanem a felhasználó eszközére és böngészőjébe telepített felolvasó hangokat használja. Ha az eszközön vagy a böngészőben nincs telepítve/engedélyezve magyar nyelvű felolvasó hangcsomag, a böngésző nem tudja megszólaltatni a szöveget.
2. **Aszinkron hangbetöltés**: Sok böngészőben (pl. Chrome) a telepített hangok listája aszinkron módon, késleltetve töltődik be az oldal megnyitása után. Ha a gombra kattintás pillanatában a böngésző még nem fejezte be a hangok betöltését, a hanglista üres lehet.
3. **Autoplay / Interakciós korlátozások**: A modern böngészők biztonsági okokból letiltják az automatikus hanghatásokat (Autoplay Policy) mindaddig, amíg a felhasználó közvetlenül interakcióba nem lép a dokumentummal (kattintás).
4. **Iframe Sandbox korlátozások**: Mivel a kód egy iframe-ben fut, egyes böngészők biztonsági okokból blokkolják a beágyazott elemek hozzáférését a beszédmotorhoz.
