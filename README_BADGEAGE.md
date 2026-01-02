# 🕐 Gestion du Badgeage - Script Python

Ce script vous aide à gérer vos heures de travail avec les contraintes de pause légales.

## 📋 Contraintes

- **Durée de travail** : 8 heures par jour
- **Pause obligatoire** : Avant d'atteindre 6 heures de travail (dans la mesure du possible)
- **Durée de pause** :
  - Minimum : 15 minutes (pour être valable)
  - Optimale : 17-27 minutes (calculée aléatoirement par le script)
  - Maximum légal : 30 minutes (temps non décompté du travail)
- **Perte de temps** : Si pause < 30 min, le temps restant (30 - durée_pause) s'ajoute à votre temps de travail
- **Plages de présence obligatoire** :
  - **9h30 - 11h30** (matin)
  - **14h30 - 15h30** (après-midi)
  - Le script ajuste automatiquement la pause pour ne pas chevaucher ces plages

## 🚀 Installation

Le script est déjà dans le dépôt. Aucune installation supplémentaire nécessaire (Python 3 requis).

```bash
chmod +x gestion_badgeage.py
```

## 💡 Utilisation

### ⭐ Mode interactif (RECOMMANDÉ) - En 2 phases

C'est le mode recommandé pour une utilisation quotidienne. Il fonctionne en 2 étapes :

**PHASE 1** : Affiche l'heure limite avant laquelle vous devez badger pour la pause
**PHASE 2** : Calcule votre heure de fin selon l'heure réelle de votre badge

```bash
python3 gestion_badgeage.py 09:00 --interactif
# ou raccourci :
python3 gestion_badgeage.py 09:00 -i
```

**Ce qui se passe :**
1. Le script affiche l'heure limite (avant 6H de travail)
2. Vous pouvez lancer un minuteur/chronomètre si vous voulez
3. Quand vous badgez réellement pour la pause, vous entrez l'heure
4. Le script calcule votre heure de fin exacte

**Avantages :**
- ✅ Vous voyez clairement l'heure limite à ne pas dépasser
- ✅ Vous entrez l'heure réelle de votre badge (plus flexible)
- ✅ Détection automatique si vous dépassez 6H (pénalité affichée)
- ✅ Calcul précis de votre fin de journée

### Mode basique - Affichage des horaires

```bash
python3 gestion_badgeage.py 09:00
```

**Résultat exemple :**
```
============================================================
 PLANNING DE VOTRE JOURNÉE DE TRAVAIL
============================================================

🕐 Premier pointage (début) : 09:00

⏸️  Départ en PAUSE (avant 6H) : 15:00
   └─ Durée de la pause : 23 minutes
   └─ Temps perdu (30min - 23min) : 7 minutes

▶️  Reprise du travail : 15:23

🏁 Fin de journée : 17:30

📊 Récapitulatif :
   - Temps de travail matin : 6h00
   - Temps de pause : 23 min
   - Temps de travail après-midi : 2h07
   - TOTAL travail effectif : 8h07
============================================================
```

### ⏱️ Mode minuteur - Jusqu'à la pause

Lance un compte à rebours jusqu'à l'heure de votre pause :

```bash
python3 gestion_badgeage.py 09:00 --minuteur-pause
```

### ⏱️ Mode minuteur - Durée de la pause

Lance un minuteur pour la durée de votre pause (utile pendant la pause) :

```bash
python3 gestion_badgeage.py 09:00 --minuteur-reprise
```

### ⏱️ Mode minuteur - Jusqu'à la fin

Lance un compte à rebours jusqu'à la fin de votre journée :

```bash
python3 gestion_badgeage.py 09:00 --minuteur-fin
```

### ⏱️ Mode chronomètre

Lance un chronomètre qui affiche le temps écoulé depuis le début (utile pour suivre votre progression) :

```bash
python3 gestion_badgeage.py 09:00 --chronometre
```

### 🎯 Mode complet - Tous les minuteurs en séquence

Lance automatiquement tous les minuteurs les uns après les autres :

```bash
python3 gestion_badgeage.py 09:00 --tout
```

**Cette commande va :**
1. Afficher votre planning
2. Lancer un minuteur jusqu'à la pause
3. Sonner et lancer le minuteur de pause
4. Sonner et lancer le minuteur jusqu'à la fin
5. Sonner à la fin de journée

## 📱 Cas d'usage pratiques

### Début de journée
```bash
# Arrivée au bureau à 8h45
python3 gestion_badgeage.py 08:45

# Si vous voulez suivre toute la journée automatiquement
python3 gestion_badgeage.py 08:45 --tout
```

### En cours de journée
```bash
# Juste avant la pause, pour savoir combien de temps elle dure
python3 gestion_badgeage.py 09:00 --minuteur-reprise

# Après la pause, pour savoir quand finir
python3 gestion_badgeage.py 09:00 --minuteur-fin
```

### Suivi en temps réel
```bash
# Lancer un chronomètre pour voir où vous en êtes
python3 gestion_badgeage.py 09:00 --chronometre
```

## 🔧 Arrêter un minuteur/chronomètre

Appuyez sur `Ctrl+C` pour arrêter le minuteur ou chronomètre en cours.

## 📊 Logique de calcul

Le script applique la logique suivante :

1. **Premier badge** à T0
2. **Heure limite de pause** : T0 + 6h maximum (avant les 6 heures réglementaires)
   - Si l'heure limite tombe dans une plage obligatoire, elle est ajustée AVANT la plage
3. **Badge de pause réel** : L'heure où vous badgez effectivement
4. **Vérification de pénalité** :
   - Si vous partez en pause **AVANT** 6H de travail → ✅ Pas de pénalité
   - Si vous partez en pause **APRÈS** 6H de travail → ⚠️ Pénalité de **+30 minutes**
5. **Durée de pause** : Aléatoire entre 17 et 27 minutes
6. **Temps perdu** : 30 min - durée_pause (ex: si pause de 23 min → 7 min perdues)
7. **Reprise** : Heure de pause + durée de pause
8. **Fin de journée** : Reprise + (8h - temps avant pause) + temps perdu + pénalité (si applicable)

## 📝 Exemples concrets (Mode Interactif)

### ✅ Cas 1 : Début 09:00, pause à 13:45 (AVANT 6H - OK)
**Phase 1** :
- Début : 09:00
- Heure limite : 14:30 (ajustée car 15:00 tombe dans 14:30-15:30)
- Vous avez 5h30 avant la limite

**Phase 2** :
- Badge pause réel : 13:45 (4h45 de travail)
- ✅ Pas de pénalité (< 6H)
- Durée pause : 21 min
- Reprise : 14:06
- Temps perdu : 9 min
- **Fin : 17:30** (8h09 de travail)

### ⚠️ Cas 2 : Début 09:00, pause à 15:30 (APRÈS 6H - PÉNALITÉ)
**Phase 1** :
- Début : 09:00
- Heure limite : 14:30
- Vous avez 5h30 avant la limite

**Phase 2** :
- Badge pause réel : 15:30 (6h30 de travail)
- ⚠️ **PÉNALITÉ +30 min** (dépassement 6H)
- Durée pause : 18 min
- Reprise : 15:48
- Temps perdu : 12 min
- Pénalité : 30 min
- **Fin : 18:00** (8h42 de travail au lieu de 8h12)

### ✅ Cas 3 : Début 08:00, pause à 13:30 (AVANT 6H - OK)
**Phase 1** :
- Début : 08:00
- Heure limite : 14:00 (pas de chevauchement)
- Vous avez 6h00 avant la limite

**Phase 2** :
- Badge pause réel : 13:30 (5h30 de travail)
- ✅ Pas de pénalité
- Durée pause : 19 min
- Reprise : 13:49
- Temps perdu : 11 min
- **Fin : 16:30** (8h11 de travail)

## 🎲 Pourquoi une pause aléatoire ?

La pause est générée aléatoirement entre 17 et 27 minutes pour :
- Varier légèrement vos horaires de pause
- Rester dans la fourchette légale (< 30 min)
- Optimiser votre temps (pause courte = moins de temps perdu)

## ❓ FAQ

**Q : C'est quoi le mode interactif et pourquoi l'utiliser ?**
R : Le mode interactif (`--interactif` ou `-i`) vous montre d'abord l'heure limite pour partir en pause (avant 6H), puis vous demande l'heure réelle de votre badge. C'est plus flexible car vous n'êtes pas obligé de partir exactement à 6H. C'est le mode RECOMMANDÉ pour une utilisation quotidienne.

**Q : Que se passe-t-il si je dépasse 6H avant de partir en pause ?**
R : Vous aurez une **pénalité de +30 minutes** ajoutée à votre journée de travail. Par exemple, si vous devriez finir à 17:30 mais que vous dépassez 6H, vous finirez à 18:00.

**Q : Pourquoi je dois travailler 8h09 ou 8h12 et pas exactement 8h ?**
R : Parce que votre pause dure moins de 30 minutes. La loi autorise 30 min de pause, donc si vous prenez 21 min, les 9 min restantes (30-21) s'ajoutent à votre journée de travail.

**Q : Comment faire exactement 8h de travail ?**
R : Il faudrait prendre exactement 30 minutes de pause ET ne pas dépasser les 6H avant la pause. Mais le script génère une pause aléatoire entre 17-27 min pour optimiser votre temps.

**Q : Pourquoi l'heure limite n'est pas toujours à 6h après mon début ?**
R : Si 6H après votre début tombe pendant une plage de présence obligatoire (9h30-11h30 ou 14h30-15h30), l'heure limite est ajustée AVANT la plage. Par exemple, si vous commencez à 09:00, l'heure limite sera 14:30 (au lieu de 15:00).

**Q : Je peux utiliser le mode interactif avec un minuteur ?**
R : Oui ! En mode interactif, après avoir vu l'heure limite, le script vous propose de lancer un minuteur jusqu'à cette heure ou un chronomètre pour suivre votre temps de travail.

**Q : Je peux changer les plages de présence obligatoire ?**
R : Oui, modifiez la constante `PRESENCE_OBLIGATOIRE` dans le code (lignes 34-37). Format : `("HH:MM", "HH:MM")`.

**Q : Je peux changer la fourchette de pause ?**
R : Oui, modifiez les variables `PAUSE_RANDOM_MIN` et `PAUSE_RANDOM_MAX` dans le code (lignes 30-31).

## 📝 Licence

Ce script est fourni tel quel pour votre usage personnel.
