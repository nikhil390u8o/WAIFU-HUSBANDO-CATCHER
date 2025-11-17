import re
import time
from html import escape
from cachetools import TTLCache

from telegram import Update, InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, CallbackContext

# In-memory storage instead of MongoDB
all_characters_data = []  # List of all character dicts
user_data_store = {}      # {user_id: {"id": ..., "first_name": ..., "characters": [...] }}

# Caches
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    if query.startswith('collection.'):
        user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
        if user_id.isdigit():
            if user_id in user_collection_cache:
                user = user_collection_cache[user_id]
            else:
                user = user_data_store.get(int(user_id))
                user_collection_cache[user_id] = user

            if user:
                all_characters = list({v['id']: v for v in user['characters']}.values())
                if search_terms:
                    regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                    all_characters = [c for c in all_characters if regex.search(c['name']) or regex.search(c['anime'])]
            else:
                all_characters = []
        else:
            all_characters = []
    else:
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = [c for c in all_characters_data if regex.search(c['name']) or regex.search(c['anime'])]
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = all_characters_data
                all_characters_cache['all_characters'] = all_characters

    characters = all_characters[offset:offset+50]
    if len(characters) > 50:
        characters = characters[:50]
        next_offset = str(offset + 50)
    else:
        next_offset = str(offset + len(characters))

    results = []
    for character in characters:
        global_count = sum(character['id'] in [c['id'] for u in user_data_store.values() for c in u['characters']])
        anime_characters = sum(c['anime'] == character['anime'] for c in all_characters_data)

        if query.startswith('collection.') and user_id.isdigit() and user:
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
            caption = f"<b>Look At <a href='tg://user?id={user['id']}'>{escape(user.get('first_name', user['id']))}</a>'s Character</b>\n\n" \
                      f"🌸: <b>{character['name']} (x{user_character_count})</b>\n" \
                      f"🏖️: <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n" \
                      f"<b>{character['rarity']}</b>\n\n<b>🆔️:</b> {character['id']}"
        else:
            caption = f"<b>Look At This Character !!</b>\n\n" \
                      f"🌸:<b> {character['name']}</b>\n" \
                      f"🏖️: <b>{character['anime']}</b>\n" \
                      f"<b>{character['rarity']}</b>\n" \
                      f"🆔️: <b>{character['id']}</b>\n\n" \
                      f"<b>Globally Guessed {global_count} Times...</b>"

        results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

# Add handler to your application
application.add_handler(InlineQueryHandler(inlinequery, block=False))
