// Regular Arduino libraries - no FastGPIO needed
#include <SPI.h>

// Pin definitions based on force resistive sensing code
const int analogPin1 = 0;  // Primary analog input
const int analogPin2 = 1;  // Secondary analog input  
const int analogPin3 = 2;  // Tertiary analog input

// Multiplexer control pins (based on force resistive sensing)
const int channelA_read = 15;  // Multiplexer A control
const int channelB_read = 16;  // Multiplexer B control
const int channelC_read = 17;  // Multiplexer C control
const int channelD_read = 18;  // Multiplexer D control

const int channelA_V = 11;     // Voltage multiplexer A
const int channelB_V = 12;     // Voltage multiplexer B
const int channelC_V = 13;     // Voltage multiplexer C
const int channelD_V = 14;     // Voltage multiplexer D

const int inhibit_one = 8;     // Inhibit control 1
const int inhibit_two = 9;     // Inhibit control 2
const int inhibit_three = 10;  // Inhibit control 3

// Column multiplexer control pins (3 multiplexers for 48 columns)
// Using pins 2-7 for column multiplexers (avoiding conflicts with existing pins)
const int colMux1_A = 2;  // Column multiplexer 1 control A
const int colMux1_B = 3;  // Column multiplexer 1 control B  
const int colMux1_C = 4;  // Column multiplexer 1 control C
const int colMux1_D = 5;  // Column multiplexer 1 control D

const int colMux2_A = 6;  // Column multiplexer 2 control A
const int colMux2_B = 7;  // Column multiplexer 2 control B
const int colMux2_C = 19; // Column multiplexer 2 control C (using available pin)
const int colMux2_D = 20; // Column multiplexer 2 control D (using available pin)

const int colMux3_A = 21; // Column multiplexer 3 control A (using available pin)
const int colMux3_B = 22; // Column multiplexer 3 control B (using available pin)
const int colMux3_C = 23; // Column multiplexer 3 control C (using available pin)
const int colMux3_D = 24; // Column multiplexer 3 control D (using available pin)

// Matrix dimensions
const int num_serial = 32;     // Number of serial sensors
const int num_5v = 48;         // Number of 5V sensors
const int total_sensors = num_serial * num_5v;

int inputVal = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(500000);
  delay(100);
  
  // Setup analog input pins
  pinMode(analogPin1, INPUT);
  pinMode(analogPin2, INPUT);
  pinMode(analogPin3, INPUT);
  
  // Setup multiplexer control pins
  pinMode(channelA_read, OUTPUT);
  pinMode(channelB_read, OUTPUT);
  pinMode(channelC_read, OUTPUT);
  pinMode(channelD_read, OUTPUT);
  pinMode(channelA_V, OUTPUT);
  pinMode(channelB_V, OUTPUT);
  pinMode(channelC_V, OUTPUT);
  pinMode(channelD_V, OUTPUT);
  
  // Setup inhibit control pins
  pinMode(inhibit_one, OUTPUT);
  pinMode(inhibit_two, OUTPUT);
  pinMode(inhibit_three, OUTPUT);
  
  // Setup column multiplexer control pins
  pinMode(colMux1_A, OUTPUT);
  pinMode(colMux1_B, OUTPUT);
  pinMode(colMux1_C, OUTPUT);
  pinMode(colMux1_D, OUTPUT);
  pinMode(colMux2_A, OUTPUT);
  pinMode(colMux2_B, OUTPUT);
  pinMode(colMux2_C, OUTPUT);
  pinMode(colMux2_D, OUTPUT);
  pinMode(colMux3_A, OUTPUT);
  pinMode(colMux3_B, OUTPUT);
  pinMode(colMux3_C, OUTPUT);
  pinMode(colMux3_D, OUTPUT);
  
  // Initialize all pins to default states
  digitalWrite(channelA_read, LOW);
  digitalWrite(channelB_read, LOW);
  digitalWrite(channelC_read, LOW);
  digitalWrite(channelD_read, LOW);
  digitalWrite(channelA_V, LOW);
  digitalWrite(channelB_V, LOW);
  digitalWrite(channelC_V, LOW);
  digitalWrite(channelD_V, LOW);
  digitalWrite(inhibit_one, LOW);
  digitalWrite(inhibit_two, HIGH);
  digitalWrite(inhibit_three, HIGH);
  
  // Initialize column multiplexer pins to default states
  digitalWrite(colMux1_A, LOW);
  digitalWrite(colMux1_B, LOW);
  digitalWrite(colMux1_C, LOW);
  digitalWrite(colMux1_D, LOW);
  digitalWrite(colMux2_A, LOW);
  digitalWrite(colMux2_B, LOW);
  digitalWrite(colMux2_C, LOW);
  digitalWrite(colMux2_D, LOW);
  digitalWrite(colMux3_A, LOW);
  digitalWrite(colMux3_B, LOW);
  digitalWrite(colMux3_C, LOW);
  digitalWrite(colMux3_D, LOW);
  
  Serial.write(0); // 0 indicates start of new frame
}

void loop() {
  // Scan through all sensors in the matrix
  for (int row = 0; row < num_5v; row++) {
    // Select the appropriate inhibit line based on row
    if (row < 16) {
      digitalWrite(inhibit_one, LOW);
      digitalWrite(inhibit_two, HIGH);
      digitalWrite(inhibit_three, HIGH);
    } else if (row < 32) {
      digitalWrite(inhibit_one, HIGH);
      digitalWrite(inhibit_two, LOW);
      digitalWrite(inhibit_three, HIGH);
    } else {
      digitalWrite(inhibit_one, HIGH);
      digitalWrite(inhibit_two, HIGH);
      digitalWrite(inhibit_three, LOW);
    }
    
    // Select the voltage multiplexer channel
    selectChannel5v(row % 16);
    
    // Scan through columns using column multiplexers
    for (int col = 0; col < num_serial; col++) {
      // Select the read multiplexer channel
      selectChannel(col % 16);
      
      // Select the column multiplexer channel
      selectColumnMux(col);
      
      // Read the sensor value
      inputVal = readMux(col);
      
      // Map the 10-bit ADC value to 8-bit for serial transmission
      byte mappedValue = map(inputVal, 0, 1023, 0, 255);
      Serial.write(mappedValue);
    }
  }
  Serial.write(0); // Mark the beginning of the next frame
}

// Function to select read multiplexer channel
void selectChannel(int chnl) {
  int A = bitRead(chnl, 0); // Take first bit from binary value of channel
  int B = bitRead(chnl, 1); // Take second bit from binary value of channel
  int C = bitRead(chnl, 2); // Take third bit from binary value of channel
  int D = bitRead(chnl, 3); // Take fourth bit from binary value of channel

  digitalWrite(channelA_read, A);
  digitalWrite(channelB_read, B);
  digitalWrite(channelC_read, C);
  digitalWrite(channelD_read, D);
}

// Function to select voltage multiplexer channel
void selectChannel5v(int chnl) {
  int A = bitRead(chnl, 0); // Take first bit from binary value of channel
  int B = bitRead(chnl, 1); // Take second bit from binary value of channel
  int C = bitRead(chnl, 2); // Take third bit from binary value of channel
  int D = bitRead(chnl, 3); // Take fourth bit from binary value of channel

  digitalWrite(channelA_V, A);
  digitalWrite(channelB_V, B);
  digitalWrite(channelC_V, C);
  digitalWrite(channelD_V, D);
}

// Function to select column multiplexer channel
void selectColumnMux(int col) {
  int channel = col % 16; // Each multiplexer handles 16 channels
  
  int A = bitRead(channel, 0);
  int B = bitRead(channel, 1);
  int C = bitRead(channel, 2);
  int D = bitRead(channel, 3);
  
  // Determine which multiplexer to use (0-15, 16-31, 32-47)
  if (col < 16) {
    // Use multiplexer 1
    digitalWrite(colMux1_A, A);
    digitalWrite(colMux1_B, B);
    digitalWrite(colMux1_C, C);
    digitalWrite(colMux1_D, D);
    // Disable other multiplexers
    digitalWrite(colMux2_A, LOW);
    digitalWrite(colMux2_B, LOW);
    digitalWrite(colMux2_C, LOW);
    digitalWrite(colMux2_D, LOW);
    digitalWrite(colMux3_A, LOW);
    digitalWrite(colMux3_B, LOW);
    digitalWrite(colMux3_C, LOW);
    digitalWrite(colMux3_D, LOW);
  } else if (col < 32) {
    // Use multiplexer 2
    digitalWrite(colMux2_A, A);
    digitalWrite(colMux2_B, B);
    digitalWrite(colMux2_C, C);
    digitalWrite(colMux2_D, D);
    // Disable other multiplexers
    digitalWrite(colMux1_A, LOW);
    digitalWrite(colMux1_B, LOW);
    digitalWrite(colMux1_C, LOW);
    digitalWrite(colMux1_D, LOW);
    digitalWrite(colMux3_A, LOW);
    digitalWrite(colMux3_B, LOW);
    digitalWrite(colMux3_C, LOW);
    digitalWrite(colMux3_D, LOW);
  } else {
    // Use multiplexer 3
    digitalWrite(colMux3_A, A);
    digitalWrite(colMux3_B, B);
    digitalWrite(colMux3_C, C);
    digitalWrite(colMux3_D, D);
    // Disable other multiplexers
    digitalWrite(colMux1_A, LOW);
    digitalWrite(colMux1_B, LOW);
    digitalWrite(colMux1_C, LOW);
    digitalWrite(colMux1_D, LOW);
    digitalWrite(colMux2_A, LOW);
    digitalWrite(colMux2_B, LOW);
    digitalWrite(colMux2_C, LOW);
    digitalWrite(colMux2_D, LOW);
  }
}

// Function to read sensor value using regular Arduino analogRead
int readMux(int col) {
  // Select appropriate analog pin based on column
  if (col < 16) {
    return analogRead(analogPin1);
  } else if (col < 32) {
    return analogRead(analogPin2);
  } else {
    return analogRead(analogPin3);
  }
}
