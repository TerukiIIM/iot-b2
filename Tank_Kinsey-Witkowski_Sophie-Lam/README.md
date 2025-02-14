### **Projet : Robot Contrôlé par Raspberry Pi Pico** 

> Par Kinsey Witkowski & Sophie Lam

#### 📌 **Description**
Ce projet est un robot piloté par une **Raspberry Pi Pico** capable de se déplacer en avant, en arrière, de tourner à gauche et à droite, de s'arrêter et de tirer avec une pompe à eau. Il utilise également un **capteur ultrasonique** pour mesurer la distance des obstacles et un **MPU6050** pour obtenir les données d’accélération et de gyroscope.

---

#### 🛠️ **Matériel Nécessaire**
- **Raspberry Pi Pico**
- **Module L298N** (Contrôleur de moteur)
- **Deux moteurs DC**
- **Capteur Ultrasonique HC-SR04**
- **MPU6050** (Accéléromètre & Gyroscope)
- **Batterie 9V**  
- **Breadboard et câbles**

💧 Pour la pompe à eau:
- **Batterie 12V**
- **Relay HW-482**
- **Brushless DC water pump**

---

#### ⚡ **Branchement des Composants**

![Montage du projet](montage_tank.png?v=2)


---

#### ⏩ **Installation du Code**
1. **Transférez les fichiers Python sur la Raspberry Pi Pico** (via Thonny).
2. **Vérifiez les connexions** selon le schéma de montage.
3. **Lancez le script de contrôle** (`Controle.py`) pour piloter le robot.

---

#### 🎮 **Contrôle du Robot**
- **Z** → Avancer
- **S** → Reculer
- **Q** → Tourner à gauche
- **D** → Tourner à droite
- **Espace** → Arrêter
- **I** → Afficher les données des capteurs
- **X** → Quitter le script
- **P** → Activer la pompe
- **O** → Désactiver la pompe  

*(il faut appuyer sur la touche entrée ⏎ après chaque commande)*
