int hallSensorPin = A0;
int ldrSensor Pin = A1;


int hallSensorValue = 0;
int ldrSensorValue = 0;

void setup() 
{
  Serial.begin(9600);

}

void loop() 
{ 
  hallSensorValue = analogRead(hallSensorPin);
  ldrSensorValue = analogRead(ldrSensorPin);
  Serial.print(hallSensorValue);
  Serial.print(" ")
  Serial.print(ldrSensorValue);
  Serial.println();
  delay(1000);
}