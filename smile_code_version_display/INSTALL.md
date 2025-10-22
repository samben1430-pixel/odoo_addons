# Installation et Configuration

## Installation Rapide

### 1. Installer le Module

```bash
# Redémarrer Odoo avec mise à jour
odoo-bin -c odoo.conf -d votre_base -u smile_code_version_display

# Ou via l'interface : Apps → Search "Code Version Display" → Install
```

### 2. Activer l'Affichage

#### Via l'Interface Odoo

1. Allez dans **Settings → Technical → Parameters → System Parameters**
2. Cherchez la clé `code.version.display`
3. Changez la valeur à `True`
4. Rafraîchissez votre navigateur (F5)

#### Via SQL

```sql
UPDATE ir_config_parameter
SET value = 'True'
WHERE key = 'code.version.display';
```

#### Via Python Shell

```python
# Avec odoo shell
env['ir.config_parameter'].set_param('code.version.display', 'True')
```

### 3. Définir la Version du Code

#### Option A : Avec smile_upgrade (Automatique)

Si vous utilisez `smile_upgrade`, la version est gérée automatiquement.
Il vous suffit d'activer l'affichage (étape 2).

#### Option B : Manuellement

##### Via l'Interface

1. **Settings → Technical → Parameters → System Parameters**
2. Cliquez sur **Create**
3. Key: `code.version`
4. Value: `1.2.3` (votre version)
5. Sauvegardez

##### Via SQL

```sql
INSERT INTO ir_config_parameter (key, value)
VALUES ('code.version', '1.2.3')
ON CONFLICT (key) DO UPDATE SET value = '1.2.3';
```

##### Via Variable d'Environnement

```bash
export CODE_VERSION="1.2.3"
odoo-bin -c odoo.conf
```

Note : Les variables d'environnement sont utilisées en fallback si `code.version` n'existe pas en base.

## Configuration Avancée

### Désactiver pour un Utilisateur Spécifique

Le badge est visible par tous les utilisateurs. Si vous voulez le réserver à certains utilisateurs :

Modifiez `static/src/js/code_version_systray.js` :

```javascript
export const systrayItem = {
    Component: CodeVersionSystray,
    isDisplayed: (env) => {
        // Afficher seulement pour les utilisateurs système
        return env.services.user.isSystem;
    },
};
```

### Personnaliser le Style

Éditez `static/src/xml/code_version_systray.xml` pour changer les couleurs :

```xml
<!-- Thème rouge pour DEV -->
<button style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); ...">

<!-- Thème orange pour QA -->
<button style="background: linear-gradient(135deg, #f46b45 0%, #eea849 100%); ...">

<!-- Thème bleu pour STAGING -->
<button style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); ...">
```

### Ajouter un Préfixe d'Environnement

Modifiez `models/code_version.py` pour ajouter un préfixe :

```python
@api.model
def get_version_info(self):
    IrConfigParam = self.env["ir.config_parameter"].sudo()
    version = IrConfigParam.get_param("code.version", default="N/A")

    # Ajouter préfixe d'environnement
    env_name = IrConfigParam.get_param("environment.name", default="")
    if env_name:
        version = f"{env_name}-{version}"

    return {
        "version": version,
        "display": IrConfigParam.get_param("code.version.display", "False") == "True",
    }
```

Puis définissez `environment.name` :

```sql
INSERT INTO ir_config_parameter (key, value)
VALUES ('environment.name', 'DEV')
ON CONFLICT (key) DO UPDATE SET value = 'DEV';
```

Résultat : le badge affichera `DEV-1.2.3`

## Configuration Multi-Environnements

### Structure Recommandée

```
/opt/odoo/
├── config/
│   ├── dev.conf
│   ├── qa.conf
│   ├── staging.conf
│   └── prod.conf
├── scripts/
│   ├── set_version.sh
│   └── deploy.sh
└── addons/
    └── smile_code_version_display/
```

### Script `set_version.sh`

```bash
#!/bin/bash

DB_NAME=$1
VERSION=$2
DISPLAY=${3:-True}  # True par défaut, False pour prod

psql -d $DB_NAME << EOF
INSERT INTO ir_config_parameter (key, value)
VALUES
    ('code.version', '$VERSION'),
    ('code.version.display', '$DISPLAY')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
EOF

echo "✓ Version $VERSION set for database $DB_NAME (display: $DISPLAY)"
```

Usage :

```bash
# DEV - Afficher la version
./set_version.sh odoo_dev 1.2.3-dev True

# QA - Afficher la version
./set_version.sh odoo_qa 1.2.3-rc1 True

# PROD - Cacher la version
./set_version.sh odoo_prod 1.2.3 False
```

### Configuration par Environnement

#### dev.conf

```ini
[options]
db_name = odoo_dev
# autres options...
```

```sql
-- Configuration DEV
UPDATE ir_config_parameter SET value = 'DEV' WHERE key = 'environment.name';
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';
```

#### qa.conf

```ini
[options]
db_name = odoo_qa
# autres options...
```

```sql
-- Configuration QA
UPDATE ir_config_parameter SET value = 'QA' WHERE key = 'environment.name';
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';
```

#### prod.conf

```ini
[options]
db_name = odoo_prod
# autres options...
```

```sql
-- Configuration PROD (désactivé)
UPDATE ir_config_parameter SET value = 'PROD' WHERE key = 'environment.name';
UPDATE ir_config_parameter SET value = 'False' WHERE key = 'code.version.display';
```

## Intégration avec Déploiement

### Avec Git Hooks

Créez `.git/hooks/post-merge` :

```bash
#!/bin/bash

VERSION=$(git describe --tags --always)
DB_NAME=$(grep db_name odoo.conf | cut -d= -f2 | tr -d ' ')

echo "Updating version to $VERSION in database $DB_NAME"

psql -d $DB_NAME -c "
    UPDATE ir_config_parameter
    SET value = '$VERSION'
    WHERE key = 'code.version';
"

echo "✓ Version updated"
```

```bash
chmod +x .git/hooks/post-merge
```

### Avec Docker

Dans votre `Dockerfile` :

```dockerfile
FROM odoo:17.0

# Récupérer la version depuis un argument de build
ARG CODE_VERSION=dev
ENV CODE_VERSION=${CODE_VERSION}

COPY ./custom_addons /mnt/extra-addons

# Script d'initialisation pour définir la version
COPY ./set_version.sh /docker-entrypoint-init.d/
```

`set_version.sh` :

```bash
#!/bin/bash
if [ ! -z "$CODE_VERSION" ]; then
    psql -U $USER -d $POSTGRES_DB -c "
        INSERT INTO ir_config_parameter (key, value)
        VALUES ('code.version', '$CODE_VERSION')
        ON CONFLICT (key) DO UPDATE SET value = '$CODE_VERSION';
    "
fi
```

Build et run :

```bash
docker build --build-arg CODE_VERSION=1.2.3 -t myodoo:1.2.3 .
docker run -e CODE_VERSION=1.2.3 myodoo:1.2.3
```

### Avec Kubernetes

ConfigMap `odoo-version.yaml` :

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: odoo-version
data:
  CODE_VERSION: "1.2.3"
  CODE_VERSION_DISPLAY: "True"
```

Deployment `odoo-deployment.yaml` :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odoo
spec:
  template:
    spec:
      containers:
      - name: odoo
        envFrom:
        - configMapRef:
            name: odoo-version
```

Mise à jour de version :

```bash
kubectl create configmap odoo-version \
  --from-literal=CODE_VERSION=1.2.4 \
  --from-literal=CODE_VERSION_DISPLAY=True \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl rollout restart deployment/odoo
```

## Vérification

### Tester l'Installation

```bash
# Vérifier que le module est installé
psql -d odoo_dev -c "SELECT state FROM ir_module_module WHERE name = 'smile_code_version_display';"
# Devrait retourner: installed

# Vérifier les paramètres
psql -d odoo_dev -c "SELECT key, value FROM ir_config_parameter WHERE key LIKE 'code.version%';"
# Devrait afficher:
# code.version | 1.2.3
# code.version.display | True
```

### Logs Odoo

Si le badge n'apparaît pas, vérifiez les logs :

```bash
tail -f /var/log/odoo/odoo.log | grep -i version
```

Recherchez les erreurs JavaScript dans la console navigateur (F12).

## Dépannage

### Le badge n'apparaît pas

1. **Vérifier que le module est installé** : Apps → Installed → chercher "Code Version Display"
2. **Vérifier le paramètre** : `code.version.display = True`
3. **Vérifier le cache** : Ctrl+Shift+R (hard refresh)
4. **Vérifier la console JS** : F12 → Console → chercher des erreurs

### La version affiche "N/A"

1. **Définir code.version** : voir section 3 ci-dessus
2. **Vérifier les droits** : le paramètre doit être lisible par tous

### Le badge apparaît mais est vide

Vérifier que le modèle `code.version.display` est bien chargé :

```python
# Odoo shell
env['code.version.display'].get_version_info()
# Devrait retourner: {'version': '1.2.3', 'display': True}
```

## Désinstallation

```bash
# Via Odoo
# Apps → Code Version Display → Uninstall

# Nettoyer les paramètres (optionnel)
psql -d votre_base -c "
    DELETE FROM ir_config_parameter
    WHERE key IN ('code.version.display', 'code.version');
"
```

## Support

Pour toute question ou problème :

- Ouvrez une issue sur GitHub : https://github.com/Smile-SA/odoo_addons/issues
- Documentation : voir README.rst et INTEGRATION_GUIDE.md
