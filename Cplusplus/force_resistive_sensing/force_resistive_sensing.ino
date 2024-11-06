#define number_of_mux 2
// #define numOfMuxPins number_of_mux * 8
#define numOfMuxPins 9

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
int analogPin2 = 0;
int raw = 0;
int raw2 = 0;
int Vin = 5;
float Vout = 0;
float R1 = 10000;
float RMux = 125;
float R2 = 0;
float buffer = 0;

const int channelA = 2;
const int channelB = 4;
const int channelC = 6;
const int comPin  = 3;

const int channelA5v = 8;
const int channelB5v = 10;
const int channelC5v = 12;

const int num_serial = 10;     
const int num_5v = 8;
int listArray[num_serial * 8][10];
//int pressed[num_serial * 8];
int calibrate = 0;

void setup(){
  Serial.begin(9600);
  pinMode(channelA,OUTPUT);
  pinMode(channelB,OUTPUT);
  pinMode(channelC,OUTPUT);
  digitalWrite(channelA, LOW);
  digitalWrite(channelB, LOW);
  digitalWrite(channelC, LOW);
}

void loop(){

  MuxMaxxing();
  
  //printPressed();

  //memset(pressed, 0, sizeof(pressed));
  // int free_mem = freeMemory();
  // Serial.print("Free Memory: ");
  // Serial.println(free_mem);

  calibrate++;
  //Serial.println(listArray[0].get(0));
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

// void printPressed() {
//   Serial.println("These are pressed: ");

//   for (int i = 0; i < (9*8); i++) {
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
  for(int i = 0; i <  num_serial; i++){
      selectChannel5v(j % 8);
      selectChannel(i % 8);
      if (i < 8) {
        raw = analogRead(analogPin);
      } else {
        raw = analogRead(analogPin2);
      }
      // raw = analogRead(analogPin);
      // raw2 = analogRead(analogPin2);
      int current_sensor = (j * num_serial) + i;

      
      if(raw){
        
        Vout = raw * (Vin / 1023.0);
        R2= ((R1 + RMux) * (Vin - Vout))/Vout;
        // Serial.print(current_sensor);
        // Serial.print("Vout: ");
        // Serial.println(Vout);
        // Serial.print("R2: ");
       if (current_sensor == 79) {
        // Serial.println(Vout);
        Serial.println(R2);
      }
        // Serial.print(R2);
        // Serial.print(",");
        // Serial.print(current_sensor);
        // Serial.println();
        
        //delay(5);
        if (calibrate < 10) {
          listArray[current_sensor][calibrate] = (int)abs(R2);
          
        } else if (bigDrop(current_sensor, abs(R2))) {
          
          // pressed[current_sensor] = 1;
        } else {
          
          // listArray[i].remove(0);
          // listArray[i].add((int)abs(R2));
        
        }

        }
      }
}

}

bool bigDrop(int index, int current) {
  float avg = 0;
  for (int i = 0; i < 10; i++) {
    avg += abs(listArray[index][i]);
  }
  
  avg /= sizeof(listArray[index]);
  // Serial.println(abs(avg) * 0.01);
  if (abs(current) <= abs(avg) * 0.1) {
    //  Serial.println(avg * 0.01);
    // if (index == 71) {
    //   Serial.print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
    // }
    //   Serial.println(index);
    //   Serial.println(current);
    return true;
  }

  return false;
}
