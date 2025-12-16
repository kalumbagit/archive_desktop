# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## Installation rapide (5 minutes)

### Étape 1 : Prérequis

```bash
# Vérifier Python (version 3.8+)
python --version
```

### Étape 2 : Créer l'environnement

```bash
# Créer un dossier pour le projet
mkdir archive_manager
cd archive_manager

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Étape 3 : Installer les dépendances

```bash
pip install -r requirements.txt
```

**Note pour Linux** : Installer aussi python-magic système

```bash
# Ubuntu/Debian
sudo apt-get install python3-magic

# Fedora
sudo dnf install python-magic
```

### Étape 4 : Configurer la base de données

```bash
python setup_database.py
```

Suivez les instructions pour créer un utilisateur admin.

### Étape 5 : Lancer l'application

```bash
python main.py
```

---

## 📁 Structure des fichiers à créer

Créez cette structure de dossiers et fichiers :

```
archive_manager/
│
├── main.py
├── setup_database.py
├── run_tests.py
├── requirements.txt
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── database.py
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py
│   └── migrations.py
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── folder.py
│   ├── file.py
│   └── audit_log.py
│
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py
│   ├── folder_controller.py
│   ├── file_controller.py
│   ├── search_controller.py
│   └── audit_controller.py
│
├── views/
│   ├── __init__.py
│   ├── login_window.py
│   ├── register_window.py
│   ├── main_window.py
│   ├── search_window.py
│   ├── import_window.py
│   ├── settings_window.py
│   ├── preview_window.py
│   ├── folder_dialog.py
│   └── folder_selection_dialog.py
│
├── utils/
│   ├── __init__.py
│   ├── file_handler.py
│   ├── scanner.py
│   ├── preview_generator.py
│   ├── validators.py
│   └── theme_manager.py
│
├── resources/
│   └── styles/
│       ├── light_theme.qss
│       └── dark_theme.qss
│
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_controllers.py
    └── test_utils.py
```

---

## ✅ Checklist de création des fichiers

Copiez le contenu de chaque artefact dans les fichiers correspondants :

### Configuration et base de données

- [ ] `config/__init__.py`
- [ ] `config/settings.py`
- [ ] `config/database.py`
- [ ] `database/__init__.py`
- [ ] `database/db_manager.py`
- [ ] `database/migrations.py`

### Modèles

- [ ] `models/__init__.py`
- [ ] `models/user.py`
- [ ] `models/folder.py`
- [ ] `models/file.py`
- [ ] `models/audit_log.py`

### Contrôleurs

- [ ] `controllers/__init__.py`
- [ ] `controllers/auth_controller.py`
- [ ] `controllers/folder_controller.py`
- [ ] `controllers/file_controller.py`
- [ ] `controllers/search_controller.py`
- [ ] `controllers/audit_controller.py`

### Vues (Interface)

- [ ] `views/__init__.py`
- [ ] `views/login_window.py`
- [ ] `views/register_window.py`
- [ ] `views/main_window.py`
- [ ] `views/search_window.py`
- [ ] `views/import_window.py`
- [ ] `views/settings_window.py`
- [ ] `views/preview_window.py`
- [ ] `views/folder_dialog.py`
- [ ] `views/folder_selection_dialog.py`

### Utilitaires

- [ ] `utils/__init__.py`
- [ ] `utils/file_handler.py`
- [ ] `utils/scanner.py`
- [ ] `utils/preview_generator.py`
- [ ] `utils/validators.py`
- [ ] `utils/theme_manager.py`

### Thèmes (créer les fichiers même s'ils sont vides)

- [ ] `resources/styles/light_theme.qss`
- [ ] `resources/styles/dark_theme.qss`

### Tests

- [ ] `tests/__init__.py`
- [ ] `tests/test_models.py`
- [ ] `tests/test_controllers.py`
- [ ] `tests/test_utils.py`

### Scripts principaux

- [ ] `main.py`
- [ ] `setup_database.py`
- [ ] `run_tests.py`
- [ ] `requirements.txt`

---

## 🧪 Tester l'installation

```bash
# Exécuter les tests unitaires
python run_tests.py

# Si tout fonctionne, vous devriez voir :
# ✓ Tests passed
```

---

## 🎯 Premier lancement

1. **Démarrer l'application**

   ```bash
   python main.py
   ```

2. **Créer un compte**

   - Cliquez sur "Créer un compte"
   - Remplissez le formulaire
   - Cliquez sur "S'inscrire"

3. **Se connecter**

   - Entrez vos identifiants
   - Cliquez sur "Se connecter"

4. **Créer votre premier dossier**

   - Cliquez sur "Nouveau Dossier"
   - Remplissez les informations
   - Cliquez sur "Enregistrer"

5. **Importer des fichiers**
   - Sélectionnez votre dossier
   - Menu Fichier → Importer des fichiers
   - Sélectionnez vos fichiers
   - Ils seront copiés dans l'archive

---

## ⚙️ Configuration avancée

### Changer le type de base de données

Dans les paramètres de l'application :

1. Cliquez sur "Paramètres"
2. Onglet "Base de données"
3. Sélectionnez le type (SQLite, PostgreSQL, MySQL)
4. Configurez la connexion
5. Redémarrez l'application

### Changer le lieu de stockage

1. Paramètres → Stockage
2. Cliquez sur "Parcourir"
3. Sélectionnez le nouveau dossier
4. Enregistrez

---

## 🔧 Dépannage courant

### Erreur "Module not found"

```bash
pip install -r requirements.txt --force-reinstall
```

### Erreur python-magic sur Windows

```bash
pip install python-magic-bin
```

### Base de données corrompue

```bash
rm ~/.archive_manager/archives.db
python setup_database.py
```

### L'interface ne s'affiche pas correctement

Vérifiez que PySide6 est bien installé :

```bash
pip install PySide6 --upgrade
```

---

## 📊 Utilisation

### Organiser vos archives

**Par projet/année** :

```
📁 Projets 2024
├── 📁 Projet A
│   ├── 📄 contrat.pdf
│   └── 📄 factures.xlsx
└── 📁 Projet B
```

**Par thème** :

```
📁 Finances
├── 📁 2023
└── 📁 2024
    ├── 📄 budget.xlsx
    └── 📄 rapport.pdf
```

**Par secteur** :

```
📁 Commercial
📁 Technique
📁 RH
```

### Recherche efficace

**Recherche simple** : Utilisez la barre de recherche en haut

**Recherche avancée** :

1. Cliquez sur "Rechercher"
2. Remplissez les critères (année, thème, secteur)
3. Cliquez sur "Rechercher"
4. Double-cliquez sur un résultat pour l'ouvrir

---

## 📈 Bonnes pratiques

1. **Nommez vos dossiers clairement**

   - ✅ "Contrats Clients 2024"
   - ❌ "Dossier1"

2. **Utilisez les métadonnées**

   - Remplissez l'année, le thème, le secteur
   - Ajoutez une description

3. **Organisez hiérarchiquement**

   - Créez des sous-dossiers
   - Gardez une structure logique

4. **Sauvegardez régulièrement**

   - Exportez la base de données
   - Sauvegardez le dossier de stockage

5. **Utilisez l'audit**
   - Consultez régulièrement les logs
   - Vérifiez qui fait quoi

---

## 🆘 Support

Pour toute question ou problème :

1. Consultez le README.md complet
2. Vérifiez les logs dans `~/.archive_manager/`
3. Exécutez les tests : `python run_tests.py`

---

## 📝 Licence et Auteurs

[À compléter avec vos informations]
