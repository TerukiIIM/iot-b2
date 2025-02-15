# Jeu Pong

## Description

Ce projet est une implémentation du jeu de Pong sur une Raspberry Pi Pico avec un écran OLED. Le but du jeu est de renvoyer la balle avec la palette en contrôlant sa position à l'aide d'un seul bouton. Lorsque le bouton est pressé, la palette se déplace vers le haut, et lorsqu'il est relâché, la palette descend. Le jeu oppose un joueur contre une IA qui contrôle la palette de l'autre côté de l'écran.

## Fonctionnalités

- Contrôle de la palette du joueur avec un seul bouton : appuyez pour déplacer la palette vers le haut et relâchez pour la déplacer vers le bas.
- La palette de l'ordinateur est contrôlée automatiquement par une IA pour suivre la balle.
- Affichage de la balle et des palettes sur un écran OLED.
- Un système de score affiche les scores du joueur et de l'ordinateur.
- Réinitialisation du jeu après chaque point marqué avec une brève pause pour afficher les scores.

## Matériel Requis

- Raspberry Pi Pico
- Écran OLED 128x64 (compatible I2C)
- 1 bouton-poussoir
- Câbles de connexion

## Installation

1. **Installer MicroPython** sur la Raspberry Pi Pico (si ce n'est pas déjà fait).
2. Utiliser **Thonny** ou un autre éditeur compatible MicroPython pour programmer la Raspberry Pi Pico.
3. **Copier le fichier** du jeu (par exemple `pong.py`) sur la Pico.
4. **Exécuter le script**.

## Utilisation

1. L'écran OLED affichera le terrain de jeu avec les palettes du joueur et de l'ordinateur, ainsi que la balle.
2. **Appuyez sur le bouton** pour déplacer la palette du joueur vers le haut.
3. **Relâchez le bouton** pour déplacer la palette du joueur vers le bas.
4. La palette de l'ordinateur suivra automatiquement la balle.
5. Le jeu affiche les scores après chaque point et réinitialise la balle au centre du terrain.

## Auteurs

- **Raphaël Parone**
- **Alain Sliman**
