from mpu6050 import MPU6050
import time

G = 9.8
mpu = MPU6050(1, 15, 14)  # bus(1), SCL(GP15), SDA(GP14)
mpu.MPU_Init()  # Initialiser le MPU6050
time.sleep(1)  # Attente pour que le MPU6050 soit stable

if __name__ == "__main__":
    try:
        while True:
            accel = mpu.MPU_Get_Accelerometer()  # Obtenir les valeurs d'accélération
            gyro = mpu.MPU_Get_Gyroscope()  # Obtenir les valeurs du gyroscope
            print("Données brutes : ")
            print("a/g : \tax: %d, ay: %d, az: %d\n\tgx: %d, gy: %d, gz: %d"
                  % (accel[0], accel[1], accel[2], gyro[0], gyro[1], gyro[2]))
            print("Données calculées : ")
            print("a/g : \tax: %0.4f, ay: %0.4f, az: %0.4f\n\tgx: %0.4f, gy: %0.4f, gz: %0.4f\n"
                  % (accel[0] / 16384, accel[1] / 16384, accel[2] / 16384, gyro[0] / 131, gyro[1] / 131, gyro[2] / 131))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêté par l'utilisateur.")
