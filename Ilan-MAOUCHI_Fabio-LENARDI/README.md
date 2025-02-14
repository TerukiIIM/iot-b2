# Circuit multi-usage
## Composants

- Raspberry Pi Pico WH
- Joystick Analogique
- Horloge DS1307
- Anneau 12 LED WS2812-12
- Écran OLED SSD1306
- 1 bouton rouge et 1 bouton bleu

## Prérequis

- MicroPython installé sur la Raspberry
- Thonny IDE installé sur un ordinateur
- Composants branchés en suivant le diagramme (fichier diagram.png ou sur https://wokwi.com/projects/422808122181404673)

## Installation

- Télécharger tous les fichiers .py dans le dossier "scripts"
- Téléverser tous les fichiers .py sur la Raspberry en utilisant Thonny

## ATTENTION
Pour utiliser les composants dans la bonne direction, il faut les orienter par rapport à vous comme dans le diagramme:
- Anneau et écran avec les pins vers le haut
- Joystick avec les pins vers la gauche

## Fonctionnement
### Vidéo
https://drive.google.com/file/d/1Nm3mVY1rS_XQ6u_dP0aBToT_o6e_HWou/view?usp=sharing

### Jeux

- Lancer mainmenu.py depuis Thonny
- Choisir un jeu avec le joystick haut/bas en confirmer avec le bouton rouge:
    - Simon Game: reproduire les sequences de directions ou boutons indiquées par l'anneau de LED
    - Snake Game: diriger le serpent avec le joystick pour manger les pixels sur l'écran OLED
    - Light Show: illumination de l'anneau LED
- Une partie de Simon Game peut être arrêtée en appuyant sur les deux boutons en même temps

### Horloge

- Lancer clock.py depuis Thonny
- La date et l'heure s'affiche sur l'écran OLED
- Appuyer sur le bouton rouge pour changer les valeurs avec le joystick:
    - Haut/bas pour augmenter/réduire la valeur sélectionnée
    - Gauche/droite pour sélectionner une valeur à modifier (Heure, Minutes, Secondes, Jour, Jour de la Semaine, Mois, Année)
    - Appuyer sur le bouton rouge pour confirmer les changements

## Équipe

- Ilan Maouchi
- Fabio Lenardi