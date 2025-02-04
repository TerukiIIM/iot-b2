# Capteur de CO2

## Modules

- Arduino Nano 33 BLE (copie Aliexpress)
- SCD30 (CO2; température; humidité)
- PN532 (RFID/NFC)
- SSD1306 (OLED)
- Bouton
- LEDs

## Fonctionnement

L'écran OLED affiche le taux de CO2 en ppm par défaut, et le "feu tricolore" (les 3 LEDs en gros) affichent une couleur en fonction du taux de CO2.

Pour changer le mode, il faut scanner une tag NFC dont l'UID est inclus dans la liste des UID autorisés (main.cpp:53).

Le bouton est alors "activé" pendant 5 secondes et l'utilisateur peut changer le mode d'affichage en appuyant dessus.

## Équipe

- Moi tout seul ([Eric HUBERT](https://github.com/ImLyenx))
