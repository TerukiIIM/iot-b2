#include <HCSR04.h>
#include <Buzzer.h>

Buzzer buzzer(13, 32);

const int trigPin = 14;        
const int echoPin = 25;         
const int ledPin = 26;         

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(115200);

  digitalWrite(trigPin, LOW);
  delay(100);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duree = pulseIn(echoPin, HIGH, 30000); 
  if (duree == 0) {
    Serial.println("Pas de retour d'écho, distance maximale supposée !");
    duree = 23529;
  }

  int distance = duree * 0.034 / 2;

  Serial.print("Distance calculée : ");
  Serial.println(distance);  

  if (distance > 0 && distance < 100) {
    Serial.println("⚠️ Présence détectée !");
    digitalWrite(ledPin, HIGH);
    Serial.println("son envoyé wsh");
    buzzer.begin(200);

    buzzer.sound(NOTE_E7, 1000);
    delay(100);
    buzzer.sound(NOTE_E7, 1000);
    delay(100);

    buzzer.end(200);
  } else {
    digitalWrite(ledPin, LOW);
    Serial.println("son pas envoyé");
  }


  delay(500);  
}
