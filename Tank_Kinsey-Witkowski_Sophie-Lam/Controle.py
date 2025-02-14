from machine import Pin
import time
from motor import move_forward, move_backward, stop, turn_left, turn_right
from ultrasonic_ranging import SR
from mpu6050_sensor import mpu

# Initialiser le MPU6050
mpu.MPU_Init()

# Définition du relais pour la pompe
relay = Pin(22, Pin.OUT)  
relay.value(0)  # éteindre la pompe au démarrage

# Fonctions de contrôle de la pompe
def pump_on():
    relay.value(1)  
    print("Pompe activée")

def pump_off():
    relay.value(0)  
    print("Pompe désactivée")

# Fonction pour récupérer les données des capteurs
def get_sensor_data():
    try:
        distance = SR.distanceCM()
    except Exception as e:
        distance = f"Erreur : {e}"

    try:
        accel = mpu.MPU_Get_Accelerometer()
        gyro = mpu.MPU_Get_Gyroscope()
    except Exception as e:
        accel = f"Erreur : {e}"
        gyro = f"Erreur : {e}"

    return distance, accel, gyro

# Boucle principale de contrôle
def control_loop():
    print("======================")
    print("Contrôlez le robot en utilisant les touches suivantes :")
    print(" - z : Avancer")
    print(" - s : Reculer")
    print(" - q : Tourner à gauche")
    print(" - d : Tourner à droite")
    print(" - Espace : Arrêter")
    print(" - i : Afficher les données des capteurs")
    print(" - p : Activer la pompe")
    print(" - o : Désactiver la pompe")
    print(" - x : Quitter")
    print("======================")

    while True:
        command = input("Entrez une commande : ").strip().lower()

        if command == "z":
            move_forward()
            print("Avance...")

        elif command == "s":
            move_backward()
            print("Recule...")

        elif command == "q":
            turn_left()
            print("Tourne à gauche...")

        elif command == "d":
            turn_right()
            print("Tourne à droite...")

        elif command == "" or command == " ":
            stop()
            print("Moteurs arrêtés.")

        elif command == "i":
            # Afficher les données des capteurs
            distance, accel, gyro = get_sensor_data()
            print("\n==== Données des capteurs ====")
            print(f"Distance : {distance} cm")
            print(f"Accéléromètre : ax={accel[0]}, ay={accel[1]}, az={accel[2]}")
            print(f"Gyroscope : gx={gyro[0]}, gy={gyro[1]}, gz={gyro[2]}")
            print("======================")

        elif command == "p":
            pump_on()

        elif command == "o":
            pump_off()

        elif command == "x":
            print("Arrêt du script...")
            stop()
            pump_off()  # arrêter avant de quitter
            break

        else:
            print(f" Commande invalide : '{command}'. Veuillez réessayer.")

        time.sleep(0.2)  # Délai

if __name__ == "__main__":
    control_loop()
