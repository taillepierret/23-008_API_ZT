from datetime import datetime
from enum import Enum


class niveau_log(Enum):
    PAS_DE_LOG = 0
    ERREUR = 1
    LOG = 2
    DEBUG = 3
    VERBOSE = 4

_niveau_de_log = niveau_log.PAS_DE_LOG

class debug():
    def set_log_level(niveau_log: niveau_log):
        global _niveau_de_log
        _niveau_de_log = niveau_log

    def get_log_level():
        global _niveau_de_log
        return _niveau_de_log

    def debug_print(niveau_log: niveau_log, message, flag_affichage_heure: bool):
        global _niveau_de_log
        message = "[" + str(niveau_log).replace("niveau_log.","") + "]" + str(message)
        if niveau_log.value <= _niveau_de_log.value:
            if flag_affichage_heure:
                heure_actuelle = datetime.now().strftime("%H:%M:%S")
                print (heure_actuelle + ": " + str(message))
            else:
                print (message)