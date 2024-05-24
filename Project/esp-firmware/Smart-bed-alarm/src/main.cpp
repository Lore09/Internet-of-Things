#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define TEST_CLIENT false  // Set to true to use the test client, false to use the real client

// Replace with your network credentials
const char* ssid = "wifi-name";          // WiFi SSID
const char* ssid_password = "wifi-pass";     // WiFi password

// MQTT settings
const char* mqtt_server = "your.domain";              // MQTT server 
const int mqtt_port = 1883;                           // MQTT port     
const char* mqtt_user = "your-user";                      // MQTT username
const char* mqtt_password = "your-password";             // MQTT password


WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

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
  if (String(topic) == "esp8266/output") {
    
    if(messageTemp == "Changing output to off"){
      Serial.println("off");
      digitalWrite(LED_BUILTIN, HIGH);
      // Do something
    }
    
    else if(messageTemp == "on"){
      Serial.println("Changing output to on");
      digitalWrite(LED_BUILTIN, LOW);
      // Do something else
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
    if (client.connect("ESP8266TestClient", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      // Subscribe to a topic
      client.subscribe("esp8266/output");
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
  if (TEST_CLIENT && (now - lastMsg > 2000)) {
    lastMsg = now;
    ++value;
    snprintf (msg, 50, "hello world #%ld", value);
    Serial.print("Publish message: ");
    Serial.println(msg);
    client.publish("esp8266/test", msg);
  }
}
