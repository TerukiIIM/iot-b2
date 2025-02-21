#include <IRremote.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const int buttonPin1 = 32; // Retour
const int buttonPin2 = 25; // Haut
const int buttonPin3 = 26; // Bas
const int buttonPin4 = 27; // Valider

const int recv_pin = 2;  // Broche D2 pour le récepteur IR
IRrecv irrecv(recv_pin);
decode_results results;

bool button1Pressed = false;
bool button2Pressed = false;
bool button3Pressed = false;
bool button4Pressed = false;

bool button1Lock = false;
bool button2Lock = false;
bool button3Lock = false;
bool button4Lock = false;

unsigned long lastDebounceTime1 = 0;
unsigned long lastDebounceTime2 = 0;
unsigned long lastDebounceTime3 = 0;
unsigned long lastDebounceTime4 = 0;
const unsigned long debounceDelay = 200; // 200 ms pour éviter le double-clic

// Structures pour menus
struct Menu {
  const char* title;
  const char** options;
  int size;
  Menu* parent;
};

const char* mainMenuOptions[] = {"Enregistrer", "Emettre"};
Menu mainMenu = {"Main Menu", mainMenuOptions, 2, nullptr};

// Sous-menu pour "Émettre" sans la sous-option "Retour"
const char* emitMenuOptions[] = {"Envoyer signal", "Liste des signaux"};
Menu emitMenu = {"Emettre", emitMenuOptions, 2, &mainMenu};

Menu* currentMenu = &mainMenu;
int menuIndex = 0;

// Liste pour stocker les signaux IR enregistrés
unsigned long irSignals[10];  // Capacité de stocker jusqu'à 10 signaux IR
int signalCount = 0;

void setup() {
  Serial.begin(9600);
  irrecv.enableIRIn();  // Démarre la réception IR
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP);
  pinMode(buttonPin3, INPUT_PULLUP);
  pinMode(buttonPin4, INPUT_PULLUP);
  displayMenu();
}

void loop() {
  // Détection des boutons et gestion des actions
  if (digitalRead(buttonPin1) == LOW && !button1Lock) {
    button1Pressed = true;
    button1Lock = true;
    lastDebounceTime1 = millis();
  }
  if (millis() - lastDebounceTime1 > debounceDelay) {
    button1Lock = false;
  }

  if (digitalRead(buttonPin2) == LOW && !button2Lock) {
    button2Pressed = true;
    button2Lock = true;
    lastDebounceTime2 = millis();
  }
  if (millis() - lastDebounceTime2 > debounceDelay) {
    button2Lock = false;
  }

  if (digitalRead(buttonPin3) == LOW && !button3Lock) {
    button3Pressed = true;
    button3Lock = true;
    lastDebounceTime3 = millis();
  }
  if (millis() - lastDebounceTime3 > debounceDelay) {
    button3Lock = false;
  }

  if (digitalRead(buttonPin4) == LOW && !button4Lock) {
    button4Pressed = true;
    button4Lock = true;
    lastDebounceTime4 = millis();
  }
  if (millis() - lastDebounceTime4 > debounceDelay) {
    button4Lock = false;
  }

  // Mise à jour des menus
  if (button1Pressed) {
    if (currentMenu->parent != nullptr) {
      currentMenu = currentMenu->parent;
      menuIndex = 0;
      displayMenu();
    }
    button1Pressed = false;
  }

  if (button2Pressed) {
    menuIndex = (menuIndex - 1 + currentMenu->size) % currentMenu->size;
    displayMenu();
    button2Pressed = false;
  }

  if (button3Pressed) {
    menuIndex = (menuIndex + 1) % currentMenu->size;
    displayMenu();
    button3Pressed = false;
  }

  if (button4Pressed) {
    if (currentMenu == &mainMenu) {
      if (menuIndex == 0) {
        currentMenu = nullptr;  // Passer à l'enregistrement
        recordSignal();
      } else if (menuIndex == 1) {
        currentMenu = &emitMenu;  // Passer au sous-menu "Émettre"
        menuIndex = 0;  // Assurez-vous que le curseur est sur la première option
        displayMenu();
      }
    } else if (currentMenu == &emitMenu) {
      if (menuIndex == 0) {
        sendSignal();
      } else if (menuIndex == 1) {
        listSignals();
      }
    }
    button4Pressed = false;
  }
}

void displayMenu() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(currentMenu->title);

  for (int i = 0; i < currentMenu->size; i++) {
    display.setCursor(10, (i + 1) * 10);
    if (i == menuIndex) {
      display.print(F("> "));
    } else {
      display.print(F("  "));
    }
    display.println(currentMenu->options[i]);
  }

  display.display();
}

// Fonction pour enregistrer un signal IR
void recordSignal() {
  static bool signalWaiting = true;  // Indicateur pour savoir si le texte a été affiché

  if (signalWaiting) {
    display.clearDisplay();
    signalWaiting = false;  // Le texte a été affiché, on ne le redessine plus
  }

  int dots = 0;
  while (!irrecv.decode(&results)) {
    dots++;
    if (dots > 3) dots = 0; // Reset des points

    display.setCursor(0, 0);
    display.print("En attente d'un signal");

    // Afficher les points d'animation
    for (int i = 0; i < dots; i++) {
      display.print(".");
    }
    display.display();

    // Vérifier si le bouton retour est pressé pour revenir en arrière
    if (digitalRead(buttonPin1) == LOW) {
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("Retour au menu principal...");
      display.display();
      delay(2000);
      currentMenu = &mainMenu;  // Retour au menu principal
      displayMenu();
      return;
    }
    
    delay(500);  // Attendre un peu avant d'afficher les points suivants
  }

  // Quand un signal est reçu, l'enregistrer
  irSignals[signalCount++] = results.value;
  irrecv.resume();  // Préparer à recevoir un autre signal
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Signal enregistre");
  display.display();
  delay(2000);
  currentMenu = &mainMenu;  // Retour au menu principal
  displayMenu();
}

// Fonction pour émettre un signal IR
void sendSignal() {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Sélectionnez un signal");

  for (int i = 0; i < signalCount; i++) {
    display.setCursor(0, 10 + i * 10);
    display.print(i + 1);
    display.print(". Signal IR ");
    display.println(i + 1);
  }
  display.display();

  // Attente de la sélection du signal
  int selectedSignal = -1;
  while (selectedSignal == -1) {
    if (digitalRead(buttonPin2) == LOW) {  // Haut
      selectedSignal = (selectedSignal - 1 + signalCount) % signalCount;
      delay(200);
    } else if (digitalRead(buttonPin3) == LOW) {  // Bas
      selectedSignal = (selectedSignal + 1) % signalCount;
      delay(200);
    }

    // Attente d'une sélection avec le bouton Valider
    if (digitalRead(buttonPin4) == LOW) {  // Valider
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("Emission en cours...");
      display.display();
      delay(2000);  // Affichage du message
      // Emission du signal
      IRsend irsend;
      irsend.sendNEC(irSignals[selectedSignal], 32);  // Par exemple, en utilisant le protocole NEC
      delay(3000);  // Attente de 3 secondes avant de revenir au menu
      currentMenu = &emitMenu; // Retour au sous-menu "Emettre"
      displayMenu();
    }
  }
}

// Fonction pour afficher la liste des signaux enregistrés
void listSignals() {
  display.clearDisplay();
  display.setCursor(0, 0);
  
  if (signalCount == 0) {
    // Aucun signal enregistré
    display.println("Aucun signal");
    display.display();
    delay(2000);  // Affiche "Aucun signal" pendant 2 secondes
    currentMenu = &emitMenu;  // Retour au sous-menu "Emettre"
    displayMenu();
    return;  // Quitte la fonction sans afficher la liste des signaux
  }

  // Afficher la liste des signaux
  display.println("Liste des signaux:");

  for (int i = 0; i < signalCount; i++) {
    display.setCursor(0, 10 + i * 10);
    display.print(i + 1);
    display.print(". Signal IR ");
    display.println(i + 1);
  }
  display.display();

  bool waitingForReturn = true;
  
  // Attente du bouton "Retour" pour revenir au sous-menu "Émettre"
  while (waitingForReturn) {
    if (digitalRead(buttonPin1) == LOW) {  // Retour
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("Retour au sous-menu...");
      display.display();
      delay(2000);  // Afficher pendant 2 secondes pour informer l'utilisateur
      currentMenu = &emitMenu;  // Retour au sous-menu "Emettre"
      displayMenu();
      waitingForReturn = false;
    }

    delay(100);  // Attente pour éviter un balayage trop rapide
  }
}

// #include <IRremote.h>
// #include <Wire.h>
// #include <Adafruit_GFX.h>
// #include <Adafruit_SSD1306.h>

// #define SCREEN_WIDTH 128
// #define SCREEN_HEIGHT 64
// #define OLED_RESET -1
// #define SCREEN_ADDRESS 0x3C
// Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// const int buttonPin1 = 32; // Retour
// const int buttonPin2 = 25; // Haut
// const int buttonPin3 = 26; // Bas
// const int buttonPin4 = 27; // Valider

// const int recv_pin = 2;
// IRrecv irrecv(recv_pin);
// decode_results results;

// bool button1Pressed = false;
// bool button2Pressed = false;
// bool button3Pressed = false;
// bool button4Pressed = false;

// bool button1Lock = false;
// bool button2Lock = false;
// bool button3Lock = false;
// bool button4Lock = false;

// unsigned long lastDebounceTime1 = 0;
// unsigned long lastDebounceTime2 = 0;
// unsigned long lastDebounceTime3 = 0;
// unsigned long lastDebounceTime4 = 0;

// // 200 ms pour éviter le double-clic
// const unsigned long debounceDelay = 200;

// // Structures pour menus
// struct Menu {
//   const char* title;
//   const char** options;
//   int size;
//   Menu* parent;
// };

// const char* mainMenuOptions[] = {"Enregistrer", "Emettre"};
// Menu mainMenu = {"Main Menu", mainMenuOptions, 2, nullptr};

// // Sous-menu pour "Émettre"
// const char* emitMenuOptions[] = {"Envoyer signal", "Liste des signaux"};
// Menu emitMenu = {"Emettre", emitMenuOptions, 2, &mainMenu};

// Menu* currentMenu = &mainMenu;
// int menuIndex = 0;

// // Liste pour stocker les signaux IR enregistrés
// unsigned long irSignals[10];  // Capacité de stocker jusqu'à 10 signaux IR
// int signalCount = 0;

// void setup() {
//   Serial.begin(9600);
//   irrecv.enableIRIn();  // Démarre la réception IR
//   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
//     Serial.println(F("SSD1306 allocation failed"));
//     for(;;);
//   }
//   pinMode(buttonPin1, INPUT_PULLUP);
//   pinMode(buttonPin2, INPUT_PULLUP);
//   pinMode(buttonPin3, INPUT_PULLUP);
//   pinMode(buttonPin4, INPUT_PULLUP);
//   displayMenu();
// }

// void loop() {
//   // Détection des boutons et gestion des actions
//   if (digitalRead(buttonPin1) == LOW && !button1Lock) {
//     button1Pressed = true;
//     button1Lock = true;
//     lastDebounceTime1 = millis();
//   }
//   if (millis() - lastDebounceTime1 > debounceDelay) {
//     button1Lock = false;
//   }

//   if (digitalRead(buttonPin2) == LOW && !button2Lock) {
//     button2Pressed = true;
//     button2Lock = true;
//     lastDebounceTime2 = millis();
//   }
//   if (millis() - lastDebounceTime2 > debounceDelay) {
//     button2Lock = false;
//   }

//   if (digitalRead(buttonPin3) == LOW && !button3Lock) {
//     button3Pressed = true;
//     button3Lock = true;
//     lastDebounceTime3 = millis();
//   }
//   if (millis() - lastDebounceTime3 > debounceDelay) {
//     button3Lock = false;
//   }

//   if (digitalRead(buttonPin4) == LOW && !button4Lock) {
//     button4Pressed = true;
//     button4Lock = true;
//     lastDebounceTime4 = millis();
//   }
//   if (millis() - lastDebounceTime4 > debounceDelay) {
//     button4Lock = false;
//   }

//   // Mise à jour des menus
//   if (button1Pressed) {
//     if (currentMenu->parent != nullptr) {
//       currentMenu = currentMenu->parent;
//       menuIndex = 0;
//       displayMenu();
//     }
//     button1Pressed = false;
//   }

//   if (button2Pressed) {
//     menuIndex = (menuIndex - 1 + currentMenu->size) % currentMenu->size;
//     displayMenu();
//     button2Pressed = false;
//   }

//   if (button3Pressed) {
//     menuIndex = (menuIndex + 1) % currentMenu->size;
//     displayMenu();
//     button3Pressed = false;
//   }

//   if (button4Pressed) {
//     if (currentMenu == &mainMenu) {
//       if (menuIndex == 0) {
//         currentMenu = nullptr;  // Passer à l'enregistrement
//         recordSignal();
//       } else if (menuIndex == 1) {
//         currentMenu = &emitMenu;  // Passer au sous-menu "Émettre"
//         displayMenu();
//       }
//     } else if (currentMenu == &emitMenu) {
//       if (menuIndex == 0) {
//         sendSignal();
//       } else if (menuIndex == 1) {
//         listSignals();
//       } else if (menuIndex == 2) {
//         currentMenu = &mainMenu;  // Retour au menu principal
//         displayMenu();
//       }
//     }
//     button4Pressed = false;
//   }
// }

// void displayMenu() {
//   display.clearDisplay();
//   display.setTextSize(1);
//   display.setTextColor(SSD1306_WHITE);
//   display.setCursor(0, 0);
//   display.println(currentMenu->title);

//   for (int i = 0; i < currentMenu->size; i++) {
//     display.setCursor(10, (i + 1) * 10);
//     if (i == menuIndex) {
//       display.print(F("> "));
//     } else {
//       display.print(F("  "));
//     }
//     display.println(currentMenu->options[i]);
//   }

//   display.display();
// }

// // Fonction pour enregistrer un signal IR
// // Fonction pour enregistrer un signal IR
// void recordSignal() {
//   static bool signalWaiting = true;  // Indicateur pour savoir si le texte a été affiché

//   if (signalWaiting) {
//     display.clearDisplay();
//     signalWaiting = false;  // Le texte a été affiché, on ne le redessine plus
//   }

//   int dots = 0;
//   while (!irrecv.decode(&results)) {
//     dots++;
//     if (dots > 3) dots = 0; // Reset des points

//     display.setCursor(0, 0);
//     display.print("En attente d'un signal");

//     // Afficher les points d'animation
//     for (int i = 0; i < dots; i++) {
//       display.print(".");
//     }
//     display.display();

//     // Vérifier si le bouton retour est pressé pour revenir en arrière
//     if (digitalRead(buttonPin1) == LOW) {
//       display.clearDisplay();
//       display.setCursor(0, 0);
//       display.println("Retour au menu principal...");
//       display.display();
//       delay(2000);
//       currentMenu = &mainMenu;  // Retour au menu principal
//       displayMenu();
//       return;
//     }
    
//     delay(500);  // Attendre un peu avant d'afficher les points suivants
//   }

//   // Quand un signal est reçu, l'enregistrer
//   irSignals[signalCount++] = results.value;
//   irrecv.resume();  // Préparer à recevoir un autre signal
//   display.clearDisplay();
//   display.setCursor(0, 0);
//   display.println("Signal enregistre");
//   display.display();
//   delay(2000);
//   currentMenu = &mainMenu;  // Retour au menu principal
//   displayMenu();
// }

// // Fonction pour émettre un signal IR
// void sendSignal() {
//   display.clearDisplay();
//   display.setCursor(0, 0);
//   display.println("Sélectionnez un signal");

//   for (int i = 0; i < signalCount; i++) {
//     display.setCursor(0, 10 + i * 10);
//     display.print(i + 1);
//     display.print(". Signal IR ");
//     display.println(i + 1);
//   }
//   display.display();

//   // Attente de la sélection du signal
//   int selectedSignal = -1;
//   while (selectedSignal == -1) {
//     if (digitalRead(buttonPin2) == LOW) {  // Haut
//       selectedSignal = (selectedSignal - 1 + signalCount) % signalCount;
//       delay(200);
//     } else if (digitalRead(buttonPin3) == LOW) {  // Bas
//       selectedSignal = (selectedSignal + 1) % signalCount;
//       delay(200);
//     }

//     // Attente d'une sélection avec le bouton Valider
//     if (digitalRead(buttonPin4) == LOW) {  // Valider
//       display.clearDisplay();
//       display.setCursor(0, 0);
//       display.println("Emission en cours...");
//       display.display();
//       delay(2000);  // Affichage du message
//       // Emission du signal
//       IRsend irsend;
//       irsend.sendNEC(irSignals[selectedSignal], 32);  // Par exemple, en utilisant le protocole NEC
//       delay(3000);  // Attente de 3 secondes avant de revenir au menu
//       currentMenu = &emitMenu; // Retour au sous-menu "Emettre"
//       displayMenu();
//     }
//   }
// }

// // Fonction pour afficher la liste des signaux enregistrés
// void listSignals() {
//   display.clearDisplay();
//   display.setCursor(0, 0);
//   display.println("Liste des signaux:");

//   for (int i = 0; i < signalCount; i++) {
//     display.setCursor(0, 10 + i * 10);
//     display.print(i + 1);
//     display.print(". Signal IR ");
//     display.println(i + 1);
//   }
//   display.display();
//   delay(2000); // Affichage des signaux pendant 2 secondes avant de revenir au sous-menu "Emettre"
//   displayMenu();
// }

// // #include <IRremote.h>
// // #include <Wire.h>
// // #include <Adafruit_GFX.h>
// // #include <Adafruit_SSD1306.h>

// // #define SCREEN_WIDTH 128
// // #define SCREEN_HEIGHT 64
// // #define OLED_RESET -1
// // #define SCREEN_ADDRESS 0x3C
// // Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// // const int buttonPin1 = 32; // Retour
// // const int buttonPin2 = 25; // Haut
// // const int buttonPin3 = 26; // Bas
// // const int buttonPin4 = 27; // Valider

// // const int recv_pin = 2;  // Broche D2 pour le récepteur IR
// // IRrecv irrecv(recv_pin);
// // decode_results results;

// // bool button1Pressed = false;
// // bool button2Pressed = false;
// // bool button3Pressed = false;
// // bool button4Pressed = false;

// // bool button1Lock = false;
// // bool button2Lock = false;
// // bool button3Lock = false;
// // bool button4Lock = false;

// // unsigned long lastDebounceTime1 = 0;
// // unsigned long lastDebounceTime2 = 0;
// // unsigned long lastDebounceTime3 = 0;
// // unsigned long lastDebounceTime4 = 0;
// // const unsigned long debounceDelay = 200; // 200 ms pour éviter le double-clic

// // // Structures pour menus
// // struct Menu {
// //   const char* title;
// //   const char** options;
// //   int size;
// //   Menu* parent;
// // };

// // const char* mainMenuOptions[] = {"Enregistrer", "Emettre"};
// // Menu mainMenu = {"Main Menu", mainMenuOptions, 2, nullptr};

// // Menu* currentMenu = &mainMenu;
// // int menuIndex = 0;

// // // Liste pour stocker les signaux IR enregistrés
// // unsigned long irSignals[10];  // Capacité de stocker jusqu'à 10 signaux IR
// // int signalCount = 0;

// // void setup() {
// //   Serial.begin(9600);
// //   irrecv.enableIRIn();  // Démarre la réception IR
// //   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
// //     Serial.println(F("SSD1306 allocation failed"));
// //     for(;;);
// //   }
// //   pinMode(buttonPin1, INPUT_PULLUP);
// //   pinMode(buttonPin2, INPUT_PULLUP);
// //   pinMode(buttonPin3, INPUT_PULLUP);
// //   pinMode(buttonPin4, INPUT_PULLUP);
// //   displayMenu();
// // }

// // void loop() {
// //   // Détection des boutons et gestion des actions
// //   if (digitalRead(buttonPin1) == LOW && !button1Lock) {
// //     button1Pressed = true;
// //     button1Lock = true;
// //     lastDebounceTime1 = millis();
// //   }
// //   if (millis() - lastDebounceTime1 > debounceDelay) {
// //     button1Lock = false;
// //   }

// //   if (digitalRead(buttonPin2) == LOW && !button2Lock) {
// //     button2Pressed = true;
// //     button2Lock = true;
// //     lastDebounceTime2 = millis();
// //   }
// //   if (millis() - lastDebounceTime2 > debounceDelay) {
// //     button2Lock = false;
// //   }

// //   if (digitalRead(buttonPin3) == LOW && !button3Lock) {
// //     button3Pressed = true;
// //     button3Lock = true;
// //     lastDebounceTime3 = millis();
// //   }
// //   if (millis() - lastDebounceTime3 > debounceDelay) {
// //     button3Lock = false;
// //   }

// //   if (digitalRead(buttonPin4) == LOW && !button4Lock) {
// //     button4Pressed = true;
// //     button4Lock = true;
// //     lastDebounceTime4 = millis();
// //   }
// //   if (millis() - lastDebounceTime4 > debounceDelay) {
// //     button4Lock = false;
// //   }

// //   // Mise à jour des menus
// //   if (button1Pressed) {
// //     if (currentMenu->parent != nullptr) {
// //       currentMenu = currentMenu->parent;
// //       menuIndex = 0;
// //       displayMenu();
// //     }
// //     button1Pressed = false;
// //   }

// //   if (button2Pressed) {
// //     menuIndex = (menuIndex - 1 + currentMenu->size) % currentMenu->size;
// //     displayMenu();
// //     button2Pressed = false;
// //   }

// //   if (button3Pressed) {
// //     menuIndex = (menuIndex + 1) % currentMenu->size;
// //     displayMenu();
// //     button3Pressed = false;
// //   }

// //   if (button4Pressed) {
// //     if (currentMenu == &mainMenu) {
// //       if (menuIndex == 0) {
// //         currentMenu = nullptr;  // Passer à l'enregistrement
// //         recordSignal();
// //       } else if (menuIndex == 1) {
// //         emitSignal();
// //       }
// //     }
// //     button4Pressed = false;
// //   }
// // }

// // void displayMenu() {
// //   display.clearDisplay();
// //   display.setTextSize(1);
// //   display.setTextColor(SSD1306_WHITE);
// //   display.setCursor(0, 0);
// //   display.println(currentMenu->title);

// //   for (int i = 0; i < currentMenu->size; i++) {
// //     display.setCursor(10, (i + 1) * 10);
// //     if (i == menuIndex) {
// //       display.print(F("> "));
// //     } else {
// //       display.print(F("  "));
// //     }
// //     display.println(currentMenu->options[i]);
// //   }

// //   display.display();
// // }

// // // Fonction pour enregistrer un signal IR
// // void recordSignal() {
// //   display.clearDisplay();
// //   display.setCursor(0, 0);

// //   int dots = 0;
// //   while (!irrecv.decode(&results)) {
// //     dots++;
// //     if (dots > 3) dots = 0; // Reset des points
// //     display.setCursor(0, 20);
// //     display.print("En attente de signal");
// //     for (int i = 0; i < dots; i++) {
// //       display.print(".");
// //     }
// //     display.display();

// //     // Vérifier si le bouton retour est pressé pour revenir en arrière
// //     if (digitalRead(buttonPin1) == LOW) {
// //       display.clearDisplay();
// //       display.setCursor(0, 0);
// //       display.println("Retour au menu principal...");
// //       display.display();
// //       delay(2000);
// //       currentMenu = &mainMenu;  // Retour au menu principal
// //       displayMenu();
// //       return;
// //     }
    
// //     delay(500);  // Attendre un peu avant d'afficher les points suivants
// //   }

// //   irSignals[signalCount++] = results.value;
// //   irrecv.resume();  // Préparer à recevoir un autre signal
// //   display.clearDisplay();
// //   display.setCursor(0, 0);
// //   display.println("Signal enregistre");
// //   display.display();
// //   delay(2000);
// //   currentMenu = &mainMenu;  // Retour au menu principal
// //   displayMenu();
// // }

// // // Fonction pour émettre un signal IR
// // void emitSignal() {
// //   display.clearDisplay();
// //   display.setCursor(0, 0);
// //   display.println("Sélectionnez un signal");

// //   for (int i = 0; i < signalCount; i++) {
// //     display.setCursor(0, 10 + i * 10);
// //     display.print(i + 1);
// //     display.print(". Signal IR ");
// //     display.println(i + 1);
// //   }
// //   display.display();

// //   // Attente de la sélection du signal
// //   int selectedSignal = -1;
// //   while (selectedSignal == -1) {
// //     if (digitalRead(buttonPin2) == LOW) {  // Haut
// //       selectedSignal = (selectedSignal - 1 + signalCount) % signalCount;
// //       delay(200);
// //     } else if (digitalRead(buttonPin3) == LOW) {  // Bas
// //       selectedSignal = (selectedSignal + 1) % signalCount;
// //       delay(200);
// //     }

// //     // Attente d'une sélection avec le bouton Valider
// //     if (digitalRead(buttonPin4) == LOW) {  // Valider
// //       display.clearDisplay();
// //       display.setCursor(0, 0);
// //       display.println("Emission en cours...");
// //       display.display();
// //       delay(2000);  // Affichage du message
// //       // Emission du signal
// //       IRsend irsend;
// //       irsend.sendNEC(irSignals[selectedSignal], 32);  // Par exemple, en utilisant le protocole NEC
// //       delay(3000);  // Attente de 3 secondes avant de revenir au menu
// //       currentMenu = &mainMenu;
// //       displayMenu();
// //     }
// //   }
// // }

// // // #include <Wire.h>
// // // #include <Adafruit_GFX.h>
// // // #include <Adafruit_SSD1306.h>

// // // // Configuration de l'écran OLED
// // // #define SCREEN_WIDTH 128
// // // #define SCREEN_HEIGHT 64
// // // #define OLED_RESET -1
// // // #define SCREEN_ADDRESS 0x3C
// // // Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// // // // Définir les broches des boutons
// // // const int buttonPin1 = 32; // Retour
// // // const int buttonPin2 = 25; // Haut
// // // const int buttonPin3 = 26; // Bas
// // // const int buttonPin4 = 27; // Valider

// // // // Variables pour stocker l'état des boutons
// // // bool button1Pressed = false;
// // // bool button2Pressed = false;
// // // bool button3Pressed = false;
// // // bool button4Pressed = false;

// // // // Verrous pour éviter le double-clic
// // // bool button1Lock = false;
// // // bool button2Lock = false;
// // // bool button3Lock = false;
// // // bool button4Lock = false;

// // // // Variables pour le debounce
// // // unsigned long lastDebounceTime1 = 0;
// // // unsigned long lastDebounceTime2 = 0;
// // // unsigned long lastDebounceTime3 = 0;
// // // unsigned long lastDebounceTime4 = 0;
// // // const unsigned long debounceDelay = 200; // 200 ms pour éviter le double-clic

// // // // Structure pour représenter un menu
// // // struct Menu {
// // //   const char* title;
// // //   const char** options;
// // //   int size;
// // //   Menu* parent;
// // // };

// // // // Menus
// // // const char* mainMenuOptions[] = {"Option 1", "Option 2", "Option 3"};
// // // const char* subMenu1Options[] = {"Sub-Option 1.1", "Sub-Option 1.2", "Sub-Option 1.3"};
// // // const char* subMenu2Options[] = {"Sub-Option 2.1", "Sub-Option 2.2", "Sub-Option 2.3"};
// // // const char* subMenu3Options[] = {"Sub-Option 3.1", "Sub-Option 3.2", "Sub-Option 3.3"};

// // // Menu mainMenu = {"Main Menu", mainMenuOptions, 3, nullptr};
// // // Menu subMenu1 = {"Sub Menu 1", subMenu1Options, 3, &mainMenu};
// // // Menu subMenu2 = {"Sub Menu 2", subMenu2Options, 3, &mainMenu};
// // // Menu subMenu3 = {"Sub Menu 3", subMenu3Options, 3, &mainMenu};

// // // Menu* currentMenu = &mainMenu;
// // // int menuIndex = 0;

// // // void setup() {
// // //   Serial.begin(9600);

// // //   // Initialiser l'écran OLED
// // //   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
// // //     Serial.println(F("SSD1306 allocation failed"));
// // //     for(;;);
// // //   }

// // //   // Initialiser les broches des boutons
// // //   pinMode(buttonPin1, INPUT_PULLUP);
// // //   pinMode(buttonPin2, INPUT_PULLUP);
// // //   pinMode(buttonPin3, INPUT_PULLUP);
// // //   pinMode(buttonPin4, INPUT_PULLUP);

// // //   // Afficher le menu initial
// // //   displayMenu();
// // // }

// // // void loop() {
// // //   // Gestion du bouton Retour
// // //   if (digitalRead(buttonPin1) == LOW && !button1Lock) {
// // //     button1Pressed = true;
// // //     button1Lock = true;
// // //     lastDebounceTime1 = millis();
// // //   }
// // //   if (millis() - lastDebounceTime1 > debounceDelay) {
// // //     button1Lock = false;
// // //   }

// // //   // Gestion du bouton Haut
// // //   if (digitalRead(buttonPin2) == LOW && !button2Lock) {
// // //     button2Pressed = true;
// // //     button2Lock = true;
// // //     lastDebounceTime2 = millis();
// // //   }
// // //   if (millis() - lastDebounceTime2 > debounceDelay) {
// // //     button2Lock = false;
// // //   }

// // //   // Gestion du bouton Bas
// // //   if (digitalRead(buttonPin3) == LOW && !button3Lock) {
// // //     button3Pressed = true;
// // //     button3Lock = true;
// // //     lastDebounceTime3 = millis();
// // //   }
// // //   if (millis() - lastDebounceTime3 > debounceDelay) {
// // //     button3Lock = false;
// // //   }

// // //   // Gestion du bouton Valider
// // //   if (digitalRead(buttonPin4) == LOW && !button4Lock) {
// // //     button4Pressed = true;
// // //     button4Lock = true;
// // //     lastDebounceTime4 = millis();
// // //   }
// // //   if (millis() - lastDebounceTime4 > debounceDelay) {
// // //     button4Lock = false;
// // //   }

// // //   // Mise à jour du menu en fonction des boutons pressés
// // //   if (button1Pressed) {
// // //     if (currentMenu->parent != nullptr) {
// // //       currentMenu = currentMenu->parent;
// // //       menuIndex = 0;
// // //       displayMenu();
// // //     }
// // //     button1Pressed = false;
// // //   }

// // //   if (button2Pressed) {
// // //     menuIndex = (menuIndex - 1 + currentMenu->size) % currentMenu->size;
// // //     displayMenu();
// // //     button2Pressed = false;
// // //   }

// // //   if (button3Pressed) {
// // //     menuIndex = (menuIndex + 1) % currentMenu->size;
// // //     displayMenu();
// // //     button3Pressed = false;
// // //   }

// // //   if (button4Pressed) {
// // //     if (currentMenu == &mainMenu) {
// // //       switch (menuIndex) {
// // //         case 0:
// // //           currentMenu = &subMenu1;
// // //           break;
// // //         case 1:
// // //           currentMenu = &subMenu2;
// // //           break;
// // //         case 2:
// // //           currentMenu = &subMenu3;
// // //           break;
// // //       }
// // //       menuIndex = 0;
// // //       displayMenu();
// // //     } else {
// // //       display.clearDisplay();
// // //       display.setCursor(0, 0);
// // //       display.println(F("Selected: "));
// // //       display.println(currentMenu->options[menuIndex]);
// // //       display.display();
// // //       delay(2000);
// // //       displayMenu();
// // //     }
// // //     button4Pressed = false;
// // //   }
// // // }

// // // // Fonction pour afficher le menu
// // // void displayMenu() {
// // //   display.clearDisplay();
// // //   display.setTextSize(1);
// // //   display.setTextColor(SSD1306_WHITE);
// // //   display.setCursor(0, 0);
// // //   display.println(currentMenu->title);

// // //   for (int i = 0; i < currentMenu->size; i++) {
// // //     display.setCursor(10, (i + 1) * 10);
// // //     if (i == menuIndex) {
// // //       display.print(F("> ")); // Indicateur de sélection
// // //     } else {
// // //       display.print(F("  "));
// // //     }
// // //     display.println(currentMenu->options[i]);
// // //   }

// // //   display.display();
// // // }

// // // // #include <Wire.h>
// // // // #include <Adafruit_GFX.h>
// // // // #include <Adafruit_SSD1306.h>

// // // // #define SCREEN_WIDTH 128
// // // // #define SCREEN_HEIGHT 64
// // // // #define OLED_RESET -1
// // // // #define SCREEN_ADDRESS 0x3C

// // // // Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// // // // // Définir les broches des boutons
// // // // const int buttonPin1 = 32; // Retour
// // // // const int buttonPin2 = 25; // Haut
// // // // const int buttonPin3 = 26; // Bas
// // // // const int buttonPin4 = 27; // Valider

// // // // // Variables pour stocker l'état des boutons
// // // // volatile bool button1Pressed = false;
// // // // volatile bool button2Pressed = false;
// // // // volatile bool button3Pressed = false;
// // // // volatile bool button4Pressed = false;

// // // // // Structure pour représenter un menu
// // // // struct Menu {
// // // //   const char* title;
// // // //   const char** options;
// // // //   int size;
// // // //   Menu* parent;
// // // // };

// // // // // Menus
// // // // const char* mainMenuOptions[] = {"Option 1", "Option 2", "Option 3"};
// // // // const char* subMenu1Options[] = {"Sub-Option 1.1", "Sub-Option 1.2", "Sub-Option 1.3"};
// // // // const char* subMenu2Options[] = {"Sub-Option 2.1", "Sub-Option 2.2", "Sub-Option 2.3"};
// // // // const char* subMenu3Options[] = {"Sub-Option 3.1", "Sub-Option 3.2", "Sub-Option 3.3"};

// // // // Menu mainMenu = {"Main Menu", mainMenuOptions, 3, nullptr};
// // // // Menu subMenu1 = {"Sub Menu 1", subMenu1Options, 3, &mainMenu};
// // // // Menu subMenu2 = {"Sub Menu 2", subMenu2Options, 3, &mainMenu};
// // // // Menu subMenu3 = {"Sub Menu 3", subMenu3Options, 3, &mainMenu};

// // // // Menu* currentMenu = &mainMenu;
// // // // int menuIndex = 0;

// // // // void setup() {
// // // //   Serial.begin(9600);

// // // //   // Initialiser l'écran OLED
// // // //   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
// // // //     Serial.println(F("SSD1306 allocation failed"));
// // // //     for(;;);
// // // //   }

// // // //   // Initialiser les broches des boutons
// // // //   pinMode(buttonPin1, INPUT_PULLUP);
// // // //   pinMode(buttonPin2, INPUT_PULLUP);
// // // //   pinMode(buttonPin3, INPUT_PULLUP);
// // // //   pinMode(buttonPin4, INPUT_PULLUP);

// // // //   // Attacher les interruptions aux broches des boutons
// // // //   attachInterrupt(digitalPinToInterrupt(buttonPin1), button1ISR, FALLING);
// // // //   attachInterrupt(digitalPinToInterrupt(buttonPin2), button2ISR, FALLING);
// // // //   attachInterrupt(digitalPinToInterrupt(buttonPin3), button3ISR, FALLING);
// // // //   attachInterrupt(digitalPinToInterrupt(buttonPin4), button4ISR, FALLING);

// // // //   // Afficher le menu initial
// // // //   displayMenu();
// // // // }

// // // // void loop() {
// // // //   // Vérifier si un bouton a été pressé et mettre à jour le menu
// // // //   if (button1Pressed) {
// // // //     // Retour au menu précédent
// // // //     if (currentMenu->parent != nullptr) {
// // // //       currentMenu = currentMenu->parent;
// // // //       menuIndex = 0;
// // // //       displayMenu();
// // // //     }
// // // //     button1Pressed = false;
// // // //   }

// // // //   if (button2Pressed) {
// // // //     // Naviguer vers le haut
// // // //     menuIndex = (menuIndex - 1 + currentMenu->size) % currentMenu->size;
// // // //     displayMenu();
// // // //     button2Pressed = false;
// // // //   }

// // // //   if (button3Pressed) {
// // // //     // Naviguer vers le bas
// // // //     menuIndex = (menuIndex + 1) % currentMenu->size;
// // // //     displayMenu();
// // // //     button3Pressed = false;
// // // //   }

// // // //   if (button4Pressed) {
// // // //     // Valider la sélection
// // // //     if (currentMenu == &mainMenu) {
// // // //       switch (menuIndex) {
// // // //         case 0:
// // // //           currentMenu = &subMenu1;
// // // //           break;
// // // //         case 1:
// // // //           currentMenu = &subMenu2;
// // // //           break;
// // // //         case 2:
// // // //           currentMenu = &subMenu3;
// // // //           break;
// // // //       }
// // // //       menuIndex = 0;
// // // //       displayMenu();
// // // //     } else {
// // // //       display.clearDisplay();
// // // //       display.setCursor(0, 0);
// // // //       display.println(F("Selected: "));
// // // //       display.println(currentMenu->options[menuIndex]);
// // // //       display.display();
// // // //       delay(2000); // Afficher la sélection pendant 2 secondes
// // // //       displayMenu(); // Revenir au menu
// // // //     }
// // // //     button4Pressed = false;
// // // //   }
// // // // }

// // // // // Fonctions d'interruption pour les boutons
// // // // void button1ISR() {
// // // //   button1Pressed = true;
// // // // }

// // // // void button2ISR() {
// // // //   button2Pressed = true;
// // // // }

// // // // void button3ISR() {
// // // //   button3Pressed = true;
// // // // }

// // // // void button4ISR() {
// // // //   button4Pressed = true;
// // // // }

// // // // // Fonction pour afficher le menu
// // // // void displayMenu() {
// // // //   display.clearDisplay();
// // // //   display.setTextSize(1);
// // // //   display.setTextColor(SSD1306_WHITE);
// // // //   display.setCursor(0, 0);
// // // //   display.println(currentMenu->title);

// // // //   for (int i = 0; i < currentMenu->size; i++) {
// // // //     display.setCursor(10, (i + 1) * 10);
// // // //     if (i == menuIndex) {
// // // //       display.print(F("> "));
// // // //     } else {
// // // //       display.print(F("  "));
// // // //     }
// // // //     display.println(currentMenu->options[i]);
// // // //   }

// // // //   display.display();
// // // // }

// // // // // #include <Wire.h>
// // // // // #include <Adafruit_GFX.h>
// // // // // #include <Adafruit_SSD1306.h>

// // // // // #define SCREEN_WIDTH 128
// // // // // #define SCREEN_HEIGHT 64
// // // // // #define OLED_RESET -1
// // // // // #define SCREEN_ADDRESS 0x3C

// // // // // Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// // // // // // Définir les broches des boutons
// // // // // const int buttonPin1 = 32; // Retour
// // // // // const int buttonPin2 = 25; // Haut
// // // // // const int buttonPin3 = 26; // Bas
// // // // // const int buttonPin4 = 27; // Valider

// // // // // // Variables pour stocker l'état des boutons
// // // // // volatile bool button1Pressed = false;
// // // // // volatile bool button2Pressed = false;
// // // // // volatile bool button3Pressed = false;
// // // // // volatile bool button4Pressed = false;

// // // // // // Variables pour le menu
// // // // // int menuIndex = 0;
// // // // // const int menuSize = 3;
// // // // // const char* menuOptions[] = {"Option 1", "Option 2", "Option 3"};

// // // // // void setup() {
// // // // //   Serial.begin(9600);

// // // // //   // Initialiser l'écran OLED
// // // // //   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
// // // // //     Serial.println(F("SSD1306 allocation failed"));
// // // // //     for(;;);
// // // // //   }

// // // // //   // Initialiser les broches des boutons
// // // // //   pinMode(buttonPin1, INPUT_PULLUP);
// // // // //   pinMode(buttonPin2, INPUT_PULLUP);
// // // // //   pinMode(buttonPin3, INPUT_PULLUP);
// // // // //   pinMode(buttonPin4, INPUT_PULLUP);

// // // // //   // Attacher les interruptions aux broches des boutons
// // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin1), button1ISR, FALLING);
// // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin2), button2ISR, FALLING);
// // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin3), button3ISR, FALLING);
// // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin4), button4ISR, FALLING);

// // // // //   // Afficher le menu initial
// // // // //   displayMenu();
// // // // // }

// // // // // void loop() {
// // // // //   // Vérifier si un bouton a été pressé et mettre à jour le menu
// // // // //   if (button1Pressed) {
// // // // //     // Retour en arrière
// // // // //     menuIndex = (menuIndex - 1 + menuSize) % menuSize;
// // // // //     displayMenu();
// // // // //     button1Pressed = false;
// // // // //   }

// // // // //   if (button2Pressed) {
// // // // //     // Naviguer vers le haut
// // // // //     menuIndex = (menuIndex - 1 + menuSize) % menuSize;
// // // // //     displayMenu();
// // // // //     button2Pressed = false;
// // // // //   }

// // // // //   if (button3Pressed) {
// // // // //     // Naviguer vers le bas
// // // // //     menuIndex = (menuIndex + 1) % menuSize;
// // // // //     displayMenu();
// // // // //     button3Pressed = false;
// // // // //   }

// // // // //   if (button4Pressed) {
// // // // //     // Valider la sélection
// // // // //     display.clearDisplay();
// // // // //     display.setCursor(0, 0);
// // // // //     display.println(F("Selected: "));
// // // // //     display.println(menuOptions[menuIndex]);
// // // // //     display.display();
// // // // //     button4Pressed = false;
// // // // //     delay(2000); // Afficher la sélection pendant 2 secondes
// // // // //     displayMenu(); // Revenir au menu
// // // // //   }
// // // // // }

// // // // // // Fonctions d'interruption pour les boutons
// // // // // void button1ISR() {
// // // // //   button1Pressed = true;
// // // // // }

// // // // // void button2ISR() {
// // // // //   button2Pressed = true;
// // // // // }

// // // // // void button3ISR() {
// // // // //   button3Pressed = true;
// // // // // }

// // // // // void button4ISR() {
// // // // //   button4Pressed = true;
// // // // // }

// // // // // // Fonction pour afficher le menu
// // // // // void displayMenu() {
// // // // //   display.clearDisplay();
// // // // //   display.setTextSize(1);
// // // // //   display.setTextColor(SSD1306_WHITE);
// // // // //   display.setCursor(0, 0);
// // // // //   display.println(F("Menu:"));

// // // // //   for (int i = 0; i < menuSize; i++) {
// // // // //     display.setCursor(10, (i + 1) * 10);
// // // // //     if (i == menuIndex) {
// // // // //       display.print(F("> "));
// // // // //     } else {
// // // // //       display.print(F("  "));
// // // // //     }
// // // // //     display.println(menuOptions[i]);
// // // // //   }

// // // // //   display.display();
// // // // // }

// // // // // // #include <Wire.h>
// // // // // // #include <Adafruit_GFX.h>
// // // // // // #include <Adafruit_SSD1306.h>

// // // // // // #define SCREEN_WIDTH 128
// // // // // // #define SCREEN_HEIGHT 64
// // // // // // #define OLED_RESET -1
// // // // // // #define SCREEN_ADDRESS 0x3C

// // // // // // Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// // // // // // // Définir les broches des boutons
// // // // // // const int buttonPin1 = 32;
// // // // // // const int buttonPin2 = 25;
// // // // // // const int buttonPin3 = 26;
// // // // // // const int buttonPin4 = 27;

// // // // // // // Variables pour stocker l'état des boutons
// // // // // // volatile bool button1Pressed = false;
// // // // // // volatile bool button2Pressed = false;
// // // // // // volatile bool button3Pressed = false;
// // // // // // volatile bool button4Pressed = false;

// // // // // // void setup() {
// // // // // //   Serial.begin(9600);

// // // // // //   // Initialiser l'écran OLED
// // // // // //   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
// // // // // //     Serial.println(F("SSD1306 allocation failed"));
// // // // // //     for(;;);
// // // // // //   }

// // // // // //   // Initialiser les broches des boutons
// // // // // //   pinMode(buttonPin1, INPUT_PULLUP);
// // // // // //   pinMode(buttonPin2, INPUT_PULLUP);
// // // // // //   pinMode(buttonPin3, INPUT_PULLUP);
// // // // // //   pinMode(buttonPin4, INPUT_PULLUP);

// // // // // //   // Attacher les interruptions aux broches des boutons
// // // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin1), button1ISR, FALLING);
// // // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin2), button2ISR, FALLING);
// // // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin3), button3ISR, FALLING);
// // // // // //   attachInterrupt(digitalPinToInterrupt(buttonPin4), button4ISR, FALLING);

// // // // // //   // Afficher un message initial
// // // // // //   display.clearDisplay();
// // // // // //   display.setTextSize(1);
// // // // // //   display.setTextColor(SSD1306_WHITE);
// // // // // //   display.setCursor(0, 0);
// // // // // //   display.println(F("Press a button!"));
// // // // // //   display.display();
// // // // // // }

// // // // // // void loop() {
// // // // // //   // Vérifier si un bouton a été pressé et afficher le message correspondant
// // // // // //   if (button1Pressed) {
// // // // // //     display.clearDisplay();
// // // // // //     display.setCursor(0, 0);
// // // // // //     display.println(F("Back !"));
// // // // // //     display.display();
// // // // // //     button1Pressed = false;
// // // // // //   }

// // // // // //   if (button2Pressed) {
// // // // // //     display.clearDisplay();
// // // // // //     display.setCursor(0, 0);
// // // // // //     display.println(F("Up !"));
// // // // // //     display.display();
// // // // // //     button2Pressed = false;
// // // // // //   }

// // // // // //   if (button3Pressed) {
// // // // // //     display.clearDisplay();
// // // // // //     display.setCursor(0, 0);
// // // // // //     display.println(F("Down !"));
// // // // // //     display.display();
// // // // // //     button3Pressed = false;
// // // // // //   }

// // // // // //   if (button4Pressed) {
// // // // // //     display.clearDisplay();
// // // // // //     display.setCursor(0, 0);
// // // // // //     display.println(F("valid !"));
// // // // // //     display.display();
// // // // // //     button4Pressed = false;
// // // // // //   }
// // // // // // }

// // // // // // // Fonctions d'interruption pour les boutons
// // // // // // void button1ISR() {
// // // // // //   button1Pressed = true;
// // // // // // }

// // // // // // void button2ISR() {
// // // // // //   button2Pressed = true;
// // // // // // }

// // // // // // void button3ISR() {
// // // // // //   button3Pressed = true;
// // // // // // }

// // // // // // void button4ISR() {
// // // // // //   button4Pressed = true;
// // // // // // }


// // // // // // // #include <Wire.h>
// // // // // // // #include <Adafruit_GFX.h>
// // // // // // // #include <Adafruit_SSD1306.h>

// // // // // // // #define SCREEN_WIDTH 128
// // // // // // // #define SCREEN_HEIGHT 64
// // // // // // // #define OLED_RESET -1
// // // // // // // #define SCREEN_ADDRESS 0x3C

// // // // // // // Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// // // // // // // void setup() {
// // // // // // //   Serial.begin(115200);

// // // // // // //   if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
// // // // // // //     Serial.println(F("SSD1306 allocation failed"));
// // // // // // //     for(;;);
// // // // // // //   }

// // // // // // //   display.clearDisplay();
// // // // // // //   display.setTextSize(1);      // Taille de texte normale
// // // // // // //   display.setTextColor(SSD1306_WHITE); // Couleur du texte
// // // // // // //   display.setCursor(0, 0);     // Position du curseur
// // // // // // //   display.println(F("Hello, World!")); // Affiche le texte
// // // // // // //   display.display(); // Met à jour l'affichage
// // // // // // // }

// // // // // // // void loop() {
// // // // // // //   // Rien à faire ici
// // // // // // // }
