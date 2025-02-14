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
