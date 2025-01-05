import argparse
import requests
from enum import Enum
from debug import debug as dbg
from debug import niveau_log
from flask import Flask, request, jsonify
import json
from GetContentFromZt.GetContentFromZt import getContentFromZt

app = Flask(__name__)

# Exemple de requête : http://ip_adresse:5000/search?query=oui&type=series
@app.route("/search", methods=["GET"])
def search_api():
    """ Endpoint Flask pour effectuer une recherche """
    query = request.args.get("query")
    content_type = request.args.get("type")

    if not query:
        return jsonify({"error": "Le paramètre 'query' est requis."}), 400
    
    if not content_type:
        return jsonify({"error": "Le paramètre 'type' est requis."}), 400

    try:
        flag_result_ok, contenus = True, "kk" #getContentFromZt(query, content_type)
        if not flag_result_ok:
            return jsonify({"error": "Aucun résultat trouvé."}), 404
        else:
            return jsonify({"results": contenus}), 200
    except Exception as e:
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
