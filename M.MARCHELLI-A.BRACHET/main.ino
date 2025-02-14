#include <Adafruit_NeoPixel.h>
#include <Arduino.h>

#define PIN 4  // GPIO4 connecté au Din de la matrice
#define WIDTH 16  // Nombre de pixels en largeur
#define HEIGHT 16 // Nombre de pixels en hauteur
#define NUMPIXELS (WIDTH * HEIGHT) // Nombre total de LEDs

#define VRX_PIN 34  // Joystick axe X
#define VRY_PIN 35  // Joystick axe Y
#define SWITCH_PIN 32 // Bouton du joystick

Adafruit_NeoPixel strip(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
int posX = WIDTH / 2;
int posY = HEIGHT / 2;
int dirX = 1;
int dirY = 0;
int snakeLength = 3;
int snakeX[256] = {WIDTH / 2, WIDTH / 2 - 1, WIDTH / 2 - 2};
int snakeY[256] = {HEIGHT / 2, HEIGHT / 2, HEIGHT / 2};
int appleX, appleY;

void setup() {
    strip.begin();
    strip.setBrightness(20); // Baisse de la luminosité
    strip.show();
    pinMode(VRX_PIN, INPUT);
    pinMode(VRY_PIN, INPUT);
    pinMode(SWITCH_PIN, INPUT_PULLUP);
    randomSeed(analogRead(0));
    spawnApple();
    countdown();
}

int getPixelIndex(int x, int y) {
    return (y % 2 == 0) ? (y * WIDTH) + x : (y * WIDTH) + (WIDTH - 1 - x);
}

void countdown() {
    const char* messages[] = {"3", "2", "1", "GO"};
    for (int i = 0; i < 4; i++) {
        strip.clear();
        for (int j = 0; j < strlen(messages[i]); j++) {
            strip.setPixelColor(getPixelIndex(WIDTH / 2 - 1 + j, HEIGHT / 2), strip.Color(255, 255, 255));
        }
        strip.show();
        delay(1000);
    }
}

void spawnApple() {
    appleX = random(WIDTH);
    appleY = random(HEIGHT);
}

void loop() {
    int xValue = analogRead(VRX_PIN);
    int yValue = analogRead(VRY_PIN);
    
    if (xValue < 1000 && dirX == 0) { dirX = -1; dirY = 0; }
    if (xValue > 3000 && dirX == 0) { dirX = 1; dirY = 0; }
    if (yValue < 1000 && dirY == 0) { dirX = 0; dirY = 1; }
    if (yValue > 3000 && dirY == 0) { dirX = 0; dirY = -1; }

    posX += dirX;
    posY += dirY;

    if (posX < 0 || posX >= WIDTH || posY < 0 || posY >= HEIGHT) {
        countdown();
        posX = WIDTH / 2;
        posY = HEIGHT / 2;
        snakeLength = 3;
        spawnApple();
    }

    for (int i = snakeLength - 1; i > 0; i--) {
        snakeX[i] = snakeX[i - 1];
        snakeY[i] = snakeY[i - 1];
    }
    snakeX[0] = posX;
    snakeY[0] = posY;

    if (posX == appleX && posY == appleY) {
        snakeLength++;
        spawnApple();
    }

    strip.clear();
    strip.setPixelColor(getPixelIndex(appleX, appleY), strip.Color(255, 0, 0)); // Pomme en rouge
    for (int i = 0; i < snakeLength; i++) {
        strip.setPixelColor(getPixelIndex(snakeX[i], snakeY[i]), strip.Color(0, 255, 0)); // Serpent en vert
    }
    strip.show();

    delay(200);
}