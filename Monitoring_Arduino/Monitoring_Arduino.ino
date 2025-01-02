void setup()
{
  Serial.begin(9600);
}

void loop()
{
  Serial.print("setBrightINT;1;200#");
  delay(500);
  Serial.print("setBrightINT;2;250#");
  delay(500);
  Serial.print("setBrightINT;1;0#");
  delay(500);
  Serial.print("setBrightFLOAT;2;0.5#");
  delay(500);
  Serial.print("launchAnimation;separately;5000#");
  delay(6000);
  Serial.print("launchAnimation;together;3000#");
  delay(6000);
}
