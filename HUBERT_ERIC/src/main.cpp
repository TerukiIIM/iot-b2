#include <Wire.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_PN532.h>
#include "SparkFun_SCD30_Arduino_Library.h"

// SSD1360
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire);

// PN532
Adafruit_PN532 nfc(13, 12, 11, 10);

// SCD30
SCD30 scd30;

// LEDs
#define GREEN_LED 2
#define YELLOW_LED 3
#define RED_LED 4
#define STATE_LED 7

// Bouton
#define BUTTON_PIN 5
bool buttonState;
bool lastButtonState = LOW;
unsigned long lastDebounceTime = 0;
#define DEBOUNCE_DELAY 50

// Modes d'affichage
enum DisplayMode
{
  CO2,
  TEMP,
  HUMIDITY
};

DisplayMode currentMode = CO2;

unsigned long lastUpdate = 0;
int co2;
float temp;
float hum;
bool isButtonAvailable = false;
unsigned long lastCardReadSuccess = 0;

unsigned long lastNfcCheck = 0;
#define NFC_CHECK_INTERVAL 100

// Whitelist des UIDs
uint8_t authorizedTags[1][4] = {
    {0x00, 0x00, 0x00, 0x00},
};

void setup()
{
  Serial.begin(115200);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C))
  {
    Serial.println("Erreur: SSD1306");
    while (1)
      ;
  }
  display.clearDisplay();

  nfc.begin();
  if (!nfc.getFirmwareVersion())
  {
    Serial.println("Erreur: PN532");
    while (1)
      ;
  }
  nfc.SAMConfig();

  if (!scd30.begin())
  {
    Serial.println("Erreur: SCD30");
    while (1)
      ;
  }

  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("READY !!");
  display.display();

  pinMode(GREEN_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLDOWN);
  pinMode(STATE_LED, OUTPUT);
}

void displayHeader(const String header)
{
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.cp437(false);
  display.setTextWrap(false);
  display.println(header);
}

void displayValue(const String value)
{
  display.setTextColor(SSD1306_WHITE);
  display.cp437(false);
  display.setTextWrap(false);
  if (value.length() <= 3)
  {
    display.setCursor(42 - (value.length() - 1) * 15, 22);
    display.setTextSize(6);
  }
  else if (value.length() == 4)
  {
    display.setCursor(4, 24);
    display.setTextSize(5);
  }
  else
  {
    display.setCursor(4, 26);
    display.setTextSize(4);
  }
  display.println(value);
  display.display();
}

void handleButton()
{
  bool reading = digitalRead(BUTTON_PIN);

  if (reading != lastButtonState)
  {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY)
  {
    if (reading != buttonState)
    {
      buttonState = reading;
      if (buttonState == HIGH && isButtonAvailable)
      {
        currentMode = static_cast<DisplayMode>((currentMode + 1) % 3);
        Serial.println("Mode suivant");
      }
    }
  }
  lastButtonState = reading;
}

void updateSensors()
{
  if (scd30.dataAvailable())
  {
    co2 = scd30.getCO2();
    temp = scd30.getTemperature();
    hum = scd30.getHumidity();
  }
}

void updateDisplay()
{
  display.clearDisplay();
  display.setCursor(0, 0);

  switch (currentMode)
  {
  case CO2:
    displayHeader("CO2 (ppm)");
    displayValue(String(co2));
    break;
  case TEMP:
    displayHeader("Temp (C)");
    displayValue(String(temp));
    break;
  case HUMIDITY:
    displayHeader("Humidite(%)");
    displayValue(String(hum));
    break;
  }
  display.display();
}

void handleNfcDetected(uint8_t *uid, uint8_t uidLength)
{
  Serial.println("Tag NFC détecté");
  Serial.print("UID: ");

  for (uint8_t i = 0; i < uidLength; i++)
  {
    Serial.print(uid[i], HEX);
    Serial.print(" ");
  }

  if (uidLength == 4)
  {
    for (uint8_t i = 0; i < sizeof(authorizedTags) / sizeof(authorizedTags[0]); i++)
    {
      if (memcmp(uid, authorizedTags[i], 4) == 0)
      {
        Serial.println("\nAutorisé");
        lastCardReadSuccess = millis();
        isButtonAvailable = true;
        return;
      }
    }
  }
  Serial.println("\nNon autorisé");
}

void checkNfc()
{
  uint8_t uid[] = {0, 0, 0, 0, 0, 0, 0};
  uint8_t uidLength;

  // Lecture NFC passive pendant 100ms
  bool success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 100);

  if (success)
  {
    handleNfcDetected(uid, uidLength);
  }
}

void updateLEDs()
{
  digitalWrite(GREEN_LED, (co2 < 800));
  digitalWrite(YELLOW_LED, (co2 >= 800 && co2 < 1200));
  digitalWrite(RED_LED, (co2 >= 1200));
  digitalWrite(STATE_LED, isButtonAvailable ? HIGH : LOW);
}

void loop()
{
  unsigned long currentMillis = millis();

  // Temps de désactivation du bouton
  if (currentMillis - lastCardReadSuccess > 5000)
  {
    isButtonAvailable = false;
  }

  handleButton();

  // Mise à jour des capteurs toutes les 2 secondes
  if (currentMillis - lastUpdate > 2000)

  {
    updateSensors();
    updateDisplay();
    lastUpdate = currentMillis;
  }

  // Check NFC toutes les 100ms
  if (currentMillis - lastNfcCheck > NFC_CHECK_INTERVAL)
  {
    checkNfc();
    lastNfcCheck = currentMillis;
  }

  updateLEDs();
}
