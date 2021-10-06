#include <WiFi.h>
char* WIFI_SSID = "NETGEAR05";
char* WIFI_PASS = "niftysheep265";

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  initWifi();
}

void loop() {
  // put your main code here, to run repeatedly:

}

void initWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to Wifi ..");
  while (WiFi.status()  != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println(WiFi.localIP());
}
