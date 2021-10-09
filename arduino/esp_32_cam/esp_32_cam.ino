#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
#include "esp_camera.h"
#include <uri/UriBraces.h>
#include <ESP32Servo.h>


#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
  

#define THROTTLE_PIN 14
#define STEERING_PIN 2
#define FLASH_LED_PIN 4
#define RED_LED_PIN 33


// CHANGE YOUR WIFI CREDENTIALS!
const char* WIFI_SSID = "NETGEAR05";
const char* WIFI_PASS = "wuxiaohua1011";

static auto loRes = esp32cam::Resolution::find(320, 240);


WebServer server(80);
Servo throttleServo;
Servo steeringServo;
volatile int32_t ws_throttle_read = 1500;
volatile int32_t ws_steering_read = 1500;


volatile bool isClientConnected = false;
bool isFlashLightOn = false;
bool isRedLEDOn = false;


void setup()
{
  Serial.begin(115200);
  Serial.println();
  pinMode(RED_LED_PIN, OUTPUT);
//  ledcSetup(0, 5000, 8);
//  ledcAttachPin(FLASH_LED_PIN, 0);
//  ledcWrite(FLASH_LED_PIN, 0);


  setupCamera();
  setupWifi();
  setupRoutes();
//  setupServo();
}



void loop()
{
  server.handleClient();
//  writeToServo(); 
  
}

void writeToServo() {
   steeringServo.writeMicroseconds(ws_steering_read);    // tell servo to go to position 'steering'
   throttleServo.writeMicroseconds(ws_throttle_read);    // tell motor to drive with power = motorPower   
}

// setup functions

void setupServo() {
  throttleServo.setPeriodHertz(50);
  throttleServo.attach(THROTTLE_PIN, 1000, 2000);
  steeringServo.setPeriodHertz(50);    // standard 50 hz servo
  steeringServo.attach(STEERING_PIN, 1000, 2000); // attaches the servo on pin (whatever you assign)
}

void setupRoutes() {
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cmd/<THROTTLE>,<STEERING>");

  server.on("/cam-lo.jpg", handleJpgLo);
  server.on(UriBraces("/cmd/{}"), handleCmd);
 
  server.begin();
}


void setupWifi() {
  WiFi.disconnect(true);

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting ...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    blinkRedLED();
    Serial.print(".");
  }
  digitalWrite(RED_LED_PIN, LOW);
  Serial.println("Connected!");
}
void setupCamera() {
//  {
//    using namespace esp32cam;
//    Config cfg;
//    cfg.setPins(pins::AiThinker);
//    cfg.setResolution(loRes);
//    cfg.setBufferCount(2);
//    cfg.setJpeg(80);
//
//    bool ok = Camera.begin(cfg);
//    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
//  }


  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG; 
  
  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  } else {
    Serial.println("Camera Init Success");
  }
  
}

// handle routes
void handleCmd() {
  String argument = server.pathArg(0);
  
  char buf[argument.length()] = "\0";
  argument.toCharArray(buf, argument.length());
  char *token = strtok(buf, ",");
  if (token != NULL) {
    unsigned int curr_throttle_read = atoi(token+1);
    if (curr_throttle_read >= 1000 and curr_throttle_read <= 2000) {
      ws_throttle_read = curr_throttle_read;
    } 
  }
  token = strtok(NULL, ",");
  if (token != NULL) {
    unsigned int curr_steering_read = atoi(token);
    if (curr_steering_read >= 1000 and curr_steering_read <= 2000) {
      ws_steering_read = curr_steering_read;
    }
  } 
//  Serial.print(ws_throttle_read);
//  Serial.print(" ");
//  Serial.print(ws_steering_read);
//  Serial.println();
  server.send(200, "text/plain","ack");
}

void handleJpgLo()
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

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}


// Utility functions
void blinkFlashlight() {
  if (isFlashLightOn) {
    ledcWrite(FLASH_LED_PIN, 0);
    isFlashLightOn = false;
  } else {
    ledcWrite(FLASH_LED_PIN, 100);
    isFlashLightOn = true;
  }
}

void blinkRedLED() {
  if (isRedLEDOn) {
    digitalWrite(RED_LED_PIN, HIGH);
    isRedLEDOn = false;
  } else {
    digitalWrite(RED_LED_PIN, LOW);
    isRedLEDOn = true;
  }
}
