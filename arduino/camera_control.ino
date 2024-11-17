// Arduino Code
#include <Servo.h>

// Pin definitions
const int IR_PIN = 7;
const int RELAY_PIN = 2;
const int JOYSTICK_X = A0;
const int JOYSTICK_Y = A5;
const int JOYSTICK_SW = 8;
const int SERVO_PIN = 12;

Servo myservo;
bool relayState = false;

void setup() {
  Serial.begin(9600);
  pinMode(IR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(JOYSTICK_SW, INPUT_PULLUP);
  myservo.attach(SERVO_PIN);
  myservo.write(0);  // Initial position
}

void loop() {
  // Read sensor values
  int irValue = digitalRead(IR_PIN);
  int joystickX = analogRead(JOYSTICK_X);
  int buttonState = digitalRead(JOYSTICK_SW);
  
  // Create data string to send to Python
  String dataString = String(irValue) + "," + 
                     String(joystickX) + "," + 
                     String(buttonState);
  
  // Send data to Python
  Serial.println(dataString);
  
  // Check for commands from Python
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'R') {  // Relay command
      relayState = !relayState;
      digitalWrite(RELAY_PIN, relayState);
    }
    else if (command == 'S') {  // Servo command
      myservo.write(90);
    }
    else if (command == 'Z') {  // Reset servo
      myservo.write(0);
    }
  }
  
  delay(100);  // Small delay to prevent serial buffer overflow
}