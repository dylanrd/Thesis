

extern unsigned int __bss_end;
extern unsigned int __heap_start;
extern void *__brkval;

int freeMemory() {
  int free_memory;
  if ((int)__brkval == 0) {
    free_memory = ((int)&free_memory) - ((int)&__bss_end);
  } else {
    free_memory = ((int)&free_memory) - ((int)__brkval);
  }
  return free_memory;
}


int analogPin = 1;
int analogPin2 = 2;
int analogPin3 = 3;
int raw = 0;
int raw2 = 0;
float Vin = 3.3;
float Vout = 0;
float R1 = 10000;
float RMux = 125;
float R2 = 0;
float buffer = 0;

const int channelA_read = 15;
const int channelB_read = 16;
const int channelC_read = 17;
const int channelD_read = 18;

const int channelA_V = 11;
const int channelB_V = 12;
const int channelC_V = 13;
const int channelD_V = 14;

const int inhibit_one = 8;
const int inhibit_two = 9;
const int inhibit_three = 10;

const int num_serial = 48;     
const int num_5v = 48;
const int total_sensors = num_serial * num_5v;
float baseline[total_sensors];  // Store baseline for each sensor
bool baseline_collected = false;
int calibrate = 0;
float threshold = 10000.0;  // Resistance change threshold (adjust as needed)


unsigned long startTime;
unsigned long endTime;
unsigned long duration;

// #define ESP32_RX 0  // RX pin for Arduino (connects to ESP32 TX)
// #define ESP32_TX 3  // TX pin for Arduino (connects to ESP32 RX, not used in this case)

// // Create SoftwareSerial instance
// SoftwareSerial espSerial(ESP32_RX, ESP32_TX);

void setup(){
  // espSerial.begin(115200);
  Serial.begin(2000000);
  pinMode(channelA_read,OUTPUT);
  pinMode(channelB_read,OUTPUT);
  pinMode(channelC_read,OUTPUT);
  pinMode(channelD_read,OUTPUT); 
  pinMode(channelA_V,OUTPUT);
  pinMode(channelB_V,OUTPUT);
  pinMode(channelC_V,OUTPUT);
  pinMode(channelD_V,OUTPUT);
  pinMode(inhibit_one, OUTPUT);
  pinMode(inhibit_two, OUTPUT);
  pinMode(inhibit_three, OUTPUT);
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
  
  // Initialize baseline array
  for(int i = 0; i < total_sensors; i++) {
    baseline[i] = 0.0;
  }
  
  Serial.println("Force Resistive Sensor Array Initialized");
  Serial.print("Total sensors: ");
  Serial.println(total_sensors);
  Serial.println("Collecting baseline... Please ensure mat is empty");
}

void loop(){
  startTime = millis();
  MuxMaxxing();
  
  // printPressed();

  //  memset(pressed, 0, sizeof(pressed));
  // int free_mem = freeMemory();
  // Serial.print("Free Memory: ");
  // Serial.println(free_mem);

  calibrate++;
  
  // Show baseline collection progress
  if (calibrate <= 10) {
    Serial.print("Baseline collection: ");
    Serial.print(calibrate);
    Serial.println("/10");
  }

  // endTime = millis();  // Record the end time
  // duration = endTime - startTime;  // Calculate the duration
  
  // Serial.print("Loop time: ");
  // Serial.print(duration);
  // Serial.println(" microseconds");
}

void selectChannel(int chnl){/* function selectChannel */ 
//// Select channel of the multiplexer 
  int A = bitRead(chnl,0); //Take first bit from binary value of i channel.
  int B = bitRead(chnl,1); //Take second bit from binary value of i channel.
  int C = bitRead(chnl,2); //Take third bit from value of i channel.
  int D = bitRead(chnl,3);
 
  digitalWrite(channelA_read, A);
  digitalWrite(channelB_read, B);
  digitalWrite(channelC_read, C);
  digitalWrite(channelD_read, D);
  // delay(5);
  
}

void selectChannel5v(int chnl){/* function selectChannel */ 
//// Select channel of the multiplexer 
  
  int A = bitRead(chnl,0); //Take first bit from binary value of i channel.
  int B = bitRead(chnl,1); //Take second bit from binary value of i channel.
  int C = bitRead(chnl,2); //Take third bit from value of i channel.
  int D = bitRead(chnl,3);
  // Serial.println(bitRead(chnl,0));
  // Serial.println(bitRead(chnl,1));
  // Serial.println(bitRead(chnl,2));
  // Serial.println(bitRead(chnl,3));
  // Serial.println("______________________________");
  digitalWrite(channelA_V, A);
  digitalWrite(channelB_V, B);
  digitalWrite(channelC_V, C);
  digitalWrite(channelD_V, D);
  // delay(5);
}

void MuxMaxxing(){/* function MuxLED */ 
//// blink leds 
String timestamp = "";

for(int j = 0; j < num_5v; j++){
  
  if (j < 16) {
    
    digitalWrite(inhibit_one, LOW);
    digitalWrite(inhibit_two, HIGH);
    digitalWrite(inhibit_three, HIGH);
  } if ((16 <= j) && (j < 32)) {
    // Serial.println("HERE");
    digitalWrite(inhibit_one, HIGH);
    digitalWrite(inhibit_two, LOW);
    digitalWrite(inhibit_three, HIGH);
  } if (j >= 32) {
    digitalWrite(inhibit_one, HIGH);
    digitalWrite(inhibit_two, HIGH);
    digitalWrite(inhibit_three, LOW);
  }
  selectChannel5v(j % 16);
  // delay(500);
  for(int i = 0; i < num_serial; i++){
      // Serial.println(((i >= 16) && i < 32));
      selectChannel(i % 16);
      if (i < 16) {
        // Serial.println("HERE");
        raw = analogRead(analogPin);
      } if ((16 <= i) && (i < 32)) {
        // Serial.println("NOt supposed to be here");
        raw = analogRead(analogPin2);
      } if (i >= 32) {
        // Serial.println("Not supporsed to be here");
        raw = analogRead(analogPin3);
      }
      
      

      int current_sensor = (j * num_serial) + i;
      // if (current_sensor == 0) {
      //   Serial.println("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa");
      // }
      // Serial.println(current_sensor);
      // Serial.println(raw);
      if(raw){
        
        Vout = (raw * Vin) / 4096.0;
        
        // Improved voltage divider calculation
        R2 = R1 * (Vin - Vout) / Vout - RMux;
        
        // Ensure non-negative resistance
        if (R2 < 0) R2 = 0;
          // if (current_sensor == 0) {
        // Always send resistance change data
        Serial.print(abs(R2));
        Serial.print(",");
        Serial.print(current_sensor);
        Serial.println();
          // }
      }
}


}
}

