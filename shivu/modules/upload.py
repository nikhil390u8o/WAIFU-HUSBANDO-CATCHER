import urllib.request
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, sudo_users, CHARA_CHANNEL_ID, SUPPORT_CHAT

WRONG_FORMAT_TEXT = """Wrong ❌️ format... eg. /upload Img_url muzan-kibutsuji Demon-slayer 3

img_url character-name anime-name rarity-number

Use rarity number according to rarity Map:

rarity_map = 1 (⚪️ Common), 2 (🟣 Rare), 3 (🟡 Legendary), 4 (🟢 Medium), 5 (💮 Special edition)"""

# In-memory storage
characters_data = {}  # {id: character_dict}
sequence_counters = {"character_id": 0}


def get_next_sequence_number(sequence_name: str) -> str:
    sequence_counters[sequence_name] += 1
    return str(sequence_counters[sequence_name]).zfill(2)


async def upload(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("Ask My Owner...")
        return

    try:
        args = context.args
        if len(args) != 4:
            await update.message.reply_text(WRONG_FORMAT_TEXT)
            return

        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        try:
            urllib.request.urlopen(args[0])
        except:
            await update.message.reply_text("Invalid URL.")
            return

        rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium", 5: "💮 Special edition"}
        try:
            rarity = rarity_map[int(args[3])]
        except KeyError:
            await update.message.reply_text("Invalid rarity. Please use 1,2,3,4,5.")
            return

        id = get_next_sequence_number("character_id")
        character = {
            "img_url": args[0],
            "name": character_name,
            "anime": anime,
            "rarity": rarity,
            "id": id
        }

        try:
            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=args[0],
                caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n'
                        f'<b>Rarity:</b> {rarity}\n<b>ID:</b> {id}\n'
                        f'Added by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
                parse_mode='HTML'
            )
            character['message_id'] = message.message_id
        except:
            update.effective_message.reply_text("Character Added but channel may not exist, consider adding one.")

        characters_data[id] = character
        await update.message.reply_text("CHARACTER ADDED....")
    except Exception as e:
        await update.message.reply_text(f"Character Upload Unsuccessful. Error: {str(e)}\nForward to: {SUPPORT_CHAT}")


async def delete(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("Ask my Owner to use this Command...")
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("Incorrect format. Use: /delete ID")
            return

        character = characters_data.pop(args[0], None)

        if character and "message_id" in character:
            try:
                await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
            except:
                pass

        await update.message.reply_text("Deleted Successfully.")
    except Exception as e:
        await update.message.reply_text(str(e))


async def update(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Incorrect format. Use: /update id field new_value")
            return

        character = characters_data.get(args[0])
        if not character:
            await update.message.reply_text("Character not found.")
            return

        valid_fields = ["img_url", "name", "anime", "rarity"]
        if args[1] not in valid_fields:
            await update.message.reply_text(f"Invalid field. Use: {', '.join(valid_fields)}")
            return

        if args[1] in ["name", "anime"]:
            new_value = args[2].replace("-", " ").title()
        elif args[1] == "rarity":
            rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium", 5: "💮 Special edition"}
            try:
                new_value = rarity_map[int(args[2])]
            except KeyError:
                await update.message.reply_text("Invalid rarity. Use 1,2,3,4,5.")
                return
        else:
            new_value = args[2]

        character[args[1]] = new_value

        # Update message in channel if exists
        if "message_id" in character:
            if args[1] == "img_url":
                try:
                    await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character['message_id'])
                    message = await context.bot.send_photo(
                        chat_id=CHARA_CHANNEL_ID,
                        photo=new_value,
                        caption=f'<b>Character Name:</b> {character["name"]}\n<b>Anime Name:</b> {character["anime"]}\n'
                                f'<b>Rarity:</b> {character["rarity"]}\n<b>ID:</b> {character["id"]}\n'
                                f'Updated by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
                        parse_mode='HTML'
                    )
                    character['message_id'] = message.message_id
                except:
                    pass
            else:
                try:
                    await context.bot.edit_message_caption(
                        chat_id=CHARA_CHANNEL_ID,
                        message_id=character['message_id'],
                        caption=f'<b>Character Name:</b> {character["name"]}\n<b>Anime Name:</b> {character["anime"]}\n'
                                f'<b>Rarity:</b> {character["rarity"]}\n<b>ID:</b> {character["id"]}\n'
                                f'Updated by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
                        parse_mode='HTML'
                    )
                except:
                    pass

        await update.message.reply_text("Updated Done in memory (no DB). Channel update may take some time.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


# Add handlers
application.add_handler(CommandHandler('upload', upload, block=False))
application.add_handler(CommandHandler('delete', delete, block=False))
application.add_handler(CommandHandler('update', update, block=False))
