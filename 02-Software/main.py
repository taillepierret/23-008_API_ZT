import copy
from enum import Enum
from debug import debug as dbg
from debug import niveau_log
import outils
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class type_contenu(Enum):
    SERIES = "series"
    FILMS = "films"
    ANIMES = "mangas"

url_zone_telechargement = "https://www.zone-telechargement.homes"
nombre_de_page_max = 10


def recherche_de_contenu_dans_une_page_ZT(numero_page: int, lien_de_recherche: str):
    """fait une recherche dans une page bien precise sur zone de telechargement. Il faut lui charger une recherche zoen de telechargement et un numero de page"""
    url_de_recherche = lien_de_recherche + "&page=" + str(numero_page)
    return outils.open_website(url_de_recherche)

def recherche_de_contenu (type_de_contenu: type_contenu, nom_de_la_recherche: str):
    """fait une recherche sur ZT à partir d'un mot utilisateur et du type de contenu, 
    renvoie une liste de page HTML contentant le resultat de la recherche """
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
            bande_audio = outils.recherche_mot_entre_2_mots_du_haut_vers_le_bas("(",")",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
            nom_de_contenu = outils.recherche_mot_entre_2_mots_du_haut_vers_le_bas(">","-",phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
            numero_saison = page[index_debut_saison:index_fin_saison]
            lien_vers_contenu = "/" + outils.recherche_mot_entre_2_mots_du_haut_vers_le_bas("href=\"","\">"+nom_de_contenu,phrase_contenant_les_infos,len(phrase_contenant_les_infos)-1)
            
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

    tab_temp = [contenus[0][0],[contenus[0][1]],[contenus[0][1],contenus[0][2],contenus[0][3]]]
    resultat.append(tab_temp)
    for j in range (len(contenus)):
        for i in range (len(resultat)):
            if contenus[j][0] == resultat[i][0]:
                flag_presence_dans_tableau = True
                index_dans_resultat_contenu_deja_present = i
                index_dans_contenus_contenu_deja_present = j
        if not(flag_presence_dans_tableau):
            tab_temp = [contenus[j][0],[contenus[j][1]],[contenus[j][1],contenus[j][2],contenus[j][3]]]
            resultat.append(tab_temp)
        else:
            flag_presence_dans_tableau = False
            resultat[index_dans_resultat_contenu_deja_present][1].append(contenus[index_dans_contenus_contenu_deja_present][1])
            resultat[index_dans_resultat_contenu_deja_present].append([contenus[index_dans_contenus_contenu_deja_present][1],contenus[index_dans_contenus_contenu_deja_present][2],contenus[index_dans_contenus_contenu_deja_present][3]])
    for i in range (len(resultat)):
        resultat[i][1] = list(set(resultat[i][1]))
        resultat[i][1].sort()
    return resultat

def trouver_contenu_sur_une_recherche(recherches: list):
    contenus_extraits = []
    for page in recherches:
        contenus_extraits_pour_une_page = trouver_contenu_sur_une_page(page)
        for contenu in (contenus_extraits_pour_une_page):
            contenus_extraits.append(contenu)
            dbg.debug_print(niveau_log.DEBUG ,contenu,True)
    contenus_extraits = rassembler_les_contenus_qui_ont_le_même_titre(contenus_extraits)
    contenus_extraits = completer_les_liens_incomplets(contenus_extraits)
    return contenus_extraits

def recherche_large(type_de_contenu: type_contenu, nom_de_la_recherche: str):
    """lance une recherche classique en supprimant les elements ne correspondants pas a la recherche"""
    recherches = recherche_de_contenu(type_de_contenu,nom_de_la_recherche)
    contenus_extraits = trouver_contenu_sur_une_recherche(recherches)
    return contenus_extraits

def recherche_fine(type_de_contenu: type_contenu, nom_de_la_recherche: str):
    """lance une recherche classique en supprimant les elements ne correspondants pas a la recherche"""
    recherches = recherche_de_contenu(type_de_contenu,nom_de_la_recherche)
    contenus_extraits = trouver_contenu_sur_une_recherche(recherches)
    resultats = []
    for contenus in contenus_extraits:
        if contenus[0].lower() == nom_de_la_recherche.lower():
            resultats.append(contenus)
    return resultats

def completer_les_liens_incomplets(resultat_recherche):
    resultat = copy.deepcopy(resultat_recherche)
    for contenu in resultat:
        for i in range (2,len(contenu)):
            contenu[i][2] = url_zone_telechargement + contenu[i][2]
    return resultat

def passer_captcha(url, captcha_input):
    # Utiliser le pilote GeckoDriver pour Firefox
    driver = webdriver.Firefox()
    
    driver.get(url)

    try:
        print("banjour")
        time.sleep(3)
        captcha_field = driver.find_element(By.ID, 'subButton')
        captcha_field.send_keys(captcha_input)
        captcha_field.submit()

        # Attendre un court instant pour que la page se charge (ajustez ce délai selon les besoins)
        time.sleep(2)

        # Vous pouvez ajouter ici d'autres actions à effectuer après avoir soumis le captcha
        # Par exemple, vérifier si la soumission a réussi, vérifier une réponse, etc.

    finally:
        driver.quit()


if __name__ == "__main__":
    dbg.set_log_level(niveau_log.LOG)
    #resultat_recherche = recherche_large(type_contenu.SERIES,"breaking bad")
    #for contenu in (resultat_recherche):
    #        dbg.debug_print(niveau_log.LOG ," ",True)
    #    for item in contenu:
    #        dbg.debug_print(niveau_log.LOG ,item,True)

    url = "https://dl-protect.link/441decb9?fn=QnJlYWtpbmcgQmFkIC0gU2Fpc29uIDUgRXBpc29kZSAxIC0gW01VTFRJIDRLIFVIRF0%3D&rl=b2"
    outils.ecrire_resultat_dans_html(outils.open_website(url))
    # Exemple d'utilisation
    url_site_web = url
    reponse_captcha = 'abcd1234'  # Remplacez par la réponse réelle du captcha
    passer_captcha(url_site_web, reponse_captcha)

    
    