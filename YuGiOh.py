import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from googletrans import Translator
from thefuzz import process

TOKEN = "7286284254:AAEQBmQPxEgTcOKXrNzet2FWwAfmjIKnHvQ"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
translator = Translator()
user_languages = {}

LANGUAGES = {
    "fr": "🇫🇷 Français",
    "en": "🇬🇧 English",
    "ar": "🇸🇦 العربية",
    "ja": "🇯🇵 日本語",
    "it": "🇮🇹 Italiano",
    "es": "🇪🇸 Español",
    "pt": "🇵🇹 Português",
    "ru": "🇷🇺 Русский"
}

@bot.message_handler(commands=["start"])
def start(message):
    markup = InlineKeyboardMarkup()
    lang_keys = list(LANGUAGES.items())

    for i in range(0, len(lang_keys), 2):
        row = [InlineKeyboardButton(lang_keys[i][1], callback_data=f"lang_{lang_keys[i][0]}")]
        if i + 1 < len(lang_keys):
            row.append(InlineKeyboardButton(lang_keys[i + 1][1], callback_data=f"lang_{lang_keys[i + 1][0]}"))
        markup.row(*row)

    bot.send_message(
        message.chat.id,
        "🌍 Please choose your language:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    lang_code = call.data.split("_")[1]
    user_languages[call.from_user.id] = lang_code
    bot.answer_callback_query(call.id, f"Language set to {LANGUAGES[lang_code]}")
    bot.send_message(call.message.chat.id, f"✅ Your language is now {LANGUAGES[lang_code]}.")

def get_all_card_names():
    """Récupère tous les noms des cartes Yu-Gi-Oh en anglais."""
    url = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    data = response.json().get("data", [])
    return [c["name"] for c in data]  

ALL_CARDS = get_all_card_names()  # Chargement initial des cartes

def rechercher_carte(nom):
    """Recherche une carte Yu-Gi-Oh en trouvant le nom le plus proche en anglais."""
    if not ALL_CARDS:
        return None

    translated_name = translator.translate(nom, dest="en").text

    best_match, score = process.extractOne(translated_name, ALL_CARDS)

    if score < 70:
        return None

    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={best_match}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json()
    if "data" not in data:
        return None

    carte = data["data"][0]
    image = carte["card_images"][0]["image_url"]
    titre = carte["name"]
    description = carte.get("desc", "No description available.")

    return {"image": image, "titre": titre, "description": description}

@bot.message_handler(commands=["search"])
def search_card(message):
    query = message.text.replace("/search", "").strip()

    if not query:
        bot.send_message(message.chat.id, "❌ Please provide a card name. Example: `/search Dark Magician`")
        return

    resultats = rechercher_carte(query)
    if not resultats:
        bot.send_message(message.chat.id, "❌ No matching card found.")
        return

    user_lang = user_languages.get(message.from_user.id, "en")
    traduction = translator.translate(resultats["description"], dest=user_lang).text

    bot.send_photo(
        message.chat.id,
        resultats["image"],
        caption=f"<b>{resultats['titre']}</b>\n\n{traduction}",
        parse_mode="HTML"
    )

@bot.inline_handler(lambda query: len(query.query) > 2)
def inline_query(query):
    resultats = rechercher_carte(query.query)
    if not resultats:
        return

    user_lang = user_languages.get(query.from_user.id, "en")
    traduction = translator.translate(resultats["description"], dest=user_lang).text

    photo = telebot.types.InlineQueryResultPhoto(
        id="1",
        photo_url=resultats["image"],
        thumbnail_url=resultats["image"],
        title=resultats["titre"],
        caption=f"<b>{resultats['titre']}</b>\n\n{traduction}",
        parse_mode="HTML"
    )
    bot.answer_inline_query(query.id, [photo])

bot.infinity_polling()
