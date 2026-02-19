import json
import os

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
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        
        # Vérification si le fichier existe avant d'ouvrir
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Le fichier config.json est introuvable à {config_path}")
        
        with open(config_path, 'r') as config_file:
            telegram_API_keys = json.load(config_file)
            return True, telegram_API_keys['phone_number'], telegram_API_keys['api_id'], telegram_API_keys['api_hash']
    except FileNotFoundError as e:
        print(f"Erreur: {e}")
        print("config.json not found. You need to create a config.json file with your Telegram API keys.")
        print("Example:")
        print("{")
        print("    \"phone_number\": \"+33000000000\",")
        print("    \"api_id\": \"YOUR_API_ID\",")
        print("    \"api_hash\": \"YOUR_API_HASH\"")
        print("}")
        return False,None,None,None
        return False, None, None, None
    except json.JSONDecodeError:
        print("Erreur: Le fichier config.json n'est pas un JSON valide.")
        return False, None, None, None
    except KeyError as e:
        print(f"Erreur: La clé {e} est manquante dans le fichier config.json.")
        return False, None, None, None
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False, None, None, None
