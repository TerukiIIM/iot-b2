# Simulateur de Combat Pokémon

Ce projet est un simulateur de combat Pokémon interactif utilisant une Raspberry Pi Pico W. Les joueurs sélectionnent leur Pokémon en scannant des badges RFID, puis interagissent avec le jeu via un écran OLED et des boutons.

## Matériel Nécessaire

- **Raspberry Pi Pico W**
- **Câbles de connexion**
- **2 lecteurs RFID**
- **Écran OLED 32x128**
- **3 boutons poussoirs**

## Librairies Requises

Assurez-vous d'importer les librairies suivantes dans votre environnement MicroPython :

- `machine`
- `time`
- `ssd1306` (pour l'écran OLED)
- `MFRC522` (pour les lecteurs RFID)

## Installation des Librairies

1. **MicroPython** : Téléchargez et installez MicroPython sur votre Raspberry Pi Pico W en suivant les instructions officielles.
2. **ssd1306.py** : Téléchargez la librairie pour l'écran OLED depuis le [dépôt officiel](https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py) et transférez-la sur votre Pico.
3. **MFRC522.py** : Obtenez la librairie pour les lecteurs RFID depuis ce [dépôt](https://github.com/micropython/micropython/blob/master/drivers/nfc/mfrc522.py) et transférez-la également sur votre Pico.

## Connexions Matérielles

- **Lecteurs RFID** : Connectez-les aux broches SPI de la Pico (SCK, MOSI, MISO, RST, SDA).
- **Écran OLED** : Connectez-le aux broches I2C de la Pico (SCL, SDA).
- **Boutons** : Reliez chaque bouton à une broche GPIO distincte et à la masse (GND).

## Utilisation

1. **Démarrage** : Allumez la Raspberry Pi Pico W.
2. **Sélection du Pokémon** : Scannez un badge RFID avec l'un des lecteurs pour choisir votre Pokémon.
3. **Combat** : Utilisez l'écran OLED pour suivre le combat et les boutons pour effectuer des actions (attaquer, défendre, etc.).

## Remarques

- Assurez-vous que toutes les connexions sont correctes et sécurisées avant de démarrer le système.
- Pour ajouter de nouveaux Pokémon ou fonctionnalités, modifiez le code en conséquence.
