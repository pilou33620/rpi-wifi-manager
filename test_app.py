import unittest
from unittest.mock import patch, MagicMock
from app import app, scan_wifi_networks

class TestWifiManager(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_scan_parsing_and_sorting(self):
        mock_output = (
            "Livebox-45:40:WPA2\n"
            "Livebox-45:85:WPA2\n"
            "iPhone d'Alex:70:WPA2 WPA3\n"
            r"Freebox\:Salon:60:WPA2" + "\n"
            "--:90:WPA2\n"
            "Public_WiFi:50:\n"
        )
        with patch("subprocess.run", return_value=MagicMock(stdout=mock_output)):
            nets = scan_wifi_networks()
            self.assertEqual(len(nets), 4)
            # Tri par signal décroissant et meilleur signal retenu pour Livebox-45
            self.assertEqual(nets[0]["ssid"], "Livebox-45")
            self.assertEqual(nets[0]["signal"], 85)
            self.assertEqual(nets[1]["ssid"], "iPhone d'Alex")
            self.assertEqual(nets[1]["signal"], 70)
            self.assertEqual(nets[2]["ssid"], "Freebox:Salon")
            self.assertEqual(nets[2]["signal"], 60)
            self.assertEqual(nets[3]["ssid"], "Public_WiFi")
            self.assertEqual(nets[3]["signal"], 50)
            self.assertFalse(nets[3]["is_secured"])

    def test_get_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_post_connect(self):
        with patch("subprocess.Popen") as mock_popen:
            resp = self.client.post("/connect", data={"ssid": "iPhone d'Alex", "password": "mypassword"})
            self.assertEqual(resp.status_code, 200)
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            self.assertEqual(args, ["sudo", "nmcli", "dev", "wifi", "connect", "iPhone d'Alex", "password", "mypassword"])

    def test_post_connect_open_network(self):
        with patch("subprocess.Popen") as mock_popen:
            resp = self.client.post("/connect", data={"ssid": "Public_WiFi", "password": ""})
            self.assertEqual(resp.status_code, 200)
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            self.assertEqual(args, ["sudo", "nmcli", "dev", "wifi", "connect", "Public_WiFi"])

if __name__ == "__main__":
    unittest.main()
