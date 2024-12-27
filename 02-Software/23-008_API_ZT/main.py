import requests
from enum import Enum
from debug import debug as dbg
from debug import niveau_log
from flask import Flask, request, jsonify
import json
from GetContentFromZt.GetContentFromZt import getContentFromZt




app = Flask(__name__)  # Initialiser l'application Flask


#exemple de requete: http://ip_adresse:5000/search?query=oui&type=series
@app.route("/search", methods=["GET"])
def search_api():
    """ Endpoint Flask pour effectuer une recherche """
    # Récupérer les paramètres de requête
    query = request.args.get("query")
    content_type = request.args.get("type")

    if not query:
        return jsonify({"error": "Le paramètre 'query' est requis."}), 400
    
    if not content_type:
        return jsonify({"error": "Le paramètre 'type' est requis."}), 400

    # Effectuer la recherche
    try:
        contenus = getContentFromZt(query, content_type)

        return jsonify({"results": contenus}), 200
    except Exception as e:
        dbg.debug_print(niveau_log.ERREUR, f"Erreur API : {e}", True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    debug = dbg()
    dbg.set_log_level(niveau_log.VERBOSE)

    contenus = getContentFromZt("oui","series")
    dbg.debug_print(niveau_log.LOG ,contenus,True)
    
    
    # app.run(host="0.0.0.0", port=5000)
    