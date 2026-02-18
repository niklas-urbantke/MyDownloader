"""
Quick Patch: Aktualisiert die _check_environment Funktion
Einfach ausführen: python patch_status_update.py
"""

import re

FILE_PATH = "app_modern.py"

# Lese Datei
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Suche und ersetze die _check_environment Funktion
old_function = '''    def _check_environment(self):
        """Prüft Node.js und FFmpeg"""
        check_and_setup_nodejs()
        check_ffmpeg()'''

new_function = '''    def _check_environment(self):
        """Prüft Node.js und FFmpeg"""
        nodejs_ok = check_and_setup_nodejs()
        ffmpeg_ok = check_ffmpeg()
        self.update_system_status(nodejs_ok, ffmpeg_ok)'''

if old_function in content:
    content = content.replace(old_function, new_function)
    
    # Schreibe zurück
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Patch erfolgreich angewendet!")
    print("Die System-Status-Labels werden jetzt korrekt aktualisiert.")
else:
    print("⚠️ Funktion wurde bereits aktualisiert oder nicht gefunden.")
