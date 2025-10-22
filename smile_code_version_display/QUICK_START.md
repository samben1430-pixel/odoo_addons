# Démarrage Rapide - 5 Minutes

## Installation en 3 Étapes

### 1️⃣ Installer le Module (1 min)

```bash
cd /home/user/odoo_addons
odoo-bin -c odoo.conf -d ma_base -u smile_code_version_display
```

### 2️⃣ Activer l'Affichage (1 min)

Connectez-vous à votre base Odoo :

```sql
psql -d ma_base << EOF
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';
INSERT INTO ir_config_parameter (key, value) VALUES ('code.version', '1.0.0')
ON CONFLICT (key) DO UPDATE SET value = '1.0.0';
EOF
```

Ou via l'interface Odoo :
- **Settings → Technical → System Parameters**
- Chercher `code.version.display` → mettre `True`
- Créer `code.version` → mettre votre version (ex: `1.0.0`)

### 3️⃣ Voir le Résultat (immédiat)

Rafraîchissez votre navigateur (F5) → Vous verrez un badge violet avec votre version en haut à droite ! 🎉

---

## Utilisation avec smile_upgrade

Si vous utilisez déjà `smile_upgrade` :

```bash
# Installation
odoo-bin -c odoo.conf -d ma_base -u smile_code_version_display

# Configuration (juste activer l'affichage)
psql -d ma_base -c "UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';"
```

La version sera automatiquement récupérée depuis `smile_upgrade` ! ✨

---

## Configuration DEV/QA/STAGING

### Environnement DEV

```sql
psql -d odoo_dev << EOF
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';
UPDATE ir_config_parameter SET value = 'DEV-1.0.0' WHERE key = 'code.version';
EOF
```

### Environnement QA

```sql
psql -d odoo_qa << EOF
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';
UPDATE ir_config_parameter SET value = 'QA-1.0.0' WHERE key = 'code.version';
EOF
```

### Environnement PROD (désactivé)

```sql
psql -d odoo_prod << EOF
UPDATE ir_config_parameter SET value = 'False' WHERE key = 'code.version.display';
EOF
```

---

## Intégration avec Votre Module Ribbon

Vous avez déjà un module ribbon ? Super ! Les deux fonctionnent ensemble :

1. **Installez les deux modules** :
   ```bash
   odoo-bin -c odoo.conf -d ma_base -u votre_module_ribbon,smile_code_version_display
   ```

2. **Activez l'affichage de version** (voir étape 2 ci-dessus)

3. **Résultat** : Ribbon + Badge de version côte à côte ! 🎨

---

## Automatisation avec Git

Créez `.git/hooks/post-checkout` :

```bash
#!/bin/bash
VERSION=$(git describe --tags --always --dirty)
DB=$(grep db_name odoo.conf | cut -d= -f2 | tr -d ' ')

psql -d $DB -c "UPDATE ir_config_parameter SET value = '$VERSION' WHERE key = 'code.version';" 2>/dev/null || true
echo "✓ Version mise à jour : $VERSION"
```

```bash
chmod +x .git/hooks/post-checkout
```

Maintenant, chaque fois que vous changez de branche, la version s'actualise automatiquement ! 🚀

---

## Vérification

Testez que tout fonctionne :

```bash
# Vérifier l'installation
psql -d ma_base -c "SELECT state FROM ir_module_module WHERE name = 'smile_code_version_display';"
# → Résultat attendu : installed

# Vérifier la configuration
psql -d ma_base -c "SELECT key, value FROM ir_config_parameter WHERE key LIKE 'code.version%';"
# → Résultat attendu :
# code.version          | 1.0.0
# code.version.display  | True
```

Puis ouvrez Odoo dans votre navigateur et regardez en haut à droite ! 👀

---

## Dépannage Express

❌ **Le badge n'apparaît pas ?**
1. Videz le cache : Ctrl+Shift+R
2. Vérifiez la console JS : F12 → onglet Console
3. Vérifiez `code.version.display = True`

❌ **Le badge affiche "N/A" ?**
- Définissez `code.version` (voir étape 2)

❌ **Erreur au démarrage ?**
- Vérifiez que `web` est dans les dépendances
- Redémarrez Odoo : `systemctl restart odoo`

---

## Documentation Complète

- **README.rst** : Documentation détaillée
- **INSTALL.md** : Guide d'installation complet
- **INTEGRATION_GUIDE.md** : Intégration avec ribbon et CI/CD

---

**C'est tout ! Vous êtes prêt à utiliser le module. Bon développement ! 🎉**
