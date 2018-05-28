// **** INCLUDES *****
#include "LowPower.h"
#include <SoftwareSerial.h>

//LoRa Serial
SoftwareSerial Serial1(7, 6); // RX, TX

const char deviceID[10] = "25046A";
#define Seconds 30
#define LoRa_VDD 15
#define Sensor_VDD 4

// sensor pins numbers
const int trigPin = 10;
const int echoPin = 9;

// sensor variables
uint16_t distance_to_send = 0;

//batteryLevel
int batteryLevel = 0;

void systemInit() {
  //Sensor Init
  pinMode(Sensor_VDD, OUTPUT);
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input

  //LoRa Init
  pinMode(LoRa_VDD, OUTPUT);
  Serial1.begin(57600);

}
void setup()
{
  // No setup is required for this library
  Serial.begin(9600);

  systemInit();
  loraReset();
  //Calibation of the distance
  distance_to_send = distance_calibrated();
}

int sleepCount = 0;

void loop()
{
  sleepCount++;
  if (sleepCount >= (Seconds / 8)) {
    sleepCount = 0;
    distance_to_send = distance_calibrated();
    lora_send();
  }
  // Enter power down state for 8 s with ADC and BOD module disabled
  LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
}

void loraReset()
{
  digitalWrite(LoRa_VDD, LOW);
  delay(250);
  digitalWrite(LoRa_VDD, HIGH);
  delay(250);
}

uint8_t obtain_distance() {
  long duration = 0;
  int distance = 0;
  // Clears the trigPin
  digitalWrite(Sensor_VDD, HIGH);
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);

  // Calculating the distance
  distance = duration * 0.034 / 2;

  // Prints the distance on the Serial Monitor
  //  Serial.print("Distance: ");
  //  Serial.println(distance);
  return distance;
}

uint8_t distance_calibrated() {
  int i = 0;
  int newDistance = 0;
  int oldDistance = 0;
  int oldFlag = 0;
  int newFlag = 0;
  for (i = 0; i <= 20 ; i++) {
    newDistance = obtain_distance();
    if ((oldDistance - 5) > newDistance > (oldDistance + 5)) {
      Serial.println("Old Distance");
      oldFlag++;
      newFlag = 0;
      if (oldFlag >= 2) {
        oldDistance = newDistance;
      }
    }
    else if ((oldDistance - 5) < newDistance < (oldDistance + 5)) {
      newFlag++;
      oldFlag = 0;
      if (newFlag >= 3) {
        Serial.println(" ");
        Serial.print("Parsed Distance: ");
        Serial.println(newDistance);
        Serial.print("Battery Level: ");
        batteryLevel = map(analogRead(A0), 0, 925, 0, 100);
        Serial.println(batteryLevel);
        Serial.println(" ");
        delay(250);
        return newDistance;
      }
    }
  }
}

void lora_send() {
  char loraBuffer[100];
  loraReset();
  Serial1.println("mac pause");
  while (!Serial1.available() ) {
    delay(100);
  }
  while (Serial1.available())
    Serial.write(Serial1.read());

  delay(500);

  sprintf(loraBuffer, "radio tx %s2C%04X2C%02X", deviceID, distance_to_send, batteryLevel);
  Serial1.println(loraBuffer);
  while (!Serial1.available() ) {
    delay(100);
  }
  while (Serial1.available())
    Serial.write(Serial1.read());

  delay(3000);
}

