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


int analogPin = 0;
int analogPin2 = 1;
int raw = 0;
int raw2 = 0;
float Vin = 5;
float Vout = 0;
float R1 = 1000;
float RMux = 125;
float R2 = 0;
float buffer = 0;

const int channelA = 2;
const int channelB = 4;
const int channelC = 6;

const int channelA5v = 8;
const int channelB5v = 10;
const int channelC5v = 12;
const int channelA5v2 = 3;
const int channelB5v2 = 5;
const int channelC5v2 = 7;

const int num_serial = 16;     
const int num_5v = 15;
float listArray[num_serial * num_5v];
//int pressed[num_serial * 8];
int calibrate = 0;


unsigned long startTime;
unsigned long endTime;
unsigned long duration;


void setup(){
  Serial.begin(115200);
  pinMode(channelA,OUTPUT);
  pinMode(channelB,OUTPUT);
  pinMode(channelC,OUTPUT);
  digitalWrite(channelA, LOW);
  digitalWrite(channelB, LOW);
  digitalWrite(channelC, LOW);
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
  digitalWrite(channelA, A);
  digitalWrite(channelB, B);
  digitalWrite(channelC, C);
  
}

void selectChannel5v(int chnl){/* function selectChannel */ 
//// Select channel of the multiplexer 
  int A = bitRead(chnl,0); //Take first bit from binary value of i channel.
  int B = bitRead(chnl,1); //Take second bit from binary value of i channel.
  int C = bitRead(chnl,2); //Take third bit from value of i channel.
  digitalWrite(channelA5v, A);
  digitalWrite(channelB5v, B);
  digitalWrite(channelC5v, C);
  
}

void selectChannel5v2(int chnl){/* function selectChannel */ 
//// Select channel of the multiplexer 
  int A = bitRead(chnl,0); //Take first bit from binary value of i channel.
  int B = bitRead(chnl,1); //Take second bit from binary value of i channel.
  int C = bitRead(chnl,2); //Take third bit from value of i channel.
  digitalWrite(channelA5v2, A);
  digitalWrite(channelB5v2, B);
  digitalWrite(channelC5v2, C);
  
}

// void printPressed() {
//   Serial.println("These are pressed: ");

//   for (int i = 0; i < (num_serial * num_5v); i++) {
//     if (pressed[i] == 1) {
//       Serial.print(i);
//       Serial.print(" ");
//     }
//   }
//   Serial.println(" ");
// }

void MuxMaxxing(){/* function MuxLED */ 
//// blink leds 
for(int j = 0; j < num_5v; j++){
  if (j < 7) {
      selectChannel5v(j);
    } else {
      selectChannel5v(7);
      selectChannel5v2((j + 1) % 8);
    }
  // Serial.println(j);
  // delay(500);
  for(int i = 0; i <  num_serial; i++){
      
      selectChannel(i % 8);
      if (i < 8) {
        raw = analogRead(analogPin);
      } else {
        raw = analogRead(analogPin2);
      }

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
          Serial.println();
          delay(10);
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
