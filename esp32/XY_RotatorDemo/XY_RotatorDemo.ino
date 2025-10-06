#include <GyverStepper.h>
#include <Adafruit_NeoPixel.h>
GStepper<STEPPER2WIRE> stepEL(320000, 13, 12, 14); // steps/rev, step, dir, en
GStepper<STEPPER2WIRE> stepAZ(320000, 27, 26, 25);

#define SerialPort Serial
#define ledPin  2
#define numLeds 8
#define brightness 50

#define Xend 32
#define Yend 33

bool testMode=false;
bool parking=true;
bool autoPwr=false;

float az;
float el;
String line;
float azSet;
float elSet;
TaskHandle_t Task1;

Adafruit_NeoPixel pix(numLeds, ledPin, NEO_GRB + NEO_KHZ800);

void printAzEl() {
  SerialPort.print("AZ");
  SerialPort.print(az, 3);
  SerialPort.print(" EL");
  SerialPort.print(el, 3);
  SerialPort.print("\n");
}

void cal(){
  for(int i=0; i<numLeds; i++) {
    pix.setPixelColor(i, pix.Color(255, 0, 0));
    pix.show();
  }
  
  stepAZ.setRunMode(KEEP_SPEED);
  stepAZ.setSpeedDeg(10);
  while(digitalRead(Xend)==0 and stepEL.getCurrentDeg()<=180) {
    stepAZ.tick();
    if (stepAZ.getCurrentDeg()>180) while(1){fillStrip(255,0,0); delay(200); fillStrip(0,0,0); delay(200); vTaskDelay(1);}
  }

  stepAZ.setCurrentDeg(90.0);
  stepAZ.setRunMode(FOLLOW_POS);
  stepAZ.setTargetDeg(0,ABSOLUTE);
  while(stepAZ.tick() and !testMode) {stepAZ.tick();}
  for(int i=0; i<numLeds; i++) {
    pix.setPixelColor(i, pix.Color(255, 70, 0));
    pix.show();
  }
  
  stepEL.setRunMode(KEEP_SPEED);
  stepEL.setSpeedDeg(-10);
  while(digitalRead(Yend)==0) {
    stepEL.tick();
    if (stepEL.getCurrentDeg()<-180) while(1){fillStrip(255,0,0); delay(200); fillStrip(0,0,0); delay(200); vTaskDelay(1);}
  }

  stepEL.setCurrentDeg(-84.3);
  stepEL.setRunMode(FOLLOW_POS);
  stepEL.setTargetDeg(0,ABSOLUTE);
  while(stepEL.tick() and !testMode) {
    stepEL.tick();
  }
  for(int i=0; i<numLeds; i++) {
    pix.setPixelColor(i, pix.Color(0, 255, 0));
    pix.show();
  }
}

void fillStrip(int r, int g, int b){
  for(int i=0; i<numLeds; i++) {
    pix.setPixelColor(i, pix.Color(r, g, b));
    pix.show();
  }
}

void Task1code( void * pvParameters ){
  while(1){
    stepAZ.tick();
    stepEL.tick();
//    yield();
    vTaskDelay(1);
//    delayMicroseconds(500);
  }
}


void setup() {
  SerialPort.begin(115200);
  Serial.setTimeout(4);
  pinMode(Xend, INPUT);
  pinMode(Yend, INPUT);

  pix.begin();
  pix.clear();
  pix.setBrightness(brightness);

  stepAZ.setAcceleration(8000);
  stepEL.setAcceleration(8000);
  stepAZ.setMaxSpeed(8000);//1500
  stepEL.setMaxSpeed(8000);//1000

  cal();
  
  stepAZ.autoPower(autoPwr);
  stepEL.autoPower(autoPwr);

  xTaskCreatePinnedToCore(Task1code, "Task1", 10000, NULL, 2, NULL,  0);
  delay(500); 
}

void loop() {
  stepAZ.setTargetDeg(0,ABSOLUTE);
  stepEL.setTargetDeg(-60,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az0
  
  stepAZ.setTargetDeg(37.7,ABSOLUTE);
  stepEL.setTargetDeg(-50.7,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az45

  stepAZ.setTargetDeg(0,ABSOLUTE);
  stepEL.setTargetDeg(60,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az90

  stepAZ.setTargetDeg(37.7,ABSOLUTE);
  stepEL.setTargetDeg(50.7,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az135

  stepAZ.setTargetDeg(0,ABSOLUTE);
  stepEL.setTargetDeg(60,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az180

  stepAZ.setTargetDeg(-37.7,ABSOLUTE);
  stepEL.setTargetDeg(50.7,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az225

  stepAZ.setTargetDeg(-60,ABSOLUTE);
  stepEL.setTargetDeg(0,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az270

  stepAZ.setTargetDeg(-37.7,ABSOLUTE);
  stepEL.setTargetDeg(50.7,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az315

  stepAZ.setTargetDeg(0,ABSOLUTE);
  stepEL.setTargetDeg(-60,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az0

  stepAZ.setTargetDeg(0,ABSOLUTE);
  stepEL.setTargetDeg(70,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az 180 el 20

  stepAZ.setTargetDeg(30,ABSOLUTE);
  stepEL.setTargetDeg(0,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az 90 el 60

  stepAZ.setTargetDeg(-28.74,ABSOLUTE);
  stepEL.setTargetDeg(65.87,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az 211 el 21

  stepAZ.setTargetDeg(28.74,ABSOLUTE);
  stepEL.setTargetDeg(-65.87,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //az 31 el 21

  stepAZ.setTargetDeg(0,ABSOLUTE);
  stepEL.setTargetDeg(0,ABSOLUTE);
  while(stepAZ.tick() or stepEL.tick()) {stepAZ.tick(); stepEL.tick();} //el90
  
  delay(1000);
}
