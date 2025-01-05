from telethon.sync import TelegramClient
import re
from GetZtLink.GetTelegramApiKeys import getTelegramApiKeys
import asyncio
import time

# if session_name.session file exists, it will be used to login without asking for a code and phone number

group_username = 'ZT_officiel'  # Telegram channel name

def extractLinkFromTelegramMessage(message):
    """
    Extract a link from a Telegram message.
    """
    link_regex = r'https?://[^\s]+'
    match = re.search(link_regex, message)
    return match.group(0) if match else None

def getZtLinkFromTelegram():
    """
    Get the last link from a Telegram group.
    """

    # Get the Telegram API keys
    print("je suis la 1")
    success, phone_number, api_id, api_hash = getTelegramApiKeys()
    print("je suis la 2")
    if not success:
        return False, "GetTelegramApiKeys failed"

    print("je suis la 3")
    time.sleep(2)  # Ajoute une pause pour vérifier l'état avant la connexion
    # Ajout de la boucle d'événements explicite
    loop = asyncio.get_event_loop()
    
    # Connexion et récupération des messages via TelegramClient
    async def fetch_data():
        try:
            print("je suis la 4")
            client = TelegramClient('session_name', api_id, api_hash)
            await client.start()
            print("je suis la 5")
            async for message in client.iter_messages(group_username, limit=2):
                if message.text:
                    link = extractLinkFromTelegramMessage(message.text)
                    if link:
                        print("Link found:", link)
                        return True, link
            return False, "No link found in the last 2 messages."
        except Exception as e:
            print(f"Error: {e}")
            return False, None

    # Exécution de la fonction asynchrone dans la boucle d'événements
    return loop.run_until_complete(fetch_data())