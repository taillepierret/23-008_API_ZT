import requests
from debug import debug as dbg
from debug import niveau_log


def recherche_mot_entre_2_mots_du_haut_vers_le_bas(mot_debut: str, mot_fin: str, phrase:str, index_haut_de_recherche):
    index_recherche_caractere_fin_mot = index_haut_de_recherche
    while phrase[index_recherche_caractere_fin_mot:index_recherche_caractere_fin_mot+len(mot_fin)] != mot_fin:#TODO ajouter un timeout
        index_recherche_caractere_fin_mot-=1
    if phrase[index_recherche_caractere_fin_mot-1] == " ":
        index_recherche_caractere_fin_mot-=1
    index_recherche_caractere_debut_mot = index_recherche_caractere_fin_mot
    while phrase[index_recherche_caractere_debut_mot:index_recherche_caractere_debut_mot+len(mot_debut)] != mot_debut:#TODO ajouter un timeout
        index_recherche_caractere_debut_mot-=1
    mot = phrase[index_recherche_caractere_debut_mot+len(mot_debut):index_recherche_caractere_fin_mot]
    return mot


def ecrire_resultat_dans_html(resultat_recherche:str):
    # Ouvrir le fichier HTML en mode écriture
    with open("resultat.html", "w") as f:
        # Écrire le contenu HTML dans le fichier
        f.write(resultat_recherche)


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