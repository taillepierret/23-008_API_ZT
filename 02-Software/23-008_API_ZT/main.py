import argparse
import requests
from enum import Enum
from debug import debug as dbg
from debug import niveau_log
from flask import Flask, request, jsonify
import json
import asyncio
from GetContentFromZt.GetContentFromZt import getContentFromZt

app = Flask(__name__)  # Initialiser l'application Flask

# Exemple de requête : http://ip_adresse:5000/search?query=oui&type=series
@app.route("/search", methods=["GET"])
def search_api():
    # Création de l'event loop explicitement dans ce thread
    thread = threading.Thread(target=run_async_function)
    thread.start()
    thread.join()

    # Votre code de recherche
    try:
        flag_result_ok, contenus = getContentFromZt(query, content_type)
        if not flag_result_ok:
            return jsonify({"error": "Aucun résultat trouvé."}), 404
        else:
            return jsonify({"results": contenus}), 200
    except Exception as e:
        dbg.debug_print(niveau_log.ERREUR, f"Erreur API : {e}", True)
        return jsonify({"error": str(e)}), 500


def main():
    # Définir les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Choisissez le mode d'exécution.")
    parser.add_argument("mode", nargs="?", choices=["test", "server"], default="test", 
                        help="Mode d'exécution : 'test' ou 'server' (par défaut 'test')")
    args = parser.parse_args()

    # Initialiser le debug
    debug = dbg()
    dbg.set_log_level(niveau_log.VERBOSE)

    if args.mode == "test":
        # Mode Test : Tester la fonction getContentFromZt
        flag_result_ok, contenus = getContentFromZt("oui", "series")
        if not flag_result_ok:
            dbg.debug_print(niveau_log.ERREUR, "Aucun résultat trouvé.", True)
        else:
            dbg.debug_print(niveau_log.LOG, contenus, True)
    elif args.mode == "server":
        # Mode Serveur : Lancer Flask
        app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
