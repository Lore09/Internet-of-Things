#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ESP8266HTTPClient.h>

#include "AudioFileSourcePROGMEM.h"
#include "AudioGeneratorMP3.h"
#include "AudioOutputI2SNoDAC.h"
#include "AudioFileSourceBuffer.h"

#include "accumula_town.h"
#include "battle_platinum.h"
#include "undella_town.h"
//#include "dragonspiral_tower.h"

// Replace with your network credentials
const char* ssid = "VodafoneArmata Edition";          // WiFi SSID
const char* ssid_password = "MassoneTerrone666!";     // WiFi password

// MQTT settings
const char* mqtt_server = "rebus.ninja";              // MQTT server 
const int mqtt_port = 1883;                           // MQTT port     
const char* mqtt_user = "test";                      // MQTT username
const char* mqtt_password = "test-user";             // MQTT password
const char* topic = "devices/esp8266-lore"; 
const int heartbeat_interval = 30000; // 30 seconds

// Sensor settings
const char* client_id = "esp8266-lore";                  // Device name
const char* sensor_endpoint = "http://rebus.ninja:5000/api/sensor_data";
int samplinge_rate = 5; // 5 seconds
const int SENSOR_PIN = A0;


// Audio client setup
AudioGeneratorMP3 *player;
AudioFileSourcePROGMEM *file;
AudioOutputI2SNoDAC *out;
AudioFileSourceBuffer *buff;
int current_song = 0;

// WiFiClient setup
WiFiClient espClient;
PubSubClient client(espClient);
long lastHeartbeat = 0;
long lastSample = 0;
long now = 0;
long httpStartTime = 0;
long httpTimeTaken = 0;
String msg;

// NTP client setup
const long utcOffsetInSeconds = 3600;
WiFiUDP ntpUDP;

// HttpClient
HTTPClient http;

void play_audio(){
  
    if(player->isRunning())
      player->stop();

    delay(10);
  
    // SONG MAPPING
    switch (current_song)
    {
    case 1: // Cloudy
      file = new AudioFileSourcePROGMEM( battle_platinum_mp3, sizeof(battle_platinum_mp3) );
      break;

    case 2: // Rainy
      file = new AudioFileSourcePROGMEM( undella_town_mp3, sizeof(undella_town_mp3) );
      break;
  
    // case 3: // Foggy
    //   file = new AudioFileSourcePROGMEM( dragonspiral_tower_mp3, sizeof(dragonspiral_tower_mp3) );
    //   break;
    
    default: // Sunny or default
      file = new AudioFileSourcePROGMEM( accumula_town_mp3, sizeof(accumula_town_mp3) );
      current_song = 0;
    }
  
    buff = new AudioFileSourceBuffer(file, 2048);
    player->begin(buff, out);
  
}

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

      Serial.println("Alarm off");
      player->stop();
      
      return;
    }
    
    if(messageTemp.indexOf("trigger_alarm") >= 0){

      Serial.println("Alarm on");
      
      // get the song index
      current_song = messageTemp.substring(messageTemp.indexOf(" ") + 1).toInt();

      play_audio();

      return;
    }

    if(messageTemp.indexOf("sampling_rate") >= 0){

      // split by space
      int index = messageTemp.indexOf(" ");
      int rate = messageTemp.substring(index + 1).toInt();

      if(rate > 0){
        samplinge_rate = rate;
        Serial.println("New sampling rate: " + String(samplinge_rate) + " seconds");
      }

      return;
    }

    Serial.println("Unknown message");
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

void setupAudio(){

  audioLogger = &Serial;
  out = new AudioOutputI2SNoDAC();
  
  player = new AudioGeneratorMP3();

}


void setup() {
  Serial.begin(9600);
  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  http.begin(espClient, sensor_endpoint);

  setupAudio();

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(SENSOR_PIN, INPUT);
  digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  now = millis();
  if ((now - lastHeartbeat > heartbeat_interval)) {
    
    lastHeartbeat = now;

    msg = "{ \"name\": \"" + String(client_id) + "\", \"sampling_rate\": " + String(samplinge_rate) + ", \"request_time\": " + String(httpTimeTaken) + "}";

    Serial.println("Publish message: " + msg + " to topic: devices/heartbeat");
    client.publish("devices/heartbeat", msg.c_str());
  }

  if ((now - lastSample > samplinge_rate * 1000)) {
    
    lastSample = now;

    // read sensor data
    int data = analogRead(SENSOR_PIN);

    String content = "client_id=" + String(client_id) + "&data=" + String(data);
    Serial.println("Sending data:\t" + content);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    httpStartTime = millis();
    http.POST(content);
    httpTimeTaken = millis() - httpStartTime;
    
  }

  if (player->isRunning()) {

    if (!player->loop()){
      play_audio();
    }
      
  }

}
