#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de gestion des heures de badgeage avec pause obligatoire.

Contraintes :
- 8H de travail par jour
- Pause obligatoire avant d'atteindre 6H de travail
- Pause minimum : 15 minutes (pour être valable)
- Pause maximum légale : 30 minutes (non décomptées du temps de travail)
- Si pause < 30min : le temps non utilisé (30 - durée_pause) s'ajoute au temps de travail
"""

import argparse
import random
import sys
from datetime import datetime, timedelta
import time
import threading


class GestionBadgeage:
    """Classe pour gérer les calculs de badgeage."""

    DUREE_TRAVAIL_JOURNEE = 8 * 60  # 8 heures en minutes
    DUREE_AVANT_PAUSE = 6 * 60      # 6 heures en minutes
    PAUSE_MIN = 15                   # minutes
    PAUSE_MAX = 30                   # minutes (légale)
    PAUSE_RANDOM_MIN = 17            # minutes
    PAUSE_RANDOM_MAX = 27            # minutes

    def __init__(self, heure_debut):
        """
        Initialise avec l'heure du premier pointage.

        Args:
            heure_debut: str au format "HH:MM" ou datetime
        """
        if isinstance(heure_debut, str):
            self.heure_debut = datetime.strptime(heure_debut, "%H:%M")
        else:
            self.heure_debut = heure_debut

        # Génération aléatoire de la durée de pause
        self.duree_pause = random.randint(self.PAUSE_RANDOM_MIN, self.PAUSE_RANDOM_MAX)

        # Calcul des heures clés
        self.calculer_horaires()

    def calculer_horaires(self):
        """Calcule tous les horaires de la journée."""
        # Heure de départ en pause (avant 6H de travail)
        self.heure_pause = self.heure_debut + timedelta(minutes=self.DUREE_AVANT_PAUSE)

        # Heure de reprise après pause
        self.heure_reprise = self.heure_pause + timedelta(minutes=self.duree_pause)

        # Temps "perdu" (différence entre pause légale et pause réelle)
        self.temps_perdu = self.PAUSE_MAX - self.duree_pause

        # Temps de travail restant après la pause
        temps_apres_pause = (self.DUREE_TRAVAIL_JOURNEE - self.DUREE_AVANT_PAUSE) + self.temps_perdu

        # Heure de fin
        self.heure_fin = self.heure_reprise + timedelta(minutes=temps_apres_pause)

    def afficher_resume(self):
        """Affiche le résumé de la journée."""
        print("\n" + "="*60)
        print(" PLANNING DE VOTRE JOURNÉE DE TRAVAIL")
        print("="*60)
        print(f"\n🕐 Premier pointage (début) : {self.heure_debut.strftime('%H:%M')}")
        print(f"\n⏸️  Départ en PAUSE (avant 6H) : {self.heure_pause.strftime('%H:%M')}")
        print(f"   └─ Durée de la pause : {self.duree_pause} minutes")
        print(f"   └─ Temps perdu (30min - {self.duree_pause}min) : {self.temps_perdu} minutes")
        print(f"\n▶️  Reprise du travail : {self.heure_reprise.strftime('%H:%M')}")
        print(f"\n🏁 Fin de journée : {self.heure_fin.strftime('%H:%M')}")

        # Calcul du temps total de travail
        temps_avant_pause = self.DUREE_AVANT_PAUSE
        temps_apres_pause = (self.DUREE_TRAVAIL_JOURNEE - self.DUREE_AVANT_PAUSE) + self.temps_perdu
        temps_total = temps_avant_pause + temps_apres_pause

        print(f"\n📊 Récapitulatif :")
        print(f"   - Temps de travail matin : {temps_avant_pause // 60}h{temps_avant_pause % 60:02d}")
        print(f"   - Temps de pause : {self.duree_pause} min")
        print(f"   - Temps de travail après-midi : {temps_apres_pause // 60}h{temps_apres_pause % 60:02d}")
        print(f"   - TOTAL travail effectif : {temps_total // 60}h{temps_total % 60:02d}")
        print("="*60 + "\n")

    def temps_restant_avant(self, heure_cible):
        """Calcule le temps restant avant une heure cible."""
        maintenant = datetime.now().replace(
            year=self.heure_debut.year,
            month=self.heure_debut.month,
            day=self.heure_debut.day
        )

        delta = heure_cible - maintenant
        return delta.total_seconds()

    def minuteur(self, message, duree_secondes):
        """Affiche un minuteur avec compte à rebours."""
        print(f"\n⏱️  {message}")
        print("   [Ctrl+C pour arrêter le minuteur]\n")

        try:
            fin = time.time() + duree_secondes
            while True:
                restant = fin - time.time()
                if restant <= 0:
                    print("\r   ⏰ TEMPS ÉCOULÉ ! " + " "*40)
                    print(f"\n🔔 {message} - C'EST LE MOMENT !\n")
                    break

                heures = int(restant // 3600)
                minutes = int((restant % 3600) // 60)
                secondes = int(restant % 60)

                print(f"\r   Temps restant : {heures:02d}:{minutes:02d}:{secondes:02d}", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n   ⏹️  Minuteur arrêté.\n")

    def chronometre(self):
        """Affiche un chronomètre depuis le début de la journée."""
        print("\n⏱️  CHRONOMÈTRE - Temps écoulé depuis le début")
        print("   [Ctrl+C pour arrêter]\n")

        try:
            debut = datetime.now()
            while True:
                maintenant = datetime.now()
                ecoule = (maintenant - debut).total_seconds()

                # Temps écoulé depuis le début théorique
                if hasattr(self, '_debut_reel'):
                    ecoule_total = (maintenant - self._debut_reel).total_seconds()
                else:
                    ecoule_total = ecoule

                heures = int(ecoule_total // 3600)
                minutes = int((ecoule_total % 3600) // 60)
                secondes = int(ecoule_total % 60)

                # Calcul du pourcentage
                pourcentage = min(100, (ecoule_total / (self.DUREE_TRAVAIL_JOURNEE * 60)) * 100)

                print(f"\r   Temps travaillé : {heures:02d}:{minutes:02d}:{secondes:02d} ({pourcentage:.1f}%)",
                      end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n   ⏹️  Chronomètre arrêté.\n")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description="Gestion des heures de badgeage avec pause obligatoire",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  %(prog)s 09:00                    # Calcule les horaires pour un début à 9h00
  %(prog)s 09:00 --minuteur-pause   # Lance un minuteur jusqu'à la pause
  %(prog)s 09:00 --minuteur-fin     # Lance un minuteur jusqu'à la fin
  %(prog)s 09:00 --chronometre      # Lance un chronomètre de travail
        """
    )

    parser.add_argument(
        "heure_debut",
        help="Heure du premier pointage (format HH:MM, ex: 09:00)"
    )

    parser.add_argument(
        "--minuteur-pause",
        action="store_true",
        help="Lance un minuteur jusqu'à l'heure de pause"
    )

    parser.add_argument(
        "--minuteur-reprise",
        action="store_true",
        help="Lance un minuteur pour la durée de la pause"
    )

    parser.add_argument(
        "--minuteur-fin",
        action="store_true",
        help="Lance un minuteur jusqu'à la fin de journée"
    )

    parser.add_argument(
        "--chronometre",
        action="store_true",
        help="Lance un chronomètre du temps de travail écoulé"
    )

    parser.add_argument(
        "--tout",
        action="store_true",
        help="Lance tous les minuteurs en séquence"
    )

    args = parser.parse_args()

    try:
        # Création de l'objet de gestion
        gestion = GestionBadgeage(args.heure_debut)

        # Affichage du résumé
        gestion.afficher_resume()

        # Gestion des minuteurs/chronomètres
        if args.tout:
            # Séquence complète
            temps_avant_pause = gestion.temps_restant_avant(gestion.heure_pause)
            if temps_avant_pause > 0:
                gestion.minuteur("Minuteur jusqu'à la PAUSE", temps_avant_pause)

            gestion.minuteur(f"Minuteur de PAUSE ({gestion.duree_pause} min)", gestion.duree_pause * 60)

            temps_avant_fin = gestion.temps_restant_avant(gestion.heure_fin)
            if temps_avant_fin > 0:
                gestion.minuteur("Minuteur jusqu'à la FIN de journée", temps_avant_fin)

        elif args.minuteur_pause:
            temps_restant = gestion.temps_restant_avant(gestion.heure_pause)
            if temps_restant > 0:
                gestion.minuteur("Minuteur jusqu'à la PAUSE", temps_restant)
            else:
                print("⚠️  L'heure de pause est déjà passée !\n")

        elif args.minuteur_reprise:
            gestion.minuteur(f"Minuteur de PAUSE ({gestion.duree_pause} min)", gestion.duree_pause * 60)

        elif args.minuteur_fin:
            temps_restant = gestion.temps_restant_avant(gestion.heure_fin)
            if temps_restant > 0:
                gestion.minuteur("Minuteur jusqu'à la FIN de journée", temps_restant)
            else:
                print("⚠️  L'heure de fin est déjà passée !\n")

        elif args.chronometre:
            gestion._debut_reel = datetime.now()
            gestion.chronometre()

    except ValueError as e:
        print(f"❌ Erreur : Format d'heure invalide. Utilisez le format HH:MM (ex: 09:00)", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Programme interrompu.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
