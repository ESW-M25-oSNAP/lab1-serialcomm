// Define the pin you connected the IR sensor's OUT pin to
#define IR_SENSOR_PIN 4
void setup() {
  // Start serial communication
  Serial.begin(9600);
  // Set the sensor pin as an input
  pinMode(IR_SENSOR_PIN, INPUT);
  Serial.println("ESP32 with IR Sensor is ready.");
  Serial.println("Bring an object near the sensor.");
}
void loop() {
  // Read the digital state of the sensor pin
  int obstacleState = digitalRead(IR_SENSOR_PIN);
  // --- Sensor Logic ---
  // Most IR modules output LOW (0) when an obstacle is detected
  // and HIGH (1) when the path is clear.
  // We will send the raw state (0 or 1).
  // --- Data Formatting ---
  // A simple, clear format for easy parsing in Python.
  // We will send "Status:0" or "Status:1"
  Serial.print("Status:");
  Serial.print(obstacleState);
  Serial.println(); // Use println for the newline character
  // A shorter delay makes the sensor more responsive
  delay(200);
}
