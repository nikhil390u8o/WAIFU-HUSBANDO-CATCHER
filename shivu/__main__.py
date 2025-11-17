import importlib
import time
import random
import re
import asyncio
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, LOGGER
from shivu.modules import ALL_MODULES


locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}


for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)


last_user = {}
warned_users = {}
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 100)
        else:
            message_frequency = 100

        
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
            
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    
                    await update.message.reply_text(f"⚠️ Don't Spam {update.effective_user.first_name}...\nYour Messages Will be ignored for 10 Minutes...")
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

    
        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

    
        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            
            message_counts[chat_id] = 0
            
async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    all_characters = list(await collection.find({}).to_list(length=None))
    
    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"""A New {character['rarity']} Character Appeared...\n/guess Character Name and add in Your Harem""",
        parse_mode='Markdown')


async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌️ Already Guessed By Someone.. Try Next Time Bruhh ')
        return
import importlib
import time
import random
import re
import asyncio
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, LOGGER
from shivu.modules import ALL_MODULES

# In-memory structures for bot state
locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
last_user = {}
warned_users = {}

# Load all modules
for module_name in ALL_MODULES:
    importlib.import_module("shivu.modules." + module_name)


def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        message_frequency = user_totals_collection.get(chat_id, {}).get('message_frequency', 100)

        # Spam protection
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    await update.message.reply_text(
                        f"⚠️ Don't Spam {update.effective_user.first_name}...\nYour messages will be ignored for 10 minutes..."
                    )
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # Count messages
        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1

        # Send new character if threshold reached
        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            message_counts[chat_id] = 0


async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)

    all_characters = list(collection.values())

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    remaining = [c for c in all_characters if c['id'] not in sent_characters[chat_id]]
    if not remaining:
        return

    character = random.choice(remaining)
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character
    first_correct_guesses.pop(chat_id, None)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"A New {character['rarity']} Character Appeared...\n/guess Character Name and add it to your Harem",
        parse_mode='Markdown'
    )


async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text('❌️ Already Guessed By Someone.. Try Next Time!')
        return

    guess_text = ' '.join(context.args).lower() if context.args else ''
    if "()" in guess_text or "&" in guess_text:
        await update.message.reply_text("You can't use these characters in your guess ❌️")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()
    if sorted(name_parts) == sorted(guess_text.split()) or any(part == guess_text for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        # Update user collection
        user_data = user_collection.get(user_id)
        if not user_data:
            user_collection[user_id] = {
                'id': user_id,
                'username': getattr(update.effective_user, 'username', ''),
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
                'favorites': []
            }
        else:
            # Update username/first_name if changed
            user_data['username'] = getattr(update.effective_user, 'username', user_data.get('username', ''))
            user_data['first_name'] = update.effective_user.first_name
            if 'characters' not in user_data:
                user_data['characters'] = []
            user_data['characters'].append(last_characters[chat_id])

        # Update group totals
        group_data = group_user_totals_collection.setdefault(chat_id, {})
        group_user = group_data.setdefault(user_id, {'username': getattr(update.effective_user, 'username', ''), 'first_name': update.effective_user.first_name, 'count': 0})
        group_user['count'] += 1

        # Update top global groups
        top_group = top_global_groups_collection.setdefault(chat_id, {'group_name': update.effective_chat.title, 'count': 0})
        top_group['count'] += 1
        top_group['group_name'] = update.effective_chat.title

        # Send confirmation
        keyboard = [[InlineKeyboardButton(f"See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
        await update.message.reply_text(
            f'<b><a href="tg://user?id={user_id}">{escape(update.effective_user.first_name)}</a></b> guessed a new character ✅\n\n'
            f'NAME: <b>{last_characters[chat_id]["name"]}</b>\n'
            f'ANIME: <b>{last_characters[chat_id]["anime"]}</b>\n'
            f'RARITY: <b>{last_characters[chat_id]["rarity"]}</b>\n\n'
            'This character has been added to your harem. Use /harem to see your collection.',
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text('Please write the correct character name ❌️')


async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text('Please provide a character ID.')
        return

    character_id = context.args[0]
    user_data = user_collection.get(user_id)
    if not user_data or 'characters' not in user_data:
        await update.message.reply_text('You have not guessed any characters yet.')
        return

    character = next((c for c in user_data['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This character is not in your collection.')
        return

    user_data['favorites'] = [character_id]
    await update.message.reply_text(f'Character {character["name"]} has been added to your favorites.')


def main() -> None:
    application.add_handler(CommandHandler(["guess", "protecc", "collect", "grab", "hunt"], guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()
    application.add_handler(CommandHandler(["guess", "protecc", "collect", "grab", "hunt"], guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))

    application.run_polling(drop_pending_updates=True)
    
if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()

