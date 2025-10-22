#!/bin/bash

# Script de configuration pour différents environnements
# Usage: ./environment_setup.sh <environment> <version> <database>
# Example: ./environment_setup.sh dev 1.2.3 odoo_dev

set -e

ENVIRONMENT=$1
VERSION=$2
DATABASE=$3

if [ -z "$ENVIRONMENT" ] || [ -z "$VERSION" ] || [ -z "$DATABASE" ]; then
    echo "Usage: $0 <environment> <version> <database>"
    echo "Example: $0 dev 1.2.3 odoo_dev"
    exit 1
fi

echo "🔧 Configuration de l'environnement $ENVIRONMENT"
echo "📦 Version: $VERSION"
echo "🗄️  Base de données: $DATABASE"
echo ""

# Définir si l'affichage doit être activé selon l'environnement
case $ENVIRONMENT in
    dev|DEV|development|DEVELOPMENT)
        DISPLAY="True"
        ENV_NAME="DEV"
        echo "✓ Mode DÉVELOPPEMENT - affichage activé"
        ;;
    qa|QA|test|TEST|testing|TESTING)
        DISPLAY="True"
        ENV_NAME="QA"
        echo "✓ Mode QA/TEST - affichage activé"
        ;;
    staging|STAGING|preprod|PREPROD)
        DISPLAY="True"
        ENV_NAME="STAGING"
        echo "✓ Mode STAGING - affichage activé"
        ;;
    prod|PROD|production|PRODUCTION)
        DISPLAY="False"
        ENV_NAME="PROD"
        echo "⚠️  Mode PRODUCTION - affichage désactivé"
        ;;
    *)
        echo "❌ Environnement inconnu: $ENVIRONMENT"
        echo "Valeurs acceptées: dev, qa, staging, prod"
        exit 1
        ;;
esac

# Appliquer la configuration
echo ""
echo "Application de la configuration..."

psql -d $DATABASE << EOF
-- Mise à jour des paramètres système
INSERT INTO ir_config_parameter (key, value) VALUES
    ('code.version', '$VERSION'),
    ('code.version.display', '$DISPLAY'),
    ('environment.name', '$ENV_NAME')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Afficher le résultat
SELECT key, value FROM ir_config_parameter WHERE key LIKE 'code.version%' OR key = 'environment.name';
EOF

echo ""
echo "✅ Configuration terminée avec succès !"
echo ""
echo "Prochaines étapes :"
echo "1. Redémarrez Odoo si nécessaire"
echo "2. Rafraîchissez votre navigateur (Ctrl+Shift+R)"
echo "3. Le badge devrait apparaître en haut à droite"
echo ""
