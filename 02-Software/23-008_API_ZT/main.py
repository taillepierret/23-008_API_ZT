import argparse
import requests
from enum import Enum
from debug import debug as dbg
from debug import niveau_log
from flask import Flask, request, jsonify
import json
from GetContentFromZt.GetContentFromZt import getContentFromZt
import os
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse

app = Flask(__name__)


DEFAULT_DOMAIN = "https://www.zone-telechargement.rent"

# Fichier de config à côté de main.py (marche sur PC et RPi)
CONFIG_FILE = Path(__file__).resolve().parent / "zt_domain.txt"

# Si tu veux pouvoir overrider par variable d'env :
# export ZT_DOMAIN_FILE=/opt/zt_api_prod/zt_domain.txt
CONFIG_FILE = Path(os.environ.get("ZT_DOMAIN_FILE", str(CONFIG_FILE)))

_domain_lock = Lock()
_cached_domain = None


def _is_valid_url(s: str) -> bool:
    try:
        u = urlparse(s.strip())
        return u.scheme in ("http", "https") and bool(u.netloc)
    except Exception:
        return False


def load_domain() -> str:
    global _cached_domain
    with _domain_lock:
        if _cached_domain:
            return _cached_domain

        if CONFIG_FILE.exists():
            txt = CONFIG_FILE.read_text(encoding="utf-8").strip()
            if txt and _is_valid_url(txt):
                _cached_domain = txt
                return _cached_domain

        _cached_domain = DEFAULT_DOMAIN
        return _cached_domain


def save_domain(new_domain: str) -> str:
    global _cached_domain
    new_domain = new_domain.strip()

    if not _is_valid_url(new_domain):
        raise ValueError("URL invalide. Exemple attendu: https://exemple.com")

    with _domain_lock:
        tmp = CONFIG_FILE.with_suffix(".tmp")
        tmp.write_text(new_domain + "\n", encoding="utf-8")
        tmp.replace(CONFIG_FILE)
        _cached_domain = new_domain

    return new_domain



#exemple: http://192.168.1.18:5001/config/domain
@app.route("/config/domain", methods=["GET"])
def get_domain():
    return jsonify({"domain": load_domain(), "config_file": str(CONFIG_FILE)}), 200


@app.route("/config/domain", methods=["PUT"])
def put_domain():
    data = request.get_json(silent=True) or {}
    new_domain = data.get("domain")

    if not new_domain:
        return jsonify({"error": "JSON attendu: {\"domain\": \"https://...\"}"}), 400

    try:
        saved = save_domain(new_domain)
        return jsonify({"domain": saved}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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
        print("query: ", query)
        print("content_type: ", content_type)
        url_zone_telechargement = load_domain()
        flag_result_ok, contenus = getContentFromZt(query, content_type, url_zone_telechargement)
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
        url_zone_telechargement = load_domain()
        flag_result_ok, contenus = getContentFromZt("never+back+down", "films",url_zone_telechargement)
        if not flag_result_ok:
            dbg.debug_print(niveau_log.ERREUR, "Aucun résultat trouvé.", True)
        else:
            dbg.debug_print(niveau_log.LOG, contenus, True)
    elif args.mode == "server":
        # Mode Serveur : Lancer Flask
        app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
