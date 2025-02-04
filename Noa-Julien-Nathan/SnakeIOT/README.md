# Jeu Snake pour Raspberry Pi Pico

Une implémentation classique du jeu Snake pour Raspberry Pi Pico utilisant un écran OLED et des boutons de contrôle.

---

## Matériel Requis

### Composants
- Raspberry Pi Pico
- Écran OLED SSD1306 (128x64 pixels)
- 5 Boutons Poussoirs :
  - Bouton Start
  - Boutons Directionnels (Haut, Bas, Gauche, Droite)

### Connexions
- Écran OLED :
  - SDA -> GPIO 0
  - SCL -> GPIO 1
- Boutons :
  - Start -> GPIO 15
  - Haut -> GPIO 14
  - Bas -> GPIO 16
  - Gauche -> GPIO 12
  - Droite -> GPIO 11

## Dépendances Logicielles

### Bibliothèques MicroPython
- `machine` : Bibliothèque principale pour le contrôle du matériel
  - `Pin` : Pour le contrôle des GPIO
  - `I2C` : Pour la communication avec l'OLED
- `ssd1306` : Pilote pour l'écran OLED
- `time` : Pour le contrôle du timing du jeu
- `random` : Pour la génération aléatoire de la position de la nourriture

## Fonctionnalités du Jeu

- Affichage sur écran OLED 128x64 pixels
- Suivi et affichage du score
- États du jeu :
  - Écran d'accueil
  - Partie en cours
  - Écran de fin de partie
- Déplacement du serpent dans quatre directions
- Mécanisme de collecte de nourriture
- Détection des collisions :
  - Avec les bords de l'écran
  - Avec le corps du serpent

## Contrôles

- Bouton START : Démarrer une nouvelle partie/recommencer après game over
- Boutons directionnels :
  - HAUT : Déplacer le serpent vers le haut
  - BAS : Déplacer le serpent vers le bas
  - GAUCHE : Déplacer le serpent vers la gauche
  - DROITE : Déplacer le serpent vers la droite

## Mécaniques de Jeu

- Le serpent commence avec une longueur d'un bloc
- À chaque nourriture collectée :
  - Le score augmente d'un point
  - La longueur du serpent augmente
  - Une nouvelle nourriture apparaît à un emplacement aléatoire
- La partie se termine quand le serpent :
  - Touche les bords de l'écran
  - Entre en collision avec lui-même

## Détails Techniques

- Résolution de l'écran : 128x64 pixels
- Taille des blocs : 4x4 pixels
- Taux de rafraîchissement : 0,1 secondes
- Communication I2C pour l'affichage
- Résistances de pull-up activées pour tous les boutons

## Instructions d'Installation

1. Flasher MicroPython sur votre Raspberry Pi Pico
2. Téléverser le code du jeu et les bibliothèques requises
3. Connecter l'écran OLED et les boutons selon la configuration des broches
4. Mettre l'appareil sous tension
5. Appuyer sur le bouton START pour commencer à jouer

---

Authors 

- 17Sx = Obringer Noa

- Noootzzz = Boisleux Nathan

- JulienMnt = Menet Julien
