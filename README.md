# 📶 Raspberry Pi Wi-Fi Manager

Une interface web légère et moderne propulsée par Flask pour scanner et configurer les connexions Wi-Fi sur **Raspberry Pi OS** via NetworkManager (`nmcli`).

Particulièrement utile en mode "headless" (sans écran) : connectez votre Raspberry Pi au partage de connexion de votre smartphone (iPhone / Android), accédez à l'interface web depuis votre navigateur mobile, et basculez facilement le Pi sur votre réseau Wi-Fi cible.

---

## ✨ Fonctionnalités

- **Scan automatique des réseaux Wi-Fi** environnants via `nmcli` (détection des SSID, puissance du signal et sécurité).
- **Interface web responsive et épurée**, pensée pour les écrans mobiles et iOS.
- **Sélection rapide** en un clic sur le réseau désiré.
- **Connexion asynchrone** : l'ordre de connexion est envoyé en tâche de fond pour permettre à la page de confirmation de se charger avant que la liaison réseau ne bascule.
- **Filtrage propre** : exclusion automatique des réseaux masqués et dédoublonnage des bornes multiples.

---

## 📁 Structure du projet

```text
rpi-wifi-manager/
├── .gitignore
├── LICENSE
├── README.md
├── app.py          # Serveur Flask et logique nmcli
└── index.html      # Interface web utilisateur
```

> **Note sur Flask :** Par défaut, Flask cherche les templates dans un sous-dossier `templates/`. Si vous conservez `index.html` à la racine, vous pouvez soit initialiser Flask avec `Flask(__name__, template_folder=".")`, soit déplacer `index.html` dans un dossier `templates/`.

---

## 🛠️ Prérequis

- Un **Raspberry Pi** avec **Raspberry Pi OS** (Bookworm ou version utilisant `NetworkManager` / `nmcli`).
- **Python 3.7+**
- **Droits sudo** : `nmcli` nécessite les privilèges administrateur pour déclencher le rescan et associer de nouvelles connexions.

---

## 🚀 Installation & Démarrage

### 1. Cloner ou copier le projet

```bash
git clone https://github.com/votre-utilisateur/rpi-wifi-manager.git
cd rpi-wifi-manager
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

Le projet ne dépend que de Flask :

```bash
pip install flask
```

### 4. Lancer l'application

```bash
sudo $(which python3) app.py
```
*(ou lancez `python3 app.py` si votre utilisateur dispose des droits sudo sans mot de passe pour `nmcli`)*

---

## 📱 Utilisation

1. Activez le **partage de connexion** sur votre smartphone (ex: iPhone).
2. Allumez votre Raspberry Pi déjà configuré pour se connecter temporairement à votre partage.
3. Repérez l'adresse IP du Pi (affichée dans les réglages de votre partage ou via `hostname -I`).
4. Ouvrez Safari ou Chrome sur votre smartphone et rendez-vous sur :
   ```text
   http://<IP_DU_RPI>:5000
   ```
   *(ou `http://raspberrypi.local:5000` si mDNS est actif)*
5. Sélectionnez votre réseau Wi-Fi habituel, entrez la clé de sécurité et validez avec **Connecter**.
6. Le Raspberry Pi se connecte automatiquement au nouveau réseau Wi-Fi.

---

## 🛡️ Configuration des droits sudo (optionnel)

Pour exécuter `app.py` sans `sudo` tout en autorisant le scan et la connexion Wi-Fi, vous pouvez ajouter une règle dans `sudoers` pour l'utilisateur `pi` :

```bash
sudo visudo /etc/sudoers.d/wifi-manager
```

Ajoutez la ligne suivante :
```text
pi ALL=(ALL) NOPASSWD: /usr/bin/nmcli
```

---

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).
