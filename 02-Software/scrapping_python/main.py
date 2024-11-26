import requests
from enum import Enum
from debug import debug as dbg
from debug import niveau_log
from flask import Flask, request, jsonify

url_zone_telechargement = "https://www.zone-telechargement.makeup"
nombre_de_page_max = 10

app = Flask(__name__)  # Initialiser l'application Flask

class Contenu:
    def __init__(self, nom: str, saison: str, bande_audio: str, lien: str, image: str):
        self.nom = nom
        self.saison = saison
        self.bande_audio = bande_audio
        self.lien = lien
        self.image = image

    def to_dict(self):
        return {
            "nom": self.nom,
            "saison": self.saison,
            "bande_audio": self.bande_audio,
            "lien": self.lien,
            "image": self.image
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

def trouver_contenu_sur_une_page(page: str):
    """renvoie un tableau avec un tableau de noms de contenu, un tableau de saisons et
    un tableau de liens partiels correspondants à chaque saison sur une page"""
    index_debut_saison = 0
    index_fin_saison = 0

    index_recherche_nom_serie = 0
    index_aide_recherche_caractere_fin_bande_audio = 0
    flag_saison_a_ne_pas_prendre_en_compte = True
    mot_fin_de_phrase_contenant_les_infos = ""

    tableau_de_retour = []

    bande_audio = [1]
    nom_de_contenu = [1]
    numero_saison = [1]
    lien_vers_contenu = [1]

    while index_debut_saison < len(page): #TODO ajouter un timeout
        index_debut_saison = page.find("saison", index_debut_saison)

        if index_debut_saison == -1:  # Si le mot n'est plus trouvé, sortir de la boucle
            break

        index_fin_saison = index_debut_saison + len("saison") + 1  # Calculer l'index du caractère suivant
        index_recherche_nom_serie = index_debut_saison
        while page[index_recherche_nom_serie] != "<":#TODO ajouter un timeout
            index_recherche_nom_serie -= 1
            

        index_aide_recherche_caractere_fin_bande_audio = index_debut_saison
        mot_fin_de_phrase_contenant_les_infos = page[index_aide_recherche_caractere_fin_bande_audio:index_aide_recherche_caractere_fin_bande_audio+7]
        flag_saison_a_ne_pas_prendre_en_compte = False
        while mot_fin_de_phrase_contenant_les_infos != "</span>" :#TODO ajouter un timeout
            index_aide_recherche_caractere_fin_bande_audio += 1
            mot_fin_de_phrase_contenant_les_infos = page[index_aide_recherche_caractere_fin_bande_audio:index_aide_recherche_caractere_fin_bande_audio+7]
            if index_aide_recherche_caractere_fin_bande_audio-index_debut_saison>200:
                flag_saison_a_ne_pas_prendre_en_compte = True
                break

        if not(flag_saison_a_ne_pas_prendre_en_compte):
            phrase_contenant_les_infos = page[index_recherche_nom_serie:index_aide_recherche_caractere_fin_bande_audio]
            bande_audio = recherche_mot_entre_2_mots("(",")",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
            nom_de_contenu = recherche_mot_entre_2_mots(">","-",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
            numero_saison = page[index_debut_saison:index_fin_saison]
            lien_vers_contenu = "/" + recherche_mot_entre_2_mots("href=\"","\">"+nom_de_contenu,phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
            
            dbg.debug_print(niveau_log.DEBUG ," ",False)
            dbg.debug_print(niveau_log.DEBUG ,nom_de_contenu,True)
            dbg.debug_print(niveau_log.DEBUG ,numero_saison,True)
            dbg.debug_print(niveau_log.DEBUG ,bande_audio,True)
            dbg.debug_print(niveau_log.DEBUG ,lien_vers_contenu,True)
            dbg.debug_print(niveau_log.DEBUG ,phrase_contenant_les_infos,True)

            tab_donnees_recuperees = []
            tab_donnees_recuperees.append(nom_de_contenu)
            tab_donnees_recuperees.append(numero_saison)
            tab_donnees_recuperees.append(bande_audio)
            tab_donnees_recuperees.append(lien_vers_contenu)
            tableau_de_retour.append(tab_donnees_recuperees)

        # Déplacer l'index de recherche pour éviter de trouver le même mot à nouveau
        index_debut_saison += 1
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
            dbg.debug_print(niveau_log.DEBUG ,contenu,True)
    contenus_extraits = rassembler_les_contenus_qui_ont_le_même_titre(contenus_extraits)
    return contenus_extraits

@app.route("/search", methods=["GET"])
def search_api():
    """ Endpoint Flask pour effectuer une recherche """
    # Récupérer les paramètres de requête
    query = request.args.get("query")
    content_type = request.args.get("type", "films")  # Default : films

    if not query:
        return jsonify({"error": "Le paramètre 'query' est requis."}), 400

    # Effectuer la recherche
    try:
        recherches = recherche_de_contenu(content_type, query)
        contenus = trouver_contenu_sur_une_recherche(recherches)

        return jsonify({"results": contenus})
    except Exception as e:
        dbg.debug_print(niveau_log.ERREUR, f"Erreur API : {e}", True)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    debug = dbg()
    dbg.set_log_level(niveau_log.LOG)
    recherches = recherche_de_contenu("series","oui")
    contenus_extraits = trouver_contenu_sur_une_recherche(recherches)
    for contenu in (contenus_extraits):
        dbg.debug_print(niveau_log.LOG ,contenu,True)
        #app.run(host="0.0.0.0", port=5000)
    