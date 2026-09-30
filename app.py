"""
Version 1.1.0
Description: Serveur web Flask pour scanner et configurer les connexions Wi-Fi
             sur Raspberry Pi OS via NetworkManager (nmcli).
Fonctions modifiées:
- scan_wifi_networks() : parsing robuste nmcli -t, dédoublonnage avec meilleur signal, tri par signal
- connect_to_wifi() : exécution asynchrone sécurisée avec journalisation
- index() : affichage avec gestion des templates
- connect() : validation et redirection
"""

import logging
from pathlib import Path
import re
import subprocess
from flask import Flask, redirect, render_template, request, url_for

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Résolution robuste du dossier de templates
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR if TEMPLATES_DIR.exists() else BASE_DIR),
)


def scan_wifi_networks():
    """Scanne les réseaux Wi-Fi environnants et extrait SSID, signal et sécurité."""
    try:
        # Demande un ré-échantillonnage (ignore les erreurs si indisponible ou non-root)
        try:
            subprocess.run(
                ["sudo", "nmcli", "dev", "wifi", "rescan"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=8,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Récupération de la liste en mode terse (-t)
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi", "list"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        networks_by_ssid = {}
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            # Découpage robuste : nmcli -t sépare par ':' mais échappe les ':' internes avec '\:'
            parts = [p.replace(r"\:", ":").strip() for p in re.split(r"(?<!\\):", line)]
            if len(parts) >= 2:
                ssid = parts[0]
                signal_raw = parts[1]
                security = parts[2] if len(parts) > 2 else ""

                # Filtrer les réseaux masqués ou invalides
                if not ssid or ssid == "--":
                    continue

                signal_int = int(signal_raw) if signal_raw.isdigit() else 0

                # Dédoublonnage : conserver le point d'accès avec le meilleur signal
                if ssid not in networks_by_ssid or signal_int > networks_by_ssid[ssid]["signal"]:
                    is_secured = bool(security and security.strip() and security.strip() != "--")
                    networks_by_ssid[ssid] = {
                        "ssid": ssid,
                        "signal": signal_int,
                        "security": security if is_secured else "Ouvert",
                        "is_secured": is_secured,
                    }

        # Tri des réseaux par puissance de signal décroissante
        return sorted(networks_by_ssid.values(), key=lambda n: n["signal"], reverse=True)

    except Exception as exc:
        logger.warning("Impossible de scanner les réseaux Wi-Fi via nmcli : %s", exc)
        return []


def connect_to_wifi(ssid, password):
    """Enregistre le profil Wi-Fi et tente la connexion en tâche de fond."""
    cmd = ["sudo", "nmcli", "dev", "wifi", "connect", ssid]
    if password:
        cmd.extend(["password", password])

    logger.info("Tentative de connexion au SSID '%s'...", ssid)
    # Exécution asynchrone pour permettre à la page web de répondre
    # avant que l'interface Wi-Fi ne coupe la liaison avec le point d'accès/iPhone
    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        logger.error("Erreur lors de l'exécution de nmcli connect : %s", exc)


@app.route("/")
def index():
    networks = scan_wifi_networks()
    return render_template("index.html", networks=networks)


@app.route("/connect", methods=["POST"])
def connect():
    ssid = request.form.get("ssid", "").strip()
    password = request.form.get("password", "")
    if ssid:
        connect_to_wifi(ssid, password)
        return render_template("index.html", connecting=True, target_ssid=ssid)
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Écoute sur toutes les interfaces, port 5000
    app.run(host="0.0.0.0", port=5000)