#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

// Replace with your network credentials
const char* ssid = "VodafoneArmata Edition";          // WiFi SSID
const char* ssid_password = "MassoneTerrone666!";     // WiFi password

// MQTT settings
const char* mqtt_server = "rebus.ninja";              // MQTT server 
const int mqtt_port = 1883;                           // MQTT port     
const char* mqtt_user = "test";                      // MQTT username
const char* mqtt_password = "test-user";             // MQTT password

const char* client_id = "esp8266-lore";                  // Device name
const char* topic = "devices/esp8266-lore";                 // Topic to subscribe to

const int heartbeat_interval = 30000; // 30 seconds

// WiFiClient setup
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
String msg;
int value = 0;

// NTP client setup
const long utcOffsetInSeconds = 3600;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "europe.pool.ntp.org", utcOffsetInSeconds);
char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

void setup_wifi() {
  delay(10);
  // Connect to Wi-Fi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, ssid_password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {

  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  
  Serial.print("Message arrived on topic: " + String(topic) + " Message: " + messageTemp);
  Serial.println();

  // Example of handling a message received on a specific topic
  if (String(topic) == topic) {
    
    if(messageTemp == "stop_alarm"){
      Serial.println("off");
      digitalWrite(LED_BUILTIN, HIGH);
      
      // TODO: Add your code here to stop the alarm
    }
    
    else if(messageTemp == "trigger_alarm"){

      digitalWrite(LED_BUILTIN, LOW);
      
      // TODO: Add your code here to trigger the alarm
    }

    else{
      Serial.println("Unknown message");
    }
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(client_id, mqtt_user, mqtt_password)) {
      Serial.println("connected");

      // Subscribe to the required topic
      client.subscribe(topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  setup_wifi();

  timeClient.begin();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if ((now - lastMsg > heartbeat_interval)) {
    
    lastMsg = now;
    timeClient.update();

    msg = "{ \"name\": \"" + String(client_id) + "\", \"time\": \"" + timeClient.getFormattedTime() + "\" }";

    Serial.println("Publish message: " + msg + " to topic: devices/heartbeat");
    client.publish("devices/heartbeat", msg.c_str());
  }
}
