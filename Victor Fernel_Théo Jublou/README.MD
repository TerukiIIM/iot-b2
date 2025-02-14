# Projet Détection Sonore avec LED

Ce projet utilise un capteur sonore pour détecter les bruits et allumer une LED en réponse à ces sons. Le projet peut être activé ou désactivé via une commande envoyée depuis le moniteur série de l'IDE Arduino. La LED s'éteint automatiquement après un délai si le niveau sonore tombe en dessous du seuil prédéfini.

## Description

Ce projet repose sur l'utilisation d'un capteur sonore GT4611 (numérique et/ou analogique) pour détecter des bruits. Lorsqu'un bruit dépasse un seuil défini, la LED s'allume. Le projet peut être activé ou désactivé en appuyant sur la touche 't' dans le moniteur série de l'IDE Arduino. Il est également possible d'ajuster dynamiquement le seuil de détection en envoyant la commande `S<valeur>`.

## Fonctionnalités

- **Détection de bruit** : Le capteur sonore détecte les bruits et déclenche l'allumage de la LED.
- **Activation/Désactivation du projet** : Appuyez sur 't' dans le moniteur série pour activer ou désactiver le projet.
- **Affichage des niveaux sonores** : Le niveau sonore est affiché dans le moniteur série pour permettre un réglage précis du seuil.
- **Modification dynamique du seuil** : Envoyez `S<valeur>` (ex: `S500`) dans le moniteur série pour ajuster le seuil de détection.

## Matériel Nécessaire

- **Carte Arduino** (Uno, Nano ou autre modèle compatible)
- **Capteur Sonore GT4611** (capteur de niveau sonore numérique et analogique)
- **LED** (intégrée ou externe avec une résistance appropriée)
- **Câbles de connexion**
- **Ordinateur avec l'IDE Arduino installé**

## Installation

### 1. Prérequis

Assurez-vous d'avoir l'IDE Arduino installé sur votre ordinateur. Si ce n'est pas déjà fait, téléchargez-le ici : [Télécharger l'IDE Arduino](https://www.arduino.cc/en/software).

### 2. Connexion du matériel

- **LED** : Si vous utilisez une LED externe, connectez la patte longue (anode) à la broche **13** de l'Arduino et la patte courte (cathode) à la masse (GND) via une résistance de 220Ω.
- **Capteur Sonore (Numérique et/ou Analogique)** : 
  - Connectez la broche numérique du capteur sonore à la broche **7** de l'Arduino.
  - Si vous utilisez la lecture analogique, connectez la broche analogique du capteur sonore à la broche **A0** de l'Arduino.

### 3. Télécharger et Charger le Code

1. Clonez ce dépôt ou téléchargez les fichiers dans un dossier local.
2. Ouvrez l'IDE Arduino, puis chargez le fichier `.ino` dans l'IDE.
3. Sélectionnez votre carte Arduino (par exemple, **Arduino Uno**) dans **Outils > Carte**.
4. Sélectionnez le port de votre carte dans **Outils > Port**.
5. Cliquez sur le bouton **Téléverser** pour envoyer le code à votre carte Arduino.

### 4. Utilisation

1. Ouvrez le **moniteur série** de l'IDE Arduino.
2. Une fois le projet chargé, appuyez sur **'t'** pour activer ou désactiver le projet.
3. La LED s'allume lorsque le capteur détecte un bruit dont le niveau dépasse le seuil défini.
4. Pour modifier le seuil de détection, envoyez `S<valeur>` (ex: `S500`).

## Code

Voici le code source complet pour ce projet :

```cpp
int Led = 13;            // LED intégrée à la carte
int capteurSon = 7;      // Broche numérique du capteur GT4611
int capteurSonA = A0;    // Broche analogique du capteur GT4611 (optionnel)
int seuil = 800;         // Seuil pour la détection en mode analogique (0-1023)
unsigned long tempsDebut = 0; // Pour éviter les clignotements rapides
const int delai = 500;   // Temps minimum avant d'éteindre la LED (ms)
bool projetActif = false; // Variable pour savoir si le projet est actif
int niveauSonPrecedent = 0; // Stocke le dernier niveau sonore affiché

void setup() {
    pinMode(Led, OUTPUT);        
    pinMode(capteurSon, INPUT);  
    Serial.begin(9600); // Initialisation du moniteur série
    Serial.println("Appuyez sur 't' pour activer/désactiver le projet.");
    Serial.println("Envoyez 'S' suivi d'un nombre pour modifier le seuil (ex: S500).");
}

void loop() {
    // Gestion des commandes du moniteur série
    if (Serial.available() > 0) {
        String commande = Serial.readStringUntil('\n');
        commande.trim();
        
        if (commande.equalsIgnoreCase("t")) {
            projetActif = !projetActif;
            Serial.println(projetActif ? "Projet activé !" : "Projet désactivé !");
            digitalWrite(Led, projetActif ? HIGH : LOW);
        } 
        else if (commande.startsWith("S")) {
            int nouveauSeuil = commande.substring(1).toInt();
            if (nouveauSeuil > 0 && nouveauSeuil <= 1023) {
                seuil = nouveauSeuil;
                Serial.print("Seuil modifié à : ");
                Serial.println(seuil);
            } else {
                Serial.println("Valeur invalide. Le seuil doit être entre 0 et 1023.");
            }
        }
    }

    if (projetActif) {
        int val = digitalRead(capteurSon);
        int niveauSon = analogRead(capteurSonA);

        if (abs(niveauSon - niveauSonPrecedent) > 10) {
            Serial.print("Niveau sonore analogique : ");
            Serial.println(niveauSon);
            niveauSonPrecedent = niveauSon;
        }

        if (val == HIGH || niveauSon > seuil) {
            digitalWrite(Led, HIGH);
            tempsDebut = millis();
            Serial.println("Bruit détecté ! LED allumée.");
        }

        if (niveauSon < seuil && millis() - tempsDebut > delai) {
            digitalWrite(Led, LOW);
            Serial.println("LED éteinte.");
        }
    } else {
        digitalWrite(Led, LOW);
    }
}

// Voici le code alternatif pour ce projet permettant d'éteindre la LED lorsque le bruit dépasse le seuil :
// if (niveauSon > seuil) {
//     digitalWrite(Led, LOW);
//     Serial.println("Bruit détecté ! LED éteinte.");
// } else {
//     digitalWrite(Led, HIGH);
//     Serial.println("Silence détecté ! LED allumée.");
// }
