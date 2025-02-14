#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DFRobot_DS1307.h>  // Ajouter la bibliothèque DS1307

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Initialiser le DS1307 RTC
DFRobot_DS1307 DS1307;

void setup() {
  Serial.begin(115200);

  // Initialiser l'écran OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Bloquer si l'initialisation échoue
  }

  // Initialiser le RTC DS1307
  while (!(DS1307.begin())) {
    Serial.println("Communication with DS1307 failed");
    delay(3000);
  }
  Serial.println("DS1307 initialized!");

  // Configurer le pin SQW en mode 1Hz
  DS1307.setSqwPinMode(DS1307.eSquareWave_1Hz);
}

void loop() {
  uint16_t getTimeBuff[7] = {0};
  DS1307.getTime(getTimeBuff);
  
  char timeString[6];
  sprintf(timeString, "%02d:%02d", 
          getTimeBuff[2],  // Heure
          getTimeBuff[1]),  // Minute
  
  // Afficher l'heure sur l'écran OLED
  display.clearDisplay();
  display.setTextSize(3);              // Taille du texte
  display.setTextColor(SSD1306_WHITE); // Couleur du texte
  display.setCursor(24, 24);           // Position du texte
  display.println(timeString);        // Afficher l'heure récupérée
  display.display();

  delay(1000);  // Attendre 1 seconde avant de rafraîchir l'heure
}
