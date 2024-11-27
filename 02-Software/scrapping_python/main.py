import requests
from enum import Enum
from debug import debug as dbg
from debug import niveau_log
from flask import Flask, request, jsonify
import json

url_zone_telechargement = "https://www.zone-telechargement.makeup"
nombre_de_page_max = 15

app = Flask(__name__)  # Initialiser l'application Flask

class Contenu:
    def __init__(self, nom: str, saison: str, bande_audio: str, lien: str, image: str, date_de_publication: str):
        self.nom = nom
        self.saison = saison
        self.bande_audio = bande_audio
        self.lien = lien
        self.image = image
        self.date_de_publication = date_de_publication

    def to_dict(self):
        return {
            "nom": self.nom,
            "saison": self.saison,
            "bande_audio": self.bande_audio,
            "lien": self.lien,
            "image": self.image,
            "date_de_publication": self.date_de_publication
        }

    @staticmethod
    def from_dict(data):
        return Contenu(data["nom"], data["saison"], data["bande_audio"], data["lien"])

def open_website(url):
    """ renvoie le contenu de la page a l'URL selectionne"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dbg.debug_print(niveau_log.DEBUG ,url,True)
            ecrire_resultat_dans_un_fichier(response.text)
            return(response.text)
        else:
            dbg.debug_print(niveau_log.ERREUR ,f"Erreur lors de l'accès au site. Code d'état : {response.status_code}",True)
    except requests.exceptions.RequestException as e:
        dbg.debug_print(niveau_log.ERREUR ,f"Une erreur s'est produite : {e}",True)


def recherche_de_contenu_dans_une_page_ZT(numero_page: int, lien_de_recherche: str):
    """fait une recherche dans une page bien precise sur zone de telechargement. Il faut lui charger une recherche zone de telechargement et un numero de page"""
    url_de_recherche = lien_de_recherche + "&page=" + str(numero_page)
    return open_website(url_de_recherche)


def recherche_de_contenu (type_de_contenu: str, nom_de_la_recherche: str):
    """fait une recherche sur zone de telechargement. Il faut lui charger un type de contenu et un nom de recherche. La fonction renvoie un tableau de recherche contenant les resultats de chaque page"""
    url_de_recherche = url_zone_telechargement + "/?search=" + nom_de_la_recherche.replace(" ", "+") + "&p=" + type_de_contenu
    tab_recherches = []
    for i in range (1,nombre_de_page_max):
        recherche = recherche_de_contenu_dans_une_page_ZT(i,url_de_recherche)
        tab_recherches.append(recherche)
        if "Aucune fiches trouvées." in recherche:
            dbg.debug_print(niveau_log.DEBUG ,f"recherche terminee le nombre de page est de : {i-1}",True)
            return tab_recherches
        elif i == nombre_de_page_max-1:
            dbg.debug_print(niveau_log.ERREUR ,f"Veuillez faire une recherche plus concise, il y a trop de pages de resultats, le nombre de page maximum est de : {nombre_de_page_max}",True)


def ecrire_resultat_dans_un_fichier(resultat_recherche:str):
    # Ouvrir le fichier HTML en mode écriture
    with open("resultat.html", "w", encoding="utf-8") as f:
        # Écrire le contenu HTML dans le fichier
        f.write(resultat_recherche)

def recherche_mot_entre_2_mots (mot_debut: str, mot_fin: str, phrase:str, index_haut_de_recherche):
    """renvoie le mot entre 2 mots donnés dans une phrase"""
    index_recherche_caractere_fin_mot = index_haut_de_recherche
    while phrase[index_recherche_caractere_fin_mot:index_recherche_caractere_fin_mot+len(mot_fin)] != mot_fin:#TODO ajouter un timeout
        index_recherche_caractere_fin_mot-=1
    index_recherche_caractere_debut_mot = index_recherche_caractere_fin_mot
    while phrase[index_recherche_caractere_debut_mot:index_recherche_caractere_debut_mot+len(mot_debut)] != mot_debut:#TODO ajouter un timeout
        index_recherche_caractere_debut_mot-=1
    mot = phrase[index_recherche_caractere_debut_mot+len(mot_debut):index_recherche_caractere_fin_mot]
    return mot

def trouver_contenu_sur_une_page(page: str): #/!\ le numero de saison ne peut pas etre superieur a 9, TODO a corriger
    """renvoie un tableau avec un tableau de noms de contenu, un tableau de saisons et
    un tableau de liens partiels correspondants à chaque saison sur une page"""
    
    index_debut_recherche = 0
    index_fin_recherche = 0

    tableau_de_retour = []

    bande_audio = []
    nom_de_contenu = []
    numero_saison = []
    lien_vers_contenu = []
    date_de_publication = []
    tab_donnees_recuperees = []

    while index_debut_recherche < len(page): #TODO ajouter un timeout
        index_debut_recherche = page.find("Publié le", index_debut_recherche)

        if index_debut_recherche == -1:  # Si le mot n'est plus trouvé, sortir de la boucle
            break

        index_fin_recherche = page.find("</b></span></span><br>", index_debut_recherche)

        phrase_contenant_les_infos = page[index_debut_recherche:index_fin_recherche]

        bande_audio = recherche_mot_entre_2_mots("(",")",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)

        nom_de_contenu = recherche_mot_entre_2_mots(">"," -",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
        numero_saison = recherche_mot_entre_2_mots(" - ","</a><br>",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
        lien_vers_contenu = "/" + recherche_mot_entre_2_mots("href=\"","\">"+nom_de_contenu,phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
        lien_vers_image = recherche_mot_entre_2_mots("src=\"","\" width",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
        date_de_publication = recherche_mot_entre_2_mots("<time>","</time>",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
        
        # dbg.debug_print(niveau_log.DEBUG ," ",False)
        # dbg.debug_print(niveau_log.DEBUG ,nom_de_contenu,True)
        # dbg.debug_print(niveau_log.DEBUG ,numero_saison,True)
        # dbg.debug_print(niveau_log.DEBUG ,bande_audio,True)
        # dbg.debug_print(niveau_log.DEBUG ,lien_vers_contenu,True)
        # dbg.debug_print(niveau_log.DEBUG ,phrase_contenant_les_infos,True)
        # dbg.debug_print(niveau_log.DEBUG ,lien_vers_image,True)
        # dbg.debug_print(niveau_log.DEBUG ,date_de_publication,True)

        tab_donnees_recuperees = []
        tab_donnees_recuperees.append(nom_de_contenu)
        tab_donnees_recuperees.append(numero_saison)
        tab_donnees_recuperees.append(bande_audio)
        tab_donnees_recuperees.append(lien_vers_contenu)
        tab_donnees_recuperees.append(lien_vers_image)
        tab_donnees_recuperees.append(date_de_publication)
        tableau_de_retour.append(tab_donnees_recuperees)


        # Déplacer l'index de recherche pour éviter de trouver le même mot à nouveau
        index_debut_recherche += 1
    return tableau_de_retour

def rassembler_les_contenus_qui_ont_le_même_titre(contenus:list):
    resultat = []
    index_dans_resultat_contenu_deja_present = 0
    index_dans_contenus_contenu_deja_present = 0
    flag_presence_dans_tableau = False

    tab_temp = []
    for i in range (len(contenus[0])):
        if i == 0:
            tab_temp.append(contenus[0][0])
        else:
            tab_temp.append([contenus[0][i]])
    resultat.append(tab_temp)

    for j in range (1,len(contenus)):
        for i in range (len(resultat)):
            if contenus[j][0] == resultat[i][0]:
                flag_presence_dans_tableau = True
                index_dans_resultat_contenu_deja_present = i
                index_dans_contenus_contenu_deja_present = j
        if not(flag_presence_dans_tableau):
            tab_temp = []
            for i in range (len(contenus[j])):
                if i == 0:
                    tab_temp.append(contenus[j][0])
                else:
                    tab_temp.append([contenus[j][i]])
            resultat.append(tab_temp)
        else:
            flag_presence_dans_tableau = False
            for i in range (len(contenus[j])):
                if i != 0:
                    resultat[index_dans_resultat_contenu_deja_present][i].append(contenus[index_dans_contenus_contenu_deja_present][i])
            
    return resultat

def trouver_contenu_sur_une_recherche(recherches: list):
    contenus_extraits = []
    for page in recherches:
        contenus_extraits_pour_une_page = trouver_contenu_sur_une_page(page)
        for contenu in (contenus_extraits_pour_une_page):
            contenus_extraits.append(contenu)
    #contenus_extraits = rassembler_les_contenus_qui_ont_le_même_titre(contenus_extraits)
    return contenus_extraits



#exemple de contenu extrait:
# ['Counterpart', 'Saison 1', 'VOSTFR HD', '/?p=serie&id=2047-counterpart-saison1', '/img/series/6940ca702a25cd00b2a67bd0a95fc31f.webp', '22 February 2019']
# ['Les Simpson', 'Saison 25', 'VF HD', '/?p=serie&id=2357-les-simpson-saison25', '/img/series/ab98f477be097ae433f4a8ede030c2bf.webp', '14 April 2019']
# ['Les Simpson', 'Saison 26', 'VF HD', '/?p=serie&id=2358-les-simpson-saison26', '/img/series/e0d9dd19c456e86db5d0c0af821b4a19.webp', '14 April 2019']
# ['Les Simpson', 'Saison 27', 'VF HD', '/?p=serie&id=2359-les-simpson-saison27', '/img/series/49030e247102be5c19b4aa754525aadb.webp', '14 April 2019']
# ['Les Simpson', 'Saison 28', 'VF HD', '/?p=serie&id=2360-les-simpson-saison28', '/img/series/c9a6bf7af351f93baf64f8fca22af66f.webp', '14 April 2019']
# ['Blacklist', 'Saison 3', 'VF', '/?p=serie&id=2389-blacklist-saison3', '/img/series/ba2d1b8f312a7506cc2f1140e9d699c9.webp', '15 April 2019']
# ['Blacklist', 'Saison 4', 'VF', '/?p=serie&id=2390-blacklist-saison4', '/img/series/132dc48f63b9a5b0195edc9b9761aebc.webp', '15 April 2019']
# ['Blacklist', 'Saison 1', 'VF HD', '/?p=serie&id=2411-blacklist-saison1', '/img/series/4729eccd0adf7ec8d1747356ef07135c.webp', '17 April 2019']
# ['Blacklist', 'Saison 2', 'VF HD', '/?p=serie&id=2412-blacklist-saison2', '/img/series/17734f777e31e89eb80d573335f8c3ba.webp', '17 April 2019']
# ['Blacklist', 'Saison 3', 'VF HD', '/?p=serie&id=2413-blacklist-saison3', '/img/series/f6551a7a8a438e1afe4cce2eb225f924.webp', '17 April 2019']
# ['Blacklist', 'Saison 4', 'VF HD', '/?p=serie&id=2422-blacklist-saison4', '/img/series/b321b86db34803e0a0215766cd332041.webp', '19 April 2019']
# ['Blacklist', 'Saison 5', 'VF HD', '/?p=serie&id=2423-blacklist-saison5', '/img/series/bc478e22164d9a026ddd691c0f794c96.webp', '19 April 2019']
# ['Blacklist', 'Saison 6', 'VOSTFR HD', '/?p=serie&id=2696-blacklist-saison6', '/img/series/497f03ddde4bcdbc73e13175beb649bd.webp', '19 May 2019']
# ['Blacklist', 'Saison 6', 'VF', '/?p=serie&id=2697-blacklist-saison6', '/img/series/cd8de78fd7c20d9dc5f9345a34320cdf.webp', '30 August 2019']

# Fonction pour rassembler les contenu par nom et ajouter les autres informations
def rassembler_contenu_par_nom(contenus: list):
    contenus_rassembles = []
    flag_presence_dans_tableau = False
    for contenu in contenus:
        nom = contenu[0]
        flag_presence_dans_tableau = False
        for contenu_rassemble in contenus_rassembles:
            if contenu_rassemble["nom"][0] == nom:
                contenu_rassemble["saison"].append(contenu[1])
                contenu_rassemble["bande_audio"].append(contenu[2])
                contenu_rassemble["lien"].append(contenu[3])
                contenu_rassemble["image"].append(contenu[4])
                contenu_rassemble["date_de_publication"].append(contenu[5])
                flag_presence_dans_tableau = True
                break
        if flag_presence_dans_tableau == False:
            contenus_rassembles.append({
                "nom": [contenu[0]],
                "saison": [contenu[1]],
                "bande_audio": [contenu[2]],
                "lien": [contenu[3]],
                "image": [contenu[4]],
                "date_de_publication": [contenu[5]]
            })
    contenus_rassembles = json.dumps(contenus_rassembles, indent=2, ensure_ascii=False)
    return contenus_rassembles


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
        recherches = recherche_de_contenu(content_type, query)
        contenus = trouver_contenu_sur_une_recherche(recherches)
        contenus = rassembler_contenu_par_nom(contenus)

        return jsonify({"results": contenus}), 200
    except Exception as e:
        dbg.debug_print(niveau_log.ERREUR, f"Erreur API : {e}", True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    debug = dbg()
    dbg.set_log_level(niveau_log.VERBOSE)


    recherches = recherche_de_contenu("series","harry")
    contenus_extraits = trouver_contenu_sur_une_recherche(recherches)
    for contenu in (contenus_extraits):
        dbg.debug_print(niveau_log.LOG ,contenu,True)
    # contenus_rassembles = rassembler_contenu_par_nom(contenus_extraits)
    # dbg.debug_print(niveau_log.LOG ,contenus_rassembles,True)
    
    
    app.run(host="0.0.0.0", port=5000)
    