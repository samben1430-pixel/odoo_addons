#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de gestion des heures de badgeage avec pause obligatoire.

Contraintes :
- 8H de travail par jour
- Pause AVANT 6H de travail (sinon pénalité de +30 min)
- Pause minimum : 15 minutes (pour être valable)
- Pause maximum légale : 30 minutes (non décomptées du temps de travail)
- Si pause < 30min : le temps non utilisé (30 - durée_pause) s'ajoute au temps de travail
- Si pause APRÈS 6H : pénalité de +30 min supplémentaires
- Plages de présence obligatoire : 9h30-11h30 et 14h30-15h30 (pas de pause possible)
"""

import argparse
import random
import sys
from datetime import datetime, timedelta
import time
import threading
import re


class GestionBadgeage:
    """Classe pour gérer les calculs de badgeage."""

    DUREE_TRAVAIL_JOURNEE = 8 * 60  # 8 heures en minutes
    DUREE_AVANT_PAUSE = 6 * 60      # 6 heures en minutes
    PAUSE_MIN = 15                   # minutes
    PAUSE_MAX = 30                   # minutes (légale)
    PAUSE_RANDOM_MIN = 17            # minutes
    PAUSE_RANDOM_MAX = 27            # minutes

    # Plages de présence obligatoire (heures en format HH:MM)
    PRESENCE_OBLIGATOIRE = [
        ("09:30", "11:30"),  # Matin
        ("14:30", "15:30"),  # Après-midi
    ]

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

    def _parse_time(self, time_str):
        """Parse une chaîne HH:MM et retourne un datetime avec la date du début."""
        time_obj = datetime.strptime(time_str, "%H:%M")
        return self.heure_debut.replace(hour=time_obj.hour, minute=time_obj.minute, second=0, microsecond=0)

    def _chevauche_plage_obligatoire(self, debut, fin):
        """
        Vérifie si une période chevauche une plage de présence obligatoire.

        Returns:
            tuple: (bool, str) - (True si chevauchement, nom de la plage)
        """
        for idx, (plage_debut_str, plage_fin_str) in enumerate(self.PRESENCE_OBLIGATOIRE):
            plage_debut = self._parse_time(plage_debut_str)
            plage_fin = self._parse_time(plage_fin_str)

            # Chevauchement si :
            # - La pause commence pendant la plage OU
            # - La pause se termine pendant la plage OU
            # - La pause englobe complètement la plage
            if (plage_debut <= debut < plage_fin or
                plage_debut < fin <= plage_fin or
                debut <= plage_debut and fin >= plage_fin):
                plage_nom = "9h30-11h30 (matin)" if idx == 0 else "14h30-15h30 (après-midi)"
                return True, plage_nom

        return False, None

    def _ajuster_pause_plage_obligatoire(self, heure_pause_ideale):
        """
        Ajuste l'heure de pause si elle chevauche une plage de présence obligatoire.

        Returns:
            tuple: (heure_pause_ajustee, temps_travail_avant_pause, avertissement)
        """
        heure_reprise_ideale = heure_pause_ideale + timedelta(minutes=self.duree_pause)
        chevauche, plage_nom = self._chevauche_plage_obligatoire(heure_pause_ideale, heure_reprise_ideale)

        if not chevauche:
            # Pas de problème, on garde l'heure idéale
            temps_avant = int((heure_pause_ideale - self.heure_debut).total_seconds() / 60)
            return heure_pause_ideale, temps_avant, None

        # Il y a chevauchement, il faut ajuster
        # Trouver quelle plage cause le problème
        plage_probleme = None
        for idx, (plage_debut_str, plage_fin_str) in enumerate(self.PRESENCE_OBLIGATOIRE):
            plage_debut = self._parse_time(plage_debut_str)
            plage_fin = self._parse_time(plage_fin_str)
            if (plage_debut <= heure_pause_ideale < plage_fin or
                plage_debut < heure_reprise_ideale <= plage_fin or
                heure_pause_ideale <= plage_debut and heure_reprise_ideale >= plage_fin):
                plage_probleme = (plage_debut, plage_fin, plage_debut_str, plage_fin_str)
                break

        if not plage_probleme:
            temps_avant = int((heure_pause_ideale - self.heure_debut).total_seconds() / 60)
            return heure_pause_ideale, temps_avant, None

        plage_debut, plage_fin, plage_debut_str, plage_fin_str = plage_probleme
        avertissement = f"⚠️  AJUSTEMENT : La pause idéale ({heure_pause_ideale.strftime('%H:%M')}) chevauche {plage_debut_str}-{plage_fin_str}"

        # Option 1: Terminer la pause AVANT le début de la plage problématique
        heure_reprise_avant = plage_debut
        heure_pause_avant = heure_reprise_avant - timedelta(minutes=self.duree_pause)
        temps_avant_avant = int((heure_pause_avant - self.heure_debut).total_seconds() / 60)

        # Option 2: Commencer la pause APRÈS la fin de la plage problématique
        heure_pause_apres = plage_fin
        heure_reprise_apres = heure_pause_apres + timedelta(minutes=self.duree_pause)
        temps_avant_apres = int((heure_pause_apres - self.heure_debut).total_seconds() / 60)

        # Choisir la meilleure option
        options = []

        # Vérifier option AVANT
        if temps_avant_avant > 0 and heure_pause_avant >= self.heure_debut:
            chevauche_avant, _ = self._chevauche_plage_obligatoire(heure_pause_avant, heure_reprise_avant)
            if not chevauche_avant:
                options.append(('avant', heure_pause_avant, temps_avant_avant))

        # Vérifier option APRÈS
        if temps_avant_apres <= self.DUREE_AVANT_PAUSE:
            chevauche_apres, _ = self._chevauche_plage_obligatoire(heure_pause_apres, heure_reprise_apres)
            if not chevauche_apres:
                options.append(('apres', heure_pause_apres, temps_avant_apres))

        # Choisir l'option qui respecte le mieux la contrainte des 6h
        if options:
            # Privilégier celle qui est la plus proche de 6h (360 min)
            meilleure = min(options, key=lambda x: abs(x[2] - self.DUREE_AVANT_PAUSE))
            type_opt, heure_pause, temps_avant = meilleure

            if type_opt == 'avant':
                avertissement += f"\n   → Pause déplacée AVANT la plage ({heure_pause.strftime('%H:%M')})"
            else:
                avertissement += f"\n   → Pause déplacée APRÈS la plage ({heure_pause.strftime('%H:%M')})"

            return heure_pause, temps_avant, avertissement

        # Si aucune option ne fonctionne, on retourne la pause idéale avec un avertissement renforcé
        temps_avant = int((heure_pause_ideale - self.heure_debut).total_seconds() / 60)
        avertissement += "\n   ⚠️  ATTENTION: Impossible d'éviter complètement le chevauchement!"
        return heure_pause_ideale, temps_avant, avertissement

    def calculer_heure_limite(self):
        """
        Calcule l'heure limite avant laquelle il faut badger pour partir en pause.
        Cette heure respecte la limite de 6H ET les plages de présence obligatoire.

        Returns:
            tuple: (heure_limite, avertissement)
        """
        # Heure limite théorique : début + 6H
        heure_limite_theorique = self.heure_debut + timedelta(minutes=self.DUREE_AVANT_PAUSE)

        # Vérifier si cette heure tombe pendant une plage obligatoire
        # Si oui, on doit partir AVANT la plage
        for plage_debut_str, plage_fin_str in self.PRESENCE_OBLIGATOIRE:
            plage_debut = self._parse_time(plage_debut_str)
            plage_fin = self._parse_time(plage_fin_str)

            # Si l'heure limite tombe pendant la plage, on doit partir AVANT
            if plage_debut <= heure_limite_theorique <= plage_fin:
                avertissement = f"⚠️  L'heure limite (6H) tombe pendant {plage_debut_str}-{plage_fin_str}"
                avertissement += f"\n   → Vous devez partir en pause AVANT {plage_debut_str}"
                return plage_debut, avertissement

        return heure_limite_theorique, None

    def calculer_fin_journee_interactive(self, heure_pause_reelle):
        """
        Calcule la fin de journée en fonction de l'heure réelle de départ en pause.

        Args:
            heure_pause_reelle: datetime de l'heure réelle du badge de pause

        Returns:
            dict avec tous les détails
        """
        # Calculer le temps de travail avant la pause
        temps_avant_pause = int((heure_pause_reelle - self.heure_debut).total_seconds() / 60)

        # Vérifier si on a dépassé les 6H (pénalité)
        penalite = 0
        if temps_avant_pause > self.DUREE_AVANT_PAUSE:
            penalite = 30  # 30 minutes de pénalité
            avertissement_penalite = f"⚠️  PÉNALITÉ : Vous avez dépassé 6H avant la pause ({temps_avant_pause//60}h{temps_avant_pause%60:02d})"
            avertissement_penalite += f"\n   → Ajout de 30 minutes supplémentaires à votre journée"
        else:
            avertissement_penalite = None

        # Heure de reprise
        heure_reprise = heure_pause_reelle + timedelta(minutes=self.duree_pause)

        # Temps perdu (si pause < 30 min)
        temps_perdu = self.PAUSE_MAX - self.duree_pause

        # Temps de travail après la pause (8H - temps_avant_pause + temps_perdu + pénalité)
        temps_apres_pause = (self.DUREE_TRAVAIL_JOURNEE - temps_avant_pause) + temps_perdu + penalite

        # Heure de fin
        heure_fin = heure_reprise + timedelta(minutes=temps_apres_pause)

        # Temps total
        temps_total = temps_avant_pause + temps_apres_pause

        return {
            'heure_pause': heure_pause_reelle,
            'temps_avant_pause': temps_avant_pause,
            'heure_reprise': heure_reprise,
            'temps_perdu': temps_perdu,
            'penalite': penalite,
            'temps_apres_pause': temps_apres_pause,
            'heure_fin': heure_fin,
            'temps_total': temps_total,
            'avertissement_penalite': avertissement_penalite
        }

    def calculer_horaires(self):
        """Calcule tous les horaires de la journée en tenant compte des plages obligatoires."""
        # Heure de départ en pause idéale (avant 6H de travail)
        heure_pause_ideale = self.heure_debut + timedelta(minutes=self.DUREE_AVANT_PAUSE)

        # Ajuster si nécessaire pour respecter les plages de présence obligatoire
        self.heure_pause, self.temps_avant_pause, self.avertissement = self._ajuster_pause_plage_obligatoire(
            heure_pause_ideale
        )

        # Heure de reprise après pause
        self.heure_reprise = self.heure_pause + timedelta(minutes=self.duree_pause)

        # Temps "perdu" (différence entre pause légale et pause réelle)
        self.temps_perdu = self.PAUSE_MAX - self.duree_pause

        # Temps de travail restant après la pause
        temps_apres_pause = (self.DUREE_TRAVAIL_JOURNEE - self.temps_avant_pause) + self.temps_perdu

        # Heure de fin
        self.heure_fin = self.heure_reprise + timedelta(minutes=temps_apres_pause)

    def afficher_heure_limite(self):
        """Affiche l'heure limite pour partir en pause (Phase 1)."""
        heure_limite, avertissement = self.calculer_heure_limite()

        print("\n" + "="*60)
        print(" PHASE 1 : HEURE LIMITE POUR LA PAUSE")
        print("="*60)

        # Affichage des plages de présence obligatoire
        print("\n📅 PLAGES DE PRÉSENCE OBLIGATOIRE :")
        for plage_debut, plage_fin in self.PRESENCE_OBLIGATOIRE:
            print(f"   • {plage_debut} - {plage_fin}")

        print(f"\n🕐 Premier pointage (début) : {self.heure_debut.strftime('%H:%M')}")

        if avertissement:
            print(f"\n{avertissement}")

        print(f"\n⏰ HEURE LIMITE pour badger (pause) : {heure_limite.strftime('%H:%M')}")
        print(f"   └─ Vous DEVEZ partir en pause AVANT cette heure")
        print(f"   └─ Sinon pénalité de +30 minutes sur votre journée")

        # Calcul du temps restant
        temps_restant_min = int((heure_limite - self.heure_debut).total_seconds() / 60)
        print(f"\n📊 Vous avez {temps_restant_min // 60}h{temps_restant_min % 60:02d} de travail avant la limite")

        print(f"\n💡 Pause prévue : {self.duree_pause} minutes")
        print(f"   └─ Temps perdu : {self.PAUSE_MAX - self.duree_pause} min")

        print("="*60 + "\n")

        return heure_limite

    def afficher_fin_journee_interactive(self, resultats):
        """Affiche le résumé de fin de journée (Phase 2)."""
        print("\n" + "="*60)
        print(" PHASE 2 : CALCUL DE FIN DE JOURNÉE")
        print("="*60)

        print(f"\n🕐 Premier pointage (début) : {self.heure_debut.strftime('%H:%M')}")
        print(f"\n⏸️  Badge PAUSE (réel) : {resultats['heure_pause'].strftime('%H:%M')}")
        print(f"   └─ Temps travaillé avant pause : {resultats['temps_avant_pause'] // 60}h{resultats['temps_avant_pause'] % 60:02d}")

        if resultats['avertissement_penalite']:
            print(f"\n{resultats['avertissement_penalite']}")

        print(f"\n💤 Durée de la pause : {self.duree_pause} minutes")
        print(f"   └─ Temps perdu (30 - {self.duree_pause}) : {resultats['temps_perdu']} min")

        if resultats['penalite'] > 0:
            print(f"   └─ Pénalité (dépassement 6H) : {resultats['penalite']} min")

        print(f"\n▶️  Reprise du travail : {resultats['heure_reprise'].strftime('%H:%M')}")
        print(f"\n🏁 FIN de journée : {resultats['heure_fin'].strftime('%H:%M')}")

        print(f"\n📊 Récapitulatif :")
        print(f"   - Temps avant pause : {resultats['temps_avant_pause'] // 60}h{resultats['temps_avant_pause'] % 60:02d}")
        print(f"   - Temps de pause : {self.duree_pause} min")
        print(f"   - Temps après pause : {resultats['temps_apres_pause'] // 60}h{resultats['temps_apres_pause'] % 60:02d}")
        if resultats['penalite'] > 0:
            print(f"   - Pénalité : {resultats['penalite']} min")
        print(f"   - TOTAL travail effectif : {resultats['temps_total'] // 60}h{resultats['temps_total'] % 60:02d}")
        print("="*60 + "\n")

    def afficher_resume(self):
        """Affiche le résumé de la journée."""
        print("\n" + "="*60)
        print(" PLANNING DE VOTRE JOURNÉE DE TRAVAIL")
        print("="*60)

        # Affichage des plages de présence obligatoire
        print("\n📅 PLAGES DE PRÉSENCE OBLIGATOIRE :")
        for plage_debut, plage_fin in self.PRESENCE_OBLIGATOIRE:
            print(f"   • {plage_debut} - {plage_fin}")

        print(f"\n🕐 Premier pointage (début) : {self.heure_debut.strftime('%H:%M')}")

        # Affichage de l'avertissement si nécessaire
        if self.avertissement:
            print(f"\n{self.avertissement}")

        print(f"\n⏸️  Départ en PAUSE : {self.heure_pause.strftime('%H:%M')}")
        print(f"   └─ Durée de la pause : {self.duree_pause} minutes")
        print(f"   └─ Temps perdu (30min - {self.duree_pause}min) : {self.temps_perdu} minutes")
        print(f"\n▶️  Reprise du travail : {self.heure_reprise.strftime('%H:%M')}")
        print(f"\n🏁 Fin de journée : {self.heure_fin.strftime('%H:%M')}")

        # Calcul du temps total de travail
        temps_avant_pause = self.temps_avant_pause
        temps_apres_pause = (self.DUREE_TRAVAIL_JOURNEE - self.temps_avant_pause) + self.temps_perdu
        temps_total = temps_avant_pause + temps_apres_pause

        print(f"\n📊 Récapitulatif :")
        print(f"   - Temps de travail avant pause : {temps_avant_pause // 60}h{temps_avant_pause % 60:02d}")
        print(f"   - Temps de pause : {self.duree_pause} min")
        print(f"   - Temps de travail après pause : {temps_apres_pause // 60}h{temps_apres_pause % 60:02d}")
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
  %(prog)s 09:00 --interactif       # MODE INTERACTIF : affiche l'heure limite, puis demande l'heure réelle
  %(prog)s 09:00 -i                 # Raccourci du mode interactif
  %(prog)s 09:00                    # Calcule les horaires pour un début à 9h00
  %(prog)s 09:00 --minuteur-pause   # Lance un minuteur jusqu'à la pause
  %(prog)s 09:00 --minuteur-fin     # Lance un minuteur jusqu'à la fin
  %(prog)s 09:00 --chronometre      # Lance un chronomètre de travail
  %(prog)s 09:00 --tout             # Lance tous les minuteurs en séquence
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

    parser.add_argument(
        "--interactif", "-i",
        action="store_true",
        help="Mode interactif en 2 phases : affiche l'heure limite, puis demande l'heure réelle de pause"
    )

    args = parser.parse_args()

    try:
        # Création de l'objet de gestion
        gestion = GestionBadgeage(args.heure_debut)

        # MODE INTERACTIF (en 2 phases)
        if args.interactif:
            # PHASE 1 : Afficher l'heure limite et lancer chrono/minuteur
            heure_limite = gestion.afficher_heure_limite()

            # Proposer un minuteur/chronomètre
            print("🤔 Que voulez-vous faire ?")
            print("   1. Lancer un MINUTEUR jusqu'à l'heure limite")
            print("   2. Lancer un CHRONOMÈTRE depuis maintenant")
            print("   3. Continuer sans minuteur")

            try:
                choix = input("\nVotre choix (1/2/3) : ").strip()

                if choix == "1":
                    temps_restant = gestion.temps_restant_avant(heure_limite)
                    if temps_restant > 0:
                        gestion.minuteur("Minuteur jusqu'à l'heure LIMITE", temps_restant)
                    else:
                        print("⚠️  L'heure limite est déjà passée !")

                elif choix == "2":
                    gestion._debut_reel = datetime.now()
                    gestion.chronometre()

            except (KeyboardInterrupt, EOFError):
                print("\n")

            # PHASE 2 : Demander l'heure réelle de pause
            print("\n" + "-"*60)
            print("📍 À quelle heure avez-vous badgé pour partir en pause ?")
            print("-"*60)

            while True:
                try:
                    heure_pause_str = input("Heure de pause (HH:MM) : ").strip()
                    heure_pause_reelle = datetime.strptime(heure_pause_str, "%H:%M")
                    heure_pause_reelle = gestion.heure_debut.replace(
                        hour=heure_pause_reelle.hour,
                        minute=heure_pause_reelle.minute,
                        second=0,
                        microsecond=0
                    )

                    # Vérifier que c'est après le début
                    if heure_pause_reelle < gestion.heure_debut:
                        print(f"❌ L'heure de pause ne peut pas être avant le début ({gestion.heure_debut.strftime('%H:%M')})")
                        continue

                    break

                except ValueError:
                    print("❌ Format invalide. Utilisez HH:MM (ex: 14:30)")
                except (KeyboardInterrupt, EOFError):
                    print("\n\n👋 Opération annulée.\n")
                    sys.exit(0)

            # Calculer la fin de journée
            resultats = gestion.calculer_fin_journee_interactive(heure_pause_reelle)

            # Afficher le résumé
            gestion.afficher_fin_journee_interactive(resultats)

            return

        # MODE NORMAL (affichage simple)
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
