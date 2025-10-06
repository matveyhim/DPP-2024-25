void setup()
{
  Serial.begin(9600);
}

void loop(){
  int frst = analogRead(A0);
  int scnd = analogRead(A1);
  
  if(frst<900 or scnd<900){
    Serial.print("launchAnimation;separately;100#");
  }else if(frst>900 and scnd>900){
    Serial.print("launchAnimation;together;1000#");
  }else{
    Serial.print("setBrightINT;1;250#");
    Serial.print("setBrightINT;2;250#");
  }
//  Serial.println(String(frst)+" "+String(scnd)+" 900");
  delay(100); 
}
