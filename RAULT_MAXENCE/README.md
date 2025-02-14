# Projet Minuteur avec Raspberry Pi Pico W

## Description
Ce projet est un minuteur programmable utilisant un **Raspberry Pi Pico W**, un **écran LCD 1602 I2C**, des **boutons poussoirs** pour contrôler le temps et choisir une mélodie, ainsi qu'un **buzzer passif** pour émettre une alarme.

## Composants utilisés
- **Raspberry Pi Pico W**
- **Écran LCD 1602 I2C** (SDA sur GP14, SCL sur GP27)
- **Buzzer passif** (connecté sur GP16)
- **4 Boutons poussoirs** :
  - Start/Pause (GP2)
  - Ajouter 30s (GP3)
  - Retirer 30s (GP4)
  - Changer mélodie (GP6)
- **Alimentation 5V**
- **Connexions via fils Dupont**

## Fichier principal
- **main.py** : Script à exécuter sur le Raspberry Pi Pico W.

## Instructions d'utilisation
1. **Démarrer le Pico** avec `main.py`.
2. **Utiliser les boutons** :
   - `Start/Pause` : Démarre ou met en pause le minuteur.
   - `Ajouter 30s` : Ajoute 30 secondes au minuteur.
   - `Retirer 30s` : Retire 30 secondes.
   - `Changer mélodie` : Sélectionne une mélodie différente pour l'alarme.
3. **Le minuteur affiche le temps restant** sur l'écran LCD.
4. **À la fin du temps**, le buzzer émet une alarme.

## Connexions
| Composant       | GPIO |
|----------------|------|
| Bouton Start/Pause | GP2  |
| Bouton Ajouter 30s | GP3  |
| Bouton Retirer 30s | GP4  |
| Bouton Mélodie    | GP5  |
| LCD SDA         | GP14 |
| LCD SCL         | GP27 |
| Buzzer          | GP16 |

## Remarque
- Le buzzer est un modèle **passif**, il doit recevoir un signal PWM pour fonctionner.

## Auteur
Projet réalisé par **Rault Maxence**.

