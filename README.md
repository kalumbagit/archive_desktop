# Gestionnaire d'Archives Numériques

Application desktop de gestion d'archives numériques développée avec Python et PySide6.

## 📋 Fonctionnalités

### ✅ Gestion des utilisateurs

- Création de comptes utilisateurs
- Authentification sécurisée
- Gestion des sessions

### 📁 Gestion des dossiers

- Création de dossiers hiérarchiques (dossiers et sous-dossiers)
- Organisation par nom, année, thème, secteur
- Tri multi-critères
- Navigation arborescente

### 📄 Gestion des fichiers

- Import de fichiers individuels ou en masse
- Scanner de dossiers avec option récursive
- Prévisualisation des fichiers
- Téléchargement/export de fichiers
- Support de tous types de fichiers

### 🔍 Recherche avancée

- Recherche par mots-clés
- Filtrage par année, thème, secteur
- Résultats avec prévisualisation
- Double-clic pour ouvrir

### 📊 Traçabilité

- Audit complet de toutes les actions
- Horodatage des opérations
- Historique par utilisateur et par entité
- Suivi des créations, modifications, suppressions, téléchargements

### ⚙️ Paramètres configurables

- Choix du type de base de données (SQLite, PostgreSQL, MySQL)
- Configuration du lieu de sauvegarde
- Gestion des droits d'accès
- Choix du thème (clair/sombre)
- Configuration de la langue

## 🛠️ Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

```bash
git clone <url-du-repo>
cd archive_manager
```

2. **Créer un environnement virtuel (recommandé)**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Installer les dépendances additionnelles pour Linux**

```bash
# Ubuntu/Debian
sudo apt-get install python3-magic

# Fedora
sudo dnf install python-magic
```

## 🚀 Lancement de l'application

```bash
python main.py
```

## 📖 Guide d'utilisation

### Premier lancement

1. **Créer un compte**

   - Cliquez sur "Créer un compte"
   - Remplissez le formulaire d'inscription
   - Cliquez sur "S'inscrire"

2. **Se connecter**
   - Entrez votre nom d'utilisateur et mot de passe
   - Cliquez sur "Se connecter"

### Créer une structure d'archives

1. **Créer un dossier racine**

   - Cliquez sur "Nouveau Dossier" dans la barre d'outils
   - Remplissez les informations (nom, année, thème, secteur)
   - Validez

2. **Créer des sous-dossiers**
   - Sélectionnez un dossier parent
   - Créez un nouveau dossier
   - Il sera automatiquement placé sous le dossier parent

### Importer des fichiers

**Méthode 1 : Import simple**

- Sélectionnez un dossier
- Menu Fichier → Importer des fichiers
- Sélectionnez vos fichiers
- Ils seront copiés dans l'archive

**Méthode 2 : Import avancé avec scanner**

- Cliquez sur "Importer" dans la barre d'outils
- Choisissez "Sélectionner un dossier"
- Activez "Scanner les sous-dossiers" si nécessaire
- Sélectionnez le dossier de destination dans l'archive
- Cliquez sur "Importer"

### Rechercher des documents

1. **Recherche rapide**

   - Utilisez la barre de recherche en haut
   - Appuyez sur Entrée

2. **Recherche avancée**
   - Cliquez sur "Rechercher" dans la barre d'outils
   - Remplissez les critères de recherche
   - Cliquez sur "Rechercher"
   - Double-cliquez sur un résultat pour l'ouvrir

### Trier les dossiers

Utilisez le menu déroulant "Trier par" pour organiser vos dossiers par :

- Nom
- Date de création
- Année
- Thème
- Secteur

### Prévisualiser un fichier

- Double-cliquez sur un fichier dans la liste
- La prévisualisation s'ouvrira (selon le type de fichier)

### Configurer l'application

1. **Accéder aux paramètres**

   - Cliquez sur "Paramètres" dans la barre d'outils

2. **Onglets disponibles**
   - **Général** : Langue de l'interface
   - **Stockage** : Emplacement de sauvegarde des fichiers
   - **Base de données** : Type et configuration de la BDD
   - **Droits d'accès** : Permissions de suppression
   - **Apparence** : Thème clair/sombre

## 🗄️ Base de données

### SQLite (par défaut)

- Fichier : `~/.archive_manager/archives.db`
- Aucune configuration requise
- Idéal pour un usage personnel

### PostgreSQL

1. Installer PostgreSQL
2. Créer une base de données
3. Dans Paramètres → Base de données :
   - Type : PostgreSQL
   - Host : localhost
   - Port : 5432
   - Database : archive_manager
   - User : votre_utilisateur
   - Password : votre_mot_de_passe

### MySQL

1. Installer MySQL
2. Créer une base de données
3. Configurer dans les paramètres

## 📂 Structure des fichiers

```
~/.archive_manager/
├── archives.db          # Base de données SQLite (par défaut)
├── config.json          # Configuration de l'application
└── ...

~/Archives/             # Stockage des fichiers (configurable)
├── 1/                  # Dossier avec ID 1
│   ├── document1.pdf
│   └── image.jpg
├── 2/                  # Dossier avec ID 2
└── ...
```

## 🔒 Sécurité

- Les mots de passe sont hashés avec Werkzeug (PBKDF2)
- Toutes les actions sont tracées dans l'audit log
- Les fichiers sont stockés localement (pas de cloud)
- Contrôle d'accès par utilisateur

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifier l'installation de Python
python --version

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Erreur de base de données

```bash
# Supprimer la base de données et recommencer
rm ~/.archive_manager/archives.db
python main.py
```

### Problème de permissions

```bash
# Vérifier les droits d'accès
chmod -R 755 ~/.archive_manager
```

## 📝 Logs et audit

Toutes les actions sont enregistrées :

- Connexions/déconnexions
- Créations de dossiers et fichiers
- Modifications
- Suppressions
- Téléchargements
- Consultations

Pour consulter les logs, accédez à la table `audit_logs` dans la base de données.

## 🔄 Mise à jour

```bash
# Sauvegarder votre base de données
cp ~/.archive_manager/archives.db ~/.archive_manager/archives.db.backup

# Mettre à jour le code
git pull

# Réinstaller les dépendances
pip install -r requirements.txt --upgrade
```

## 🤝 Support

Pour toute question ou problème :

1. Consultez la documentation
2. Vérifiez les logs d'erreur
3. Contactez le support technique

## 📄 Licence

[Votre licence ici]

## 👥 Auteurs

ALIMA AMBASSA Steve Bodouin Ingenieur logiciel tous droits reservés

## informations consernant les options de build

Pour builder l’application, j’ai créé et configuré un fichier .spec qui décrit comment PyInstaller doit empaqueter le projet.
J’ai également écrit un script build.py qui automatise le processus de build en fonction de la plateforme (Windows, macOS, Linux).

Les commandes possibles sont :

# ====> python build.py --spec --clean

--spec : utilise le fichier archive_manager.spec pour construire l’exécutable.

--clean : nettoie les anciens fichiers de build (dist/, build/) avant de lancer la compilation.
👉 Résultat : un exécutable complet, configuré selon les options du .spec (icônes, hidden imports, ressources, etc.).

# ===> python build.py --simple --onefile --windowed

--simple : lance un build direct avec PyInstaller, sans passer par le fichier .spec.

--onefile : génère un seul exécutable autonome (au lieu d’un dossier avec plusieurs fichiers).

--windowed : crée une application graphique sans console (utile pour les applications PySide6).
👉 Résultat : un exécutable minimal, pratique pour tester rapidement.

# ===> python build.py --clean

Supprime les dossiers dist/ et build/ ainsi que les fichiers .spec temporaires.
👉 Résultat : environnement de build propre, prêt pour une nouvelle compilation.

# RESUME

# --spec : utilise le fichier archive_manager.spec pour construire l’exécutable.

# --simple : lance un build direct avec PyInstaller, sans passer par le fichier .spec.

# --onefile : génère un seul exécutable autonome (au lieu d’un dossier avec plusieurs fichiers).

# --windowed : crée une application graphique sans console (utile pour les applications PySide6).

# --clean : nettoie les anciens fichiers de build (dist/, build/) avant de lancer la compilation.
