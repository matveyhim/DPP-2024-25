void setup() {
  Serial.begin(9600);
  Serial.setTimeout(10);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
}

void loop() { 
  String line, frstparam, secparam, thrdparam;
  int Idot, IIdot, sharp;
  
 if (Serial.available()) {  
    line = Serial.readString();
    Idot = line.indexOf(';');
    IIdot = line.indexOf(';', Idot+1);
    sharp = line.indexOf('#', IIdot+1);
    
    frstparam = line.substring(0, Idot);
    secparam = line.substring(Idot+1, IIdot);
    thrdparam = line.substring(IIdot+1, sharp);
    Serial.println(frstparam+" "+secparam+" "+thrdparam);

    if(frstparam=="setBrightINT"){
      analogWrite(secparam.toInt()+4, thrdparam.toInt());
    }
    if(frstparam=="setBrightFLOAT"){
      analogWrite(secparam.toInt()+4, thrdparam.toFloat()*255);
    }
    if(frstparam=="launchAnimation"){
      uint32_t starttime=millis();
      if(secparam=="together"){
        while(millis()-starttime <= thrdparam.toInt()){
          digitalWrite(5,HIGH);
          digitalWrite(6,HIGH);
          delay(100);
          digitalWrite(5,LOW);
          digitalWrite(6,LOW);
          delay(100);
        }
        digitalWrite(5,LOW);
        digitalWrite(6,LOW);
      }
      if(secparam=="separately"){
        while(millis()-starttime <= thrdparam.toInt()){
          digitalWrite(5,LOW);
          digitalWrite(6,HIGH);
          delay(100);
          digitalWrite(5,HIGH);
          digitalWrite(6,LOW);
          delay(100);
        }
        digitalWrite(5,LOW);
        digitalWrite(6,LOW);
      }
    }
  }
}
