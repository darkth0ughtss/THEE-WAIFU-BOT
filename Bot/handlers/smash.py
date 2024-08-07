from pyrogram import Client, filters
from ..database import get_drop, update_smashed_image, update_drop, get_character_details
from pyrogram.types import Message

async def smash_image(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide the character name.")
        return

    guessed_name = " ".join(message.command[1:]).strip().lower()
    group_id = message.chat.id
    user_id = message.from_user.id

    # Retrieve the last drop for the group
    drop = await get_drop(group_id)

    if not drop:
        await message.reply("No image has been dropped in this group.")
        return

    # Check if the image has already been smashed
    if drop["smashed_by"]:
        # Fetch the user who smashed the character
        smashed_user = await client.get_users(drop["smashed_by"])
        smashed_user_mention = smashed_user.mention if smashed_user else f"User ID: {drop['smashed_by']}"

        await message.reply(f"**ℹ Last character was already smashed by {smashed_user_mention} !!**")
        return

    # Check if the guessed name is correct
    if guessed_name == drop["image_name"].strip().lower():
        # Fetch additional details from the Characters collection
        character = await get_character_details(drop["image_id"])
        if not character:
            await message.reply("**Character details not found in the database.**")
            return

        # Update the smashed image in the user's collection
        await update_smashed_image(user_id, drop["image_id"], message.from_user.mention)

        # Update the drop to indicate it has been smashed
        await update_drop(group_id, drop["image_id"], drop["image_name"], drop["image_url"], smashed_by=user_id)

        # Send success message with character details
        rarity_sign = character.get("rarity_sign", "")
        rarity = character.get("rarity", "")
        anime = character.get("anime", "")
        await message.reply(
            f"**🎯 You Successfully Smashed A Character !!\n\n"
            f"✨ Name : {drop['image_name']}\n"
            f"{rarity_sign} Rarity : {rarity}\n"
            f"🍁 Anime : {anime}\n\n"
            f"You Can Take A Look At Your Collection Using /smashes**"
        )
    else:
        # Send incorrect guess message with a link to the dropped image
        dropped_image_link = drop.get("dropped_image_link", "")
        await message.reply(
            f"**❌ Incorrect guess : {guessed_name}!!**\n\n"
            f"**Please try again [🔼]({dropped_image_link})**",
            disable_web_page_preview=True
        )

