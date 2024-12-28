import json

#le fichier config.json est au format suivant:
# {
#     "phone_number": "+33000000000",
#     "api_id": "YOUR_API_ID",
#     "api_hash": "YOUR_API_HASH"
# }
# ce fichier est necessaire car il contient les clefs d'API pour utiliser l'API de Telegram

def getTelegramApiKeys():
    """
    Get the Telegram API keys from the config.json file.
    """
    try:
        with open('config.json', 'r') as config_file:
            telegram_API_keys = json.load(config_file)
            return True,telegram_API_keys['phone_number'],telegram_API_keys['api_id'],telegram_API_keys['api_hash']

    except FileNotFoundError:
        print(FileNotFoundError)
        print("config.json not found. You need to create a config.json file with your Telegram API keys.")
        print("Example:")
        print("{")
        print("    \"phone_number\": \"+33000000000\",")
        print("    \"api_id\": \"YOUR_API_ID\",")
        print("    \"api_hash\": \"YOUR_API_HASH\"")
        print("}")
        return False,None,None,None
