#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <Adafruit_NeoPixel.h>

// --- CONFIGURATION DU WIFI ---
const char* ssid = "iPhone Ilyan";
const char* password = "ilyanjude";

// --- CONFIGURATION DU DHT11 ---
#define DHTPIN 27
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- CONFIGURATION DES LEDS ---
#define LED_PIN 25      // Pin où sont connectées les LEDs
#define NUM_LEDS 8     // Nombre de LEDs dans le cercle
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// --- DÉCLARATION DU SERVEUR WEB ---
WebServer server(80);

// --- VARIABLES ---
float temperature = 0;
float humidity = 0;

// --- CHANGEMENT DE COULEUR EN FONCTION DE L'HUMIDITÉ ---
void updateLEDs(float hum) {
    
    uint32_t color;
    strip.clear(); // Effacer d'abord toutes les LEDs

    // Changer la couleur en fonction de l'humidité
    if (hum > 60) {
      color = strip.Color(255, 0, 255); 
        
    } else if (hum > 30) {
      color = strip.Color(255, 255, 255);
      
    } else {
      color = strip.Color(255, 255, 26); 
          
    }

    // Appliquer la couleur à chaque LED
    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, color);
    }
    
    strip.setBrightness(20); // Ajouter une luminosité modérée
    strip.show(); // Afficher les changements
}

// --- GÉNÉRATION DE LA PAGE WEB ---
void handleRoot() {
    String html = R"rawliteral(
    <!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script
      src="https://kit.fontawesome.com/ec35368b02.js"
      crossorigin="anonymous"
    ></script>
    <title>Station Météo</title>
    <style>
      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }

      body {
        overflow-x: hidden;
        font-family: Arial, sans-serif;
        text-align: center;
        background-color: #3b82f6;
        color: #ffffff;
      }

      .title {
        width: 100vw;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        padding: 50px 0;
      }

      .container {
        width: 400px;
        height: 150px;
        margin: 10px;
        padding: 20px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        color: #f8fafc;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
      }

      .all-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-wrap: wrap;
        height: 100%;
        width: 100vw;
        margin-bottom: 50px;
      }
      #date {
        opacity: 75%;
      }
      #date i {
        color: #f8fafc;
      }
      #div_horloge {
        font-size: 32px;
      }
      .info-station .fa-temperature-half {
        color: rgb(255, 116, 116);
        margin-right: 8px;
        font-size: 20px;
        width: 8%;
        text-align: center;
      }
      .fa-water {
        color: rgb(2, 2, 199);
        margin-right: 8px;
        font-size: 20px;
        width: 8%;
        text-align: center;
      }
      .info-station {
        width: 70%;
        text-align: start;
      }
      .message {
        min-width: 392px;
        max-width: 800px;
        width: 50%;
        height: 150px;
        text-align: center;
      }
      .message h3 {
        display: flex;
        gap: 20px;
      }
    </style>
  </head>
  <body>
    <div class="title">
      <i class="fa-solid fa-ghost"></i>
      <h1>Ma station météo</h1>
      <i class="fa-solid fa-poo-storm"></i>
    </div>
    <div class="all-container">
      <div class="container">
        <div id="date"></div>
        <div id="div_horloge"></div>
      </div>

      <div class="container">
        <div class="info-station">
          <i class="fa-solid fa-temperature-half"></i>
          <strong>Température :</strong> <span id="temp">--</span> °C
        </div>
        <div class="info-station">
          <i class="fa-solid fa-water"></i>
          <strong>Humidité :</strong> <span id="hum">--</span> %
        </div>
      </div>

      <div class="container message" id="message-temp">
        <h3></h3>
        <p></p>
      </div>

      <div class="container message" id="message-humidty">
        <h3></h3>
        <p></p>
      </div>
    </div>
    <script>
      const day = [
        "Dimanche",
        "Lundi",
        "Mardi",
        "Mercredi",
        "Jeudi",
        "Vendredi",
        "Samedi",
      ];
      const month = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
      ];

      const message_temp = {
        cold: {
          h3: "<i class='fa-solid fa-temperature-empty'></i> Attention, il fait vraiment froid ici ! <i class='fa-solid fa-snowman'></i>",
          p: "Ça va, tu ne gèles pas trop ? Petit conseil : pour réchauffer un peu l'ambiance, allume un radiateur si tu en as un. Sinon... bon courage !",
        },
        normal: {
          h3: "<i class='fa-solid fa-temperature-half'></i> Température parfaite ! <i class='fa-solid fa-sun'></i>",
          p: "Ni trop chaud, ni trop froid, t'es dans la zone de confort. Profites-en avant que ça change !</p>",
        },
        hot: {
          h3: "<i class='fa-solid fa-temperature-three-quarters'></i> Chaud, chaud, chaud ! <i class='fa-solid fa-fire'></i>",
          p: "Ça commence à cogner ! Pense à boire de l'eau et à rester à l'ombre si possible. Sinon, bon courage !",
        },
        superHot: {
          h3: "<i class='fa-solid fa-temperature-full'></i>C'est l'enfer ici !<i class='fa-solid fa-hot-tub'></i>",
          p: "Sérieusement, hydrate-toi, évite le soleil et mets un ventilateur ou la clim si tu peux. C'est une question de survie !",
        },
      };

      const message_humidity = {
        superSec: {
          h3: "<i class='fa-solid fa-wind'></i> Attention, c'est le Sahara ici ! <i class='fa-solid fa-plant-wilt'></i>",
          p: "L'air est si sec que même les poissons rouges demandent de l'eau ! Pense à boire un max et à mettre un bol d'eau sur le radiateur... ou prie pour une pluie miraculeuse.",
        },
        normal: {
          h3: "<i class='fa-solid fa-droplet'></i> Humidité parfaite, c'est la belle vie ! <i class='fa-solid fa-leaf'></i>",
          p: "Respire, détends-toi, t'es dans la zone idéale. Pas de peau qui craquelle, pas d'impression d'être dans une éponge... Profite avant que ça change !",
        },
        humid: {
          h3: "<i class='fa-solid fa-cloud-rain'></i> Ambiance sauna gratuite ! <i class='fa-solid fa-umbrella'></i>",
          p: "Même ton t-shirt transpire tout seul... Courage, ouvre une fenêtre ou mets un ventilo avant de te liquéfier sur place.",
        },
        superHumid: {
          h3: "<i class='fa-solid fa-temperature-high'></i> J'espère que tu sais nager ! <i class='fa-solid fa-fish'></i>",
          p: "L'air est tellement humide qu'il faudrait des palmes pour se déplacer. Si t'entends des grenouilles coasser, c'est normal. Garde un déshumidificateur à portée avant de voir des algues pousser chez toi !",
        },
      };

      window.onload = function () {
        horloge("div_horloge");
        date();
        displaysData();
        displayMessage(10, 0);
      };

      function displaysData() {
        setInterval(() => {
          fetch("/data")
            .then((response) => response.json())
            .then((data) => {
              document.getElementById("temp").textContent = data.temperature.toFixed(1);
              document.getElementById("hum").textContent = data.humidity.toFixed(1);
              displayMessage(data.temperature, data.humidity);
            })
            .catch((error) => console.error("Erreur:", error));
        }, 1000);
      }

      function displayMessage(temperature, humidity) {
        const h3_message_temp = document
          .getElementById("message-temp")
          .querySelector("h3");
        const p_message_temp = document
          .getElementById("message-temp")
          .querySelector("p");

        const h3_message_humidty = document
          .getElementById("message-humidty")
          .querySelector("h3");
        const p_message_humidty = document
          .getElementById("message-humidty")
          .querySelector("p");

        if (temperature <= 0) {
          h3_message_temp.innerHTML = message_temp.cold.h3;
          p_message_temp.innerHTML = message_temp.cold.p;
        } else if (temperature > 0 && temperature <= 23) {
          h3_message_temp.innerHTML = message_temp.normal.h3;
          p_message_temp.innerHTML = message_temp.normal.p;
        } else if (temperature > 23 && temperature <= 30) {
          h3_message_temp.innerHTML = message_temp.hot.h3;
          p_message_temp.innerHTML = message_temp.hot.p;
        } else {
          h3_message_temp.innerHTML = message_temp.superHot.h3;
          p_message_temp.innerHTML = message_temp.superHot.p;
        }

        if (humidity <= 30) {
          h3_message_humidty.innerHTML = message_humidity.superSec.h3;
          p_message_humidty.innerHTML = message_humidity.superSec.p;
        } else if (humidity > 30 && humidity <= 60) {
          h3_message_humidty.innerHTML = message_humidity.normal.h3;
          p_message_humidty.innerHTML = message_humidity.normal.p;
        } else if (humidity > 60 && humidity <= 80) {
          h3_message_humidty.innerHTML = message_humidity.humid.h3;
          p_message_humidty.innerHTML = message_humidity.humid.p;
        } else {
          h3_message_humidty.innerHTML = message_humidity.superHumid.h3;
          p_message_humidty.innerHTML = message_humidity.superHumid.p;
        }
      }

      function date() {
        const date = new Date();
        document.getElementById(
          "date"
        ).innerHTML = `<i class="fa-solid fa-calendar-week"></i>
                  ${day[date.getDay()]} ${date.getDate()}
                  ${month[date.getMonth()]}
                  ${date.getFullYear()}`;
      }

      function horloge(el) {
        if (typeof el == "string") {
          el = document.getElementById(el);
        }

        function actualiser() {
          const date = new Date();
          let str = date.getHours();
          str += ":" + (date.getMinutes() < 10 ? "0" : "") + date.getMinutes();
          str += ":" + (date.getSeconds() < 10 ? "0" : "") + date.getSeconds();
          el.innerHTML = str;
        }
        actualiser();
        setInterval(actualiser, 1000);
      }
    </script>
  </body>
</html>  )rawliteral";

    server.send(200, "text/html", html);
}

// --- ENVOI DES DONNÉES JSON ---
void handleData() {
    String json = "{ \"temperature\": " + String(temperature) + ", \"humidity\": " + String(humidity) + " }";
    server.send(200, "application/json", json);
}

// --- CONFIGURATION INITIALE ---
void setup() {
    Serial.begin(115200);
    Serial.println("Démarrage de l'ESP32...");

    dht.begin();
    strip.begin();
    strip.show(); // Éteindre toutes les LEDs au démarrage

    // Connexion Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Connexion au Wi-Fi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnecté !");
    Serial.print("Adresse IP : ");
    Serial.println(WiFi.localIP());

  // Configuration du serveur
    server.on("/", handleRoot);
    server.on("/data", handleData);
    server.begin();
    Serial.println("Serveur web démarré.");
}

// --- BOUCLE PRINCIPALE ---
void loop() {
    server.handleClient();

    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate >= 1000) { // Vérifier toutes les secondes
        float newTemp = dht.readTemperature();
        float newHum = dht.readHumidity();

        if (!isnan(newTemp) && !isnan(newHum)) {
            temperature = newTemp;
            humidity = newHum;
            updateLEDs(humidity);
            
            Serial.print("Température: ");
            Serial.print(temperature);
            Serial.print(" °C, Humidité: ");
            Serial.print(humidity);
            Serial.println(" %");
        } else {
            Serial.println("Erreur de lecture du capteur DHT11 !");
        }
        
        lastUpdate = millis();
    }
}