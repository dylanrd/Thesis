#include <SoftwareSerial.h>

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

const inhibit_one = 8;
const inhibit_two = 9;
const inhibit_three = 10;

const int num_serial = 16;     
const int num_5v = 16;
float listArray[num_serial * num_5v];
//int pressed[num_serial * 8];
int calibrate = 0;


unsigned long startTime;
unsigned long endTime;
unsigned long duration;

// #define ESP32_RX 0  // RX pin for Arduino (connects to ESP32 TX)
// #define ESP32_TX 3  // TX pin for Arduino (connects to ESP32 RX, not used in this case)

// // Create SoftwareSerial instance
// SoftwareSerial espSerial(ESP32_RX, ESP32_TX);

void setup(){
  // espSerial.begin(115200);
  Serial.begin(115200);
  pinMode(channelA,OUTPUT);
  pinMode(channelB,OUTPUT);
  pinMode(channelC,OUTPUT);
  pinMode(inhibit_one, OUTPUT);
  pinMode(inhibit_two, OUTPUT);
  pinMode(inhibit_three, OUTPUT);
  digitalWrite(channelA, LOW);
  digitalWrite(channelB, LOW);
  digitalWrite(channelC, LOW);
  digitalWrite(inhibit_one, HIGH);
  digitalWrite(inhibit_two, LOW);
  digitalWrite(inhibit_two, THREE);
  
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
  //Serial.println(listArray[0].get(0));

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
  
}

void selectChannel5v(int chnl){/* function selectChannel */ 
//// Select channel of the multiplexer 
  int A = bitRead(chnl,0); //Take first bit from binary value of i channel.
  int B = bitRead(chnl,1); //Take second bit from binary value of i channel.
  int C = bitRead(chnl,2); //Take third bit from value of i channel.
  int D = bitRead(chnl,3);
  digitalWrite(channelA_V, A);
  digitalWrite(channelB_V, B);
  digitalWrite(channelC_V, C);
  digitalWrite(channelD_V, C);
  
}

void MuxMaxxing(){/* function MuxLED */ 
//// blink leds 
String timestamp = "";

for(int j = 0; j < num_5v; j++){
  
  selectChannel5v(j);
  for(int i = 0; i <  num_serial; i++){
      
      selectChannel(i);
      
      raw = analogRead(analogPin);
      

      int current_sensor = (j * num_serial) + i;

      if(raw){
        
        Vout = (raw * Vin) / 1024.0;
        
        R2= (R1 + RMux) * ((Vin/Vout) - 1);
        // Serial.print(current_sensor);
        // Serial.print("Vout: ");
        //Serial.println(Vout);
        // Serial.print("R2: ");
      //   if (current_sensor == 1 || current_sensor == 15) {
      //    Serial.println(Vout);
      //    Serial.println(R2);
      //    delay(500);
      //  }

      //  if (i < 8) {
      //    // Serial.println(Vout);
      //    Serial.println((R1 + RMux) * (Vout/(Vin - Vout)));
      //  }
        // Serial.print(R2);
        // Serial.print(",");
        // Serial.print(current_sensor);
        // Serial.println();
        
        //delay(5);
        if (calibrate < 10) {

          listArray[current_sensor] += (R2);
          //  Serial.println(R2);
          //  Serial.println(listArray[current_sensor]);
        } else if (calibrate == 10) {
          listArray[current_sensor] /= 10;
          // Serial.println(listArray[current_sensor]);
        } else {
          
          Serial.print(R2);
          Serial.print(",");
          Serial.print(current_sensor);
          Serial.print(",");
          Serial.print(timestamp);
          Serial.println();
          //delay(10);
          //bigDrop(current_sensor, abs(R2));
        }

        
        // else if (bigDrop(current_sensor, abs(R2))) {
          
        //   //pressed[current_sensor] = 1;
        // } else {
          
        //   // listArray[i].remove(0);
        //   // listArray[i].add((int)abs(R2));
        
        // }

        // }
      }
}


}
}

bool bigDrop(int index, float current) {
  
  // Serial.println(abs(avg) * 0.01);
  if (abs(current) <= abs(listArray[index]) * 0.3) {
    //Serial.println("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
    Serial.print(current);
    Serial.print(",");
    Serial.print(index);
    Serial.println();
    return true;
  }

  Serial.print(abs(listArray[index]));
  Serial.print(",");
  Serial.print(index);
  Serial.println();
  return false;
}
