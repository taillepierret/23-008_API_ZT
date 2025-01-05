from telethon.sync import TelegramClient
import re
from GetZtLink.GetTelegramApiKeys import getTelegramApiKeys

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
        return False,"GetTelegramApiKeys failed"

    print("je suis la 3")
    with TelegramClient('session_name', api_id, api_hash).start(phone_number) as client: 
        
        # Access recent messages from the group
        print("je suis la 4")
        for message in client.iter_messages(group_username, limit=2):
            if message.text:
                link = extractLinkFromTelegramMessage(message.text)
                if link:
                    print("Link found:", link)
                    return True,link
        return False,"No link found in the last 2 messages."