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
2. **Calcul de la pause idéale** : T0 + 6h (juste avant les 6 heures réglementaires)
3. **Vérification des plages obligatoires** : Si la pause chevauche 9h30-11h30 ou 14h30-15h30, elle est automatiquement ajustée
4. **Durée de pause** : Aléatoire entre 17 et 27 minutes
5. **Temps perdu** : 30 min - durée_pause (ex: si pause de 23 min → 7 min perdues)
6. **Reprise** : Heure de pause + durée de pause
7. **Fin de journée** : Reprise + (8h - temps avant pause) + temps perdu

## 📝 Exemples concrets

### Cas 1 : Début à 08:00 (pas de chevauchement)
- Début : 08:00
- Pause : 14:00 (après 6h, avant la plage 14:30-15:30) ✅
- Durée pause : 24 minutes
- Reprise : 14:24
- Temps perdu : 6 minutes
- Fin : 16:30

### Cas 2 : Début à 09:00 (chevauchement avec 14:30-15:30)
- Début : 09:00
- Pause idéale : 15:00 ❌ (chevauche 14:30-15:30)
- **Pause ajustée** : 14:12 ✅ (reprend à 14:30)
- Durée pause : 18 minutes
- Reprise : 14:30 (début de la plage obligatoire)
- Temps perdu : 12 minutes
- Fin : 17:30

### Cas 3 : Début à 10:00 (pas de chevauchement)
- Début : 10:00
- Pause : 16:00 (après 6h, après la plage 14:30-15:30) ✅
- Durée pause : 22 minutes
- Reprise : 16:22
- Temps perdu : 8 minutes
- Fin : 18:30

## 🎲 Pourquoi une pause aléatoire ?

La pause est générée aléatoirement entre 17 et 27 minutes pour :
- Varier légèrement vos horaires de pause
- Rester dans la fourchette légale (< 30 min)
- Optimiser votre temps (pause courte = moins de temps perdu)

## ❓ FAQ

**Q : Pourquoi je dois travailler 8h03 ou 8h07 et pas exactement 8h ?**
R : Parce que votre pause dure moins de 30 minutes. La loi autorise 30 min de pause, donc si vous prenez moins, le temps non utilisé s'ajoute à votre journée.

**Q : Comment faire exactement 8h ?**
R : Prenez exactement 30 minutes de pause. Mais le script génère entre 17-27 min pour optimiser votre temps.

**Q : Je peux changer la fourchette de pause ?**
R : Oui, modifiez les variables `PAUSE_RANDOM_MIN` et `PAUSE_RANDOM_MAX` dans le code (lignes 30-31).

**Q : Pourquoi ma pause n'est pas à 6h exactement après mon début ?**
R : Si votre pause de 6h tomberait pendant une plage de présence obligatoire (9h30-11h30 ou 14h30-15h30), le script la déplace automatiquement pour respecter ces contraintes.

**Q : Que faire si je commence très tôt ou très tard ?**
R : Le script s'adapte automatiquement. Si vous commencez à 07:00, la pause sera vers 13:00 (pas de chevauchement). Si vous commencez à 11:00, la pause sera vers 17:00.

**Q : Je peux changer les plages de présence obligatoire ?**
R : Oui, modifiez la constante `PRESENCE_OBLIGATOIRE` dans le code (lignes 34-37). Format : `("HH:MM", "HH:MM")`.

## 📝 Licence

Ce script est fourni tel quel pour votre usage personnel.
