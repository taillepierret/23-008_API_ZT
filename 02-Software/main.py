import requests
from enum import Enum
from debug import debug as dbg
from debug import niveau_log

class type_contenu(Enum):
    SERIES = "series"
    FILMS = "films"
    ANIMES = "mangas"

url_zone_telechargement = "https://www.zone-telechargement.homes"
nombre_de_page_max = 10

def open_website(url):
    """ renvoie le contenu de la page a l'URL selectionne"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dbg.debug_print(niveau_log.DEBUG ,url,True)
            return(response.text)
        else:
            dbg.debug_print(niveau_log.ERREUR ,f"Erreur lors de l'accès au site. Code d'état : {response.status_code}",True)
    except requests.exceptions.RequestException as e:
        dbg.debug_print(niveau_log.ERREUR ,f"Une erreur s'est produite : {e}",True)

def recherche_de_contenu_dans_une_page_ZT(numero_page: int, lien_de_recherche: str):
    """fait une recherche dans une page bien precise sur zone de telechargement. Il faut lui charger une recherche zoen de telechargement et un numero de page"""
    url_de_recherche = lien_de_recherche + "&page=" + str(numero_page)
    return open_website(url_de_recherche)

def recherche_de_contenu (type_de_contenu: type_contenu, nom_de_la_recherche: str):
    url_de_recherche = url_zone_telechargement + "/?search=" + nom_de_la_recherche.replace(" ", "+") + "&p=" + type_de_contenu.value
    tab_recherches = []
    for i in range (1,nombre_de_page_max):
        recherche = recherche_de_contenu_dans_une_page_ZT(i,url_de_recherche)
        tab_recherches.append(recherche)
        if "Aucune fiches trouvées." in recherche:
            dbg.debug_print(niveau_log.DEBUG ,f"recherche terminee le nombre de page est de : {i-1}",True)
            return tab_recherches
        elif i == nombre_de_page_max-1:
            dbg.debug_print(niveau_log.ERREUR ,f"Veuillez faire une recherche plus concise, il y a trop de pages de resultats, le nombre de page maximum est de : {nombre_de_page_max}",True)


def ecrire_resultat_dans_html(resultat_recherche:str):
    # Ouvrir le fichier HTML en mode écriture
    with open("resultat.html", "w") as f:
        # Écrire le contenu HTML dans le fichier
        f.write(resultat_recherche)

def recherche_mot_entre_2_mots (mot_debut: str, mot_fin: str, phrase:str, index_haut_de_recherche):
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


def liste_saisons_disponibles_avec_liens(recherches: list):
    contenus_extraits = trouver_contenu_sur_une_page(recherches)
    for contenu in (contenus_extraits):
        print (contenu)
        print ()

def liste_saisons_disponibles_avec_liens2(recherches: list):
    contenus_extraits = []
    for page in recherches:
        contenus_extraits_pour_une_page = trouver_contenu_sur_une_page(recherches[0])
        for contenu in (contenus_extraits):
            contenus_extraits.append(contenu)
    dbg.debug_print(niveau_log.LOG ,contenus_extraits,True)
    return contenus_extraits


if __name__ == "__main__":
    debug = dbg()
    dbg.set_log_level(niveau_log.LOG)
    recherches = recherche_de_contenu(type_contenu.SERIES,"breaking bad")
    liste_saisons_disponibles_avec_liens(recherches[0])
    #print(recherches[4])
    #ecrire_resultat_dans_html()
    