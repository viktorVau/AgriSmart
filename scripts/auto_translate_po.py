# scripts/auto_translate_po.py
import polib
from googletrans import Translator

LANGUAGES = ['fr', 'yo', 'ha', 'ig', 'sw', 'zu']
BASE_LOCALE_DIR = 'locale'
translator = Translator()

def translate_po_file(lang):
    po_path = f'{BASE_LOCALE_DIR}/{lang}/LC_MESSAGES/django.po'
    po = polib.pofile(po_path)

    for entry in po:
        if not entry.translated():
            translated = translator.translate(entry.msgid, src='en', dest=lang)
            entry.msgstr = translated.text
    
    po.save()
    print(f"{lang} translation completed.")

if __name__ == '__main__':
    for lang in LANGUAGES:
        translate_po_file(lang)
