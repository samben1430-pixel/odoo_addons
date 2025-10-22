# Guide d'Intégration avec Module Ribbon

Ce guide explique comment intégrer `smile_code_version_display` avec votre module ribbon existant.

## Option 1 : Utilisation en Complément (Recommandé)

Utilisez les deux modules ensemble sans modification. Ils fonctionnent côte à côte parfaitement.

### Exemple de Configuration Multi-Environnements

#### Environnement DEV (`odoo-dev.conf`)

```ini
[options]
db_name = odoo_dev
upgrades_path = /opt/odoo/upgrades
ribbon_name = DEVELOPMENT
ribbon_color = #FF0000
```

Puis en SQL ou via l'interface :

```sql
-- Activer l'affichage de la version
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';

-- Définir la version
UPDATE ir_config_parameter SET value = '2.1.0-dev' WHERE key = 'code.version';
```

#### Environnement QA (`odoo-qa.conf`)

```ini
[options]
db_name = odoo_qa
upgrades_path = /opt/odoo/upgrades
ribbon_name = QA
ribbon_color = #FFA500
```

```sql
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'code.version.display';
UPDATE ir_config_parameter SET value = '2.1.0-rc1' WHERE key = 'code.version';
```

## Option 2 : Intégration dans Votre Module Ribbon

Si vous voulez fusionner la fonctionnalité dans votre module ribbon :

### 1. Ajouter la Dépendance

Dans `votre_module_ribbon/__manifest__.py` :

```python
{
    'name': 'Your Environment Ribbon',
    'depends': ['web', 'smile_code_version_display'],
    # ...
}
```

### 2. Étendre le Composant (JavaScript)

Créez `votre_module_ribbon/static/src/js/ribbon_with_version.js` :

```javascript
/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { CodeVersionSystray } from "@smile_code_version_display/js/code_version_systray";

// Patch pour personnaliser l'apparence selon l'environnement
patch(CodeVersionSystray.prototype, {
    getStyle() {
        const env = odoo.session_info.ribbon_env || 'dev';
        const colors = {
            'dev': 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)',
            'qa': 'linear-gradient(135deg, #f46b45 0%, #eea849 100%)',
            'staging': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        };
        return colors[env] || colors['dev'];
    }
});
```

## Option 3 : Composant Unique Ribbon + Version

Créez un composant personnalisé qui affiche le ribbon ET la version :

### `votre_module/static/src/js/ribbon_version_component.js`

```javascript
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class RibbonWithVersion extends Component {
    static template = "votre_module.RibbonWithVersion";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            version: "",
            environment: odoo.session_info.ribbon_env || "DEV",
            display: false,
        });

        onWillStart(async () => {
            const data = await this.orm.call(
                "code.version.display",
                "get_version_info",
                []
            );
            Object.assign(this.state, {
                version: data.version,
                display: data.display,
            });
        });
    }

    get ribbonColor() {
        const colors = {
            'DEV': '#eb3349',
            'QA': '#f46b45',
            'STAGING': '#4facfe',
            'PROD': '#28a745',
        };
        return colors[this.state.environment] || colors['DEV'];
    }
}

registry.category("systray").add("RibbonWithVersion", {
    Component: RibbonWithVersion,
}, { sequence: 1 });
```

### `votre_module/static/src/xml/ribbon_version_component.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="votre_module.RibbonWithVersion">
        <t t-if="state.display">
            <div class="ribbon-version-container" style="display: flex; gap: 10px; align-items: center;">
                <!-- Environment Ribbon -->
                <div class="env-ribbon" t-att-style="`background: ${ribbonColor}; color: white; padding: 5px 12px; border-radius: 4px; font-weight: 600;`">
                    <t t-esc="state.environment"/>
                </div>

                <!-- Version Badge -->
                <div class="version-badge" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 5px 12px; border-radius: 4px; font-weight: 600;">
                    <i class="fa fa-code-fork"/>
                    <t t-esc="state.version"/>
                </div>
            </div>
        </t>
    </t>
</templates>
```

## Automatisation du Déploiement

### Script de Déploiement avec Version

Créez `deploy.sh` :

```bash
#!/bin/bash

# Récupérer la version depuis git
VERSION=$(git describe --tags --always)
ENVIRONMENT=$1  # dev, qa, staging, prod

echo "Deploying version $VERSION to $ENVIRONMENT"

# Mettre à jour la base de données
psql -d odoo_$ENVIRONMENT -c "
    UPDATE ir_config_parameter
    SET value = '$VERSION'
    WHERE key = 'code.version';

    -- Activer l'affichage pour dev/qa/staging uniquement
    UPDATE ir_config_parameter
    SET value = CASE
        WHEN '$ENVIRONMENT' IN ('dev', 'qa', 'staging') THEN 'True'
        ELSE 'False'
    END
    WHERE key = 'code.version.display';
"

# Redémarrer Odoo
systemctl restart odoo-$ENVIRONMENT

echo "Deployment complete!"
```

### Utilisation avec Docker

Dans votre `docker-compose.yml` :

```yaml
version: '3.8'
services:
  odoo:
    image: odoo:17.0
    environment:
      - CODE_VERSION=${GIT_TAG:-dev}
      - DB_NAME=odoo_dev
    command: >
      bash -c "
      odoo --load=web,smile_upgrade,smile_code_version_display &&
      psql -d odoo_dev -c \"UPDATE ir_config_parameter SET value = '$$CODE_VERSION' WHERE key = 'code.version'\"
      "
```

Puis :

```bash
export GIT_TAG=$(git describe --tags)
docker-compose up -d
```

## Intégration CI/CD

### GitLab CI (.gitlab-ci.yml)

```yaml
deploy_to_qa:
  stage: deploy
  script:
    - export VERSION=$(git describe --tags --always)
    - echo "Deploying version $VERSION to QA"
    - ssh qa-server "cd /opt/odoo && git pull"
    - ssh qa-server "psql -d odoo_qa -c \"UPDATE ir_config_parameter SET value = '$VERSION' WHERE key = 'code.version'\""
    - ssh qa-server "systemctl restart odoo"
  only:
    - qa
```

### GitHub Actions

```yaml
name: Deploy to QA

on:
  push:
    branches: [ qa ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Get version
        id: version
        run: echo "::set-output name=version::$(git describe --tags --always)"

      - name: Update version in database
        run: |
          psql ${{ secrets.QA_DB_URL }} -c "
            UPDATE ir_config_parameter
            SET value = '${{ steps.version.outputs.version }}'
            WHERE key = 'code.version'
          "
```

## Personnalisation Avancée

### Afficher Plus d'Informations

Modifiez `models/code_version.py` pour retourner plus de données :

```python
@api.model
def get_version_info(self):
    IrConfigParam = self.env["ir.config_parameter"].sudo()

    return {
        "version": IrConfigParam.get_param("code.version", "N/A"),
        "display": IrConfigParam.get_param("code.version.display") == "True",
        "environment": IrConfigParam.get_param("environment.name", "DEV"),
        "deployed_at": IrConfigParam.get_param("deploy.timestamp", "Unknown"),
        "git_commit": IrConfigParam.get_param("git.commit.sha", "Unknown"),
    }
```

### Ajouter une Popup d'Information

Dans `code_version_systray.js`, modifiez `onClick()` :

```javascript
onClick() {
    const { notification } = this.env.services;
    notification.add(
        `Code Version: ${this.state.version}\n` +
        `Environment: ${this.state.environment}\n` +
        `Deployed: ${this.state.deployed_at}`,
        {
            title: "Version Information",
            type: "info",
        }
    );
}
```

## Conclusion

Choisissez l'option qui convient le mieux à votre architecture :

- **Option 1** : Simple, modulaire, facile à maintenir (recommandé)
- **Option 2** : Bonne intégration, garde les modules séparés
- **Option 3** : Composant unique, personnalisation maximale

Pour la plupart des cas, l'**Option 1** est suffisante et maintient une bonne séparation des responsabilités.
