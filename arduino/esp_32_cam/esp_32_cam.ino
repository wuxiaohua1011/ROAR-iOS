/**
 * Dependency:
 *    https://www.arduino.cc/reference/en/libraries/esp32servo/
 * 
 * Get Started:
 * 1. Install ESP 32 Board (Tools -> Board -> Boards Manager, search for ESP32)
 * 2. Select AI Thinker ESP32-Cam in the Tools -> Board -> ESP32 Arduino -> AI Thinker ESP32-Cam
 * 3. Replace WIFI_SSID and WIFI_PASS with your Wifi credentials
 * 4. Click the upload button
 */

#include <esp32cam.h>
#include <WebServer.h>
#include <WiFi.h>
#include <ESP32Servo.h> 



//#include <BLEDevice.h>
//#include <BLEUtils.h>
//#include <BLEServer.h>

//#include <BLE2902.h>
#include <Arduino.h>

#define SERVICE_UUID "ab0828b1-198e-4351-b779-901fa0e0371e"
#define CONTROL_UUID "19B10011-E8F2-537E-4F6C-D104768A1214"

#define DEVINFO_UUID (uint16_t)0x180a
#define DEVINFO_MANUFACTURER_UUID (uint16_t)0x2a29
#define DEVINFO_NAME_UUID (uint16_t)0x2a24
#define DEVINFO_SERIAL_UUID (uint16_t)0x2a25

#define DEVICE_MANUFACTURER "Intelligent Racing"
#define DEVICE_NAME "IR Vehicle Control"

bool is_bluetooth_connected = false;

const char HANDSHAKE_START = '(';
char* WIFI_SSID = "NETGEAR78";
char* WIFI_PASS = "wuxiaohua1011";

WebServer server(80);
AsyncWebSocket ws("/test");

//Servo throttleServo;
//Servo steeringServo;

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);

volatile int32_t bluetooth_throttle_read = 1500;
volatile int32_t bluetooth_steering_read = 1500;



//BLECharacteristic *controlBLECharacteristicMessage;
//class MyServerCallbacks : public BLEServerCallbacks
//{
//    void onConnect(BLEServer *server)
//    {
//        Serial.println("Connected");
//        is_bluetooth_connected = true;
//    };
//
//    void onDisconnect(BLEServer *server)
//    {
//        Serial.println("Disconnected");
//        is_bluetooth_connected = false;
//    }
//};
//
//
//class ControlCallback : public BLECharacteristicCallbacks
//{
//    void onWrite(BLECharacteristic *characteristic)
//    {
//        std::string data = characteristic->getValue();
//        int n = data.length();
//        char buf[n+1];
//        strcpy(buf, data.c_str());
//        char *token = strtok(buf, ",");
//        if (token[0] == HANDSHAKE_START) {
//          if (token != NULL) {
//            unsigned int curr_throttle_read = atoi(token + 1);
//            if (curr_throttle_read >= 1000 and curr_throttle_read <= 2000) {
//              bluetooth_throttle_read = curr_throttle_read;
//            } 
//          }
//          token = strtok(NULL, ",");
//          if (token != NULL) {
//            unsigned int curr_steering_read = atoi(token);
//            if (curr_steering_read >= 1000 and curr_steering_read <= 2000) {
//              bluetooth_steering_read = curr_steering_read;
//            }
//          }
//        } 
//    }
//
//    void onRead(BLECharacteristic *characteristic)
//    {
//        // TODO revise what's being sent here
//        characteristic->setValue("(1500,1500)");
//        
//    }
//};
//
//void startBLE() {
//  // Setup BLE Server
//    BLEDevice::init(DEVICE_NAME);
//    
//    BLEServer *server = BLEDevice::createServer();
//    server->setCallbacks(new MyServerCallbacks());
//
//    // Register message service that can receive messages and reply with a static message.
//    BLEService *service = server->createService(SERVICE_UUID);
//    controlBLECharacteristicMessage = service->createCharacteristic(CONTROL_UUID, 
//                                                                    BLECharacteristic::PROPERTY_READ | 
//                                                                    BLECharacteristic::PROPERTY_NOTIFY |
//                                                                    BLECharacteristic::PROPERTY_WRITE);
//    controlBLECharacteristicMessage->setCallbacks(new ControlCallback());
////    controlBLECharacteristicMessage->addDescriptor(new BLE2902());
//    service->start();
//
//    // TODO add another BLE service for changing BLE Name
//
//    // TODO add another BLE service for connecting to Wifi (2Ghz)
//    
//
//    // Advertise services
//    BLEAdvertising *advertisement = BLEDevice::getAdvertising();
//    advertisement->addServiceUUID(SERVICE_UUID);
//    advertisement->setScanResponse(true);
//    advertisement->setMinPreferred(0x06);  // functions that help with iPhone connections issue
//    advertisement->setMinPreferred(0x12);
//    BLEDevice::startAdvertising();
//    Serial.println("BLE Ready");
//}



void setup()
{
  Serial.begin(115200);
  startCamera();
  startWebserver();
//  startBLE();
//  startServo();
}

//void startServo(){
//  throttleServo.attach(16, 1000, 2000);
//}
void startCamera() {
    {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }
}
void startWebserver(){
  
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.print("IP Addr: ");
  Serial.println(WiFi.localIP());
  
  Serial.print("Available routes:");
  Serial.println("  /cam.bmp");
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam.mjpeg");

  server.on("/cam.bmp", handleBmp);
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam.jpg", handleJpg);
  server.on("/cam.mjpeg", handleMjpeg);



  server.begin();
}

void loop()
{
  server.handleClient();  
}




void handleBmp()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }

  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  if (!frame->toBmp()) {
    Serial.println("CONVERT FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CONVERT OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/bmp");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void handleJpg()
{
  server.sendHeader("Location", "/cam-hi.jpg");
  server.send(302, "", "");
}

void handleMjpeg()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }

  Serial.println("STREAM BEGIN");
  WiFiClient client = server.client();
  auto startTime = millis();
  int res = esp32cam::Camera.streamMjpeg(client);
  if (res <= 0) {
    Serial.printf("STREAM ERROR %d\n", res);
    return;
  }
  auto duration = millis() - startTime;
  Serial.printf("STREAM END %dfrm %0.2ffps\n", res, 1000.0 * res / duration);
}
