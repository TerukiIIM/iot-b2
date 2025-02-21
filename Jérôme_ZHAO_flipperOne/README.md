# Flipper One

Ce projet utilise un écran OLED et des boutons pour naviguer dans un menu et enregistrer/émettre des signaux infrarouges (IR).

---
## 👤 Auteurs
- **Jérôme Zhao**
---

## 📦 Matériel Nécessaire
- **Carte Arduino** (par exemple, Arduino Uno)
- **Écran OLED** (par exemple, Adafruit SSD1306)
- **Récepteur IR** (par exemple, TSOP4838)
- **Émetteur IR**
- **Boutons poussoirs** (4)
- **Câbles de connexion**

---

## 🔌 Connexions Matérielles

### Écran OLED :
- `VCC` → 3.3V ou 5V  
- `GND` → GND  
- `SDA` → A4 (ou broche SDA sur certaines cartes)  
- `SCL` → A5 (ou broche SCL sur certaines cartes)  

### Récepteur IR :
- `VCC` → 3.3V ou 5V  
- `GND` → GND  
- `OUT` → Broche 2  

### Émetteur IR :
- **Anode** → Broche numérique (exemple : 3)  
- **Cathode** → GND via une résistance de 220Ω  

### Boutons :
- **Bouton 1 (Retour)** → Broche 32  
- **Bouton 2 (Haut)** → Broche 25  
- **Bouton 3 (Bas)** → Broche 26  
- **Bouton 4 (Valider)** → Broche 27  

---

## ⚙️ Installation
1. **Clonez ce dépôt** ou téléchargez les fichiers dans un dossier local.
2. **Ouvrez l'IDE Arduino** et chargez le fichier `flipper_one.ino`.
3. **Installez les bibliothèques nécessaires** via le gestionnaire de bibliothèques de l'IDE Arduino :
    - `IRremote`
    - `Adafruit GFX Library`
    - `Adafruit SSD1306`
4. **Sélectionnez votre carte Arduino** et le port correspondant dans :
    - `Outils > Carte`
    - `Outils > Port`
5. **Téléversez le code** sur votre carte Arduino.

---

## 🎮 Utilisation
1. **Allumez votre Arduino.**
2. **Utilisez les boutons** pour naviguer dans le menu :
    - **Bouton 1 (Retour)** : Retourne au menu précédent.
    - **Bouton 2 (Haut)** : Déplace le curseur vers le haut.
    - **Bouton 3 (Bas)** : Déplace le curseur vers le bas.
    - **Bouton 4 (Valider)** : Sélectionne l'option actuelle.

### 📋 Menu Principal :
- **Enregistrer** : Enregistre un signal IR.
- **Émettre** : Passe au sous-menu pour émettre des signaux IR ou afficher la liste des signaux enregistrés.

---

## 🚀 Fonctionnalités
### Enregistrer un signal IR :
1. Sélectionnez l'option **"Enregistrer"** dans le menu principal.
2. Attendez qu'un signal IR soit reçu. Le signal sera enregistré et affiché à l'écran.
3. Appuyez sur le bouton **"Retour"** pour revenir au menu principal.

### Émettre un signal IR :
1. Sélectionnez l'option **"Émettre"** dans le menu principal.
2. Choisissez **"Envoyer signal"** pour émettre un signal IR enregistré.
3. Choisissez **"Liste des signaux"** pour afficher la liste des signaux enregistrés.

---

## 📜 Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
