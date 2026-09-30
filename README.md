# Raspberry Pi Wi-Fi Manager

Interface web légère en Python (Flask) pour scanner et connecter un Raspberry Pi à un réseau Wi-Fi environnant via `nmcli` (NetworkManager).

## Prérequis

- Raspberry Pi OS (Debian Bookworm recommandé, utilisant NetworkManager).
- Python 3.9+ et `pip`.

## Installation

1. Cloner ou copier le projet sur le Raspberry Pi :
   ```bash
   cd ~/rpi-wifi-manager
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Démarrage manuel

```bash
python3 app.py
```
Accédez ensuite à l'interface depuis un navigateur sur le même réseau ou en point d'accès :
`http://<adresse_ip_du_pi>:5000`

## Démarrage automatique au boot (systemd)

Créez le fichier de service `/etc/systemd/system/rpi-wifi-manager.service` :

```ini
[Unit]
Description=Raspberry Pi WiFi Manager Web App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rpi-wifi-manager
ExecStart=/usr/bin/python3 /home/pi/rpi-wifi-manager/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Activez et démarrez le service :
```bash
sudo systemctl daemon-reload
sudo systemctl enable rpi-wifi-manager.service
sudo systemctl start rpi-wifi-manager.service
```
