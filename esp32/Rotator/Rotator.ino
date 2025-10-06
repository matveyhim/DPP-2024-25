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
bool parking=false;
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

  stepAZ.setCurrentDeg(95);
  stepAZ.setRunMode(FOLLOW_POS);
  stepAZ.setTargetDeg(0,ABSOLUTE);
  while(stepAZ.tick() and !testMode) {stepAZ.tick();}
  for(int i=0; i<numLeds; i++) {
    pix.setPixelColor(i, pix.Color(255, 70, 0));
    pix.show();
  }
  
  stepEL.setRunMode(KEEP_SPEED);
  stepEL.setSpeedDeg(10);
  while(digitalRead(Yend)==0) {
    stepEL.tick();
    if (stepEL.getCurrentDeg()>180) while(1){fillStrip(255,0,0); delay(200); fillStrip(0,0,0); delay(200); vTaskDelay(1);}
  }

  stepEL.setCurrentDeg(80);
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

  stepAZ.setAcceleration(9000);
  stepEL.setAcceleration(9000);
  stepAZ.setMaxSpeed(8000);//1500
  stepEL.setMaxSpeed(8000);//1000

  cal();
  
  stepAZ.autoPower(autoPwr);
  stepEL.autoPower(autoPwr);

  
  delay(500); 
}

void loop() {
//  delay(1);
  xTaskCreatePinnedToCore(Task1code, "Task1", 10000, NULL, 2, NULL,  0);
  az=stepAZ.getCurrentDeg();
  el=stepEL.getCurrentDeg();
  
  if (Serial.available()) {
    line = Serial.readString();
    String param;                                          
    int firstSpace;                                         
    int secondSpace;                                        
    
    if (line.indexOf("AZ EL")!=-1) {                        
      printAzEl();                                         
    } else if (line.startsWith("AZ")) {
      firstSpace = line.indexOf(' ');
      secondSpace = line.indexOf(' ', firstSpace + 1);
      param = line.substring(2, firstSpace);
      azSet = param.toFloat();
      param = line.substring(firstSpace + 3, secondSpace);
      elSet = param.toFloat();
    } else if (line.indexOf("calibration")!=-1) {
      cal();
    }
  }
  
  if (azSet==0.0 and elSet==0.0 and parking){
    stepAZ.disable();
    stepEL.disable();
  }else{
    stepAZ.enable();
    stepEL.enable();
  }

  stepEL.setTargetDeg(elSet,ABSOLUTE);
  stepAZ.setTargetDeg(azSet,ABSOLUTE);

  
  while(stepAZ.tick() or stepEL.tick()){
//    delay(1);
    stepAZ.tick();
    stepEL.tick();
    az=stepAZ.getCurrentDeg();
    el=stepEL.getCurrentDeg();
    
    if (Serial.available()) {
      line = Serial.readString();
      String param;                                           //Parameter value
      int firstSpace;                                         //Position of the first space in the command line
      int secondSpace;                                        //Position of the second space in the command line
      
      if (line.indexOf("AZ EL")!=-1) {                         //Query command received
        printAzEl();                                          //Send the current Azimuth and Elevation
      } else if (line.startsWith("AZ")) {                          //Position command received: Parse the line.
        firstSpace = line.indexOf(' ');                     //Get the position of the first space
        secondSpace = line.indexOf(' ', firstSpace + 1);    //Get the position of the second space
        param = line.substring(2, firstSpace);              //Get the first parameter
        azSet = param.toFloat();                            //Set the azSet value
        param = line.substring(firstSpace + 3, secondSpace);//Get the second parameter
        elSet = param.toFloat();                            //Set the elSet value
      } else if (line.indexOf("calibration")!=-1) {
      cal();
      }
    }
  }
}
