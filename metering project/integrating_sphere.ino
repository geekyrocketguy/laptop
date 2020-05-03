/*
Instructions for the user:
Connect the Arduino to the computer. 
Select Tools > Board > Arduino Duemilanove or Diecimila
Select Tools > Port > whatever port the Arduino is on (4 for me now)
Select Tools > Serial Monitor
This pulls up the command line interface to talk to the Arduino.

Allowable commands (no quotes):
"bright" - illuminates the Arduino at max brightness (calibrated to 0 EV). Equivalent to "n=0".
"focus" - Equivalent to a half-press of the shutter. Useful for testing camera connection.
"photo" or "trigger" - takes a photo. Useful for testing camera connection.
"step" - takes 11 photos, starting with the LEDs on 100% of the time and ending with them on 
  0.1% of the time, for 11 stops of dynamic range. This collects the dataset. In this mode only,
  you can press the pushbutton and skip ahead to the next brightness level. Do this when the
  camera has finished its exposure and you don't want to wait the ~37 seconds for the next one.
"n=x" where x is the number of stops of dimming from 0 EV. "n=0" is equivalent to the command
  "bright". "n=10" is EV-10. In theory you could use non-integers here (e.g. "n=1.333") but I 
  haven't tested this. This is useful if you want to test a particular brightness level and
  don't want to take 11 photos. Note that this does not trigger the camera. If you want that,
  you need to hit the shutter button yourself.
"dark" will make the sphere dark.
"quit" or "abort" to stop the current command. In "step", it will quit after the exposure
  has ended. After sending this command, hit the pushbutton to stop immediately.
"help" will print this documentation.

Capitalization doesn't matter. "BRIGHT" is the same as "bright" is the same as "BrIgHt".
Note that only one command operates at a time. If you do "n=3" and then "photo", the sphere
will go dark before taking the photo. 
 */

double p = 1./240.*1e6;//4166.7; //microseconds, 240 Hz
byte shutter=11; //the camera is triggered by digital pin 11
byte focus=10; //the camera focus is triggered by digital pin 10
byte led=12; //the led is triggered by digital pin 12
byte button=2; //the pushbutton switch
String str="bright"; //the given command, default to "bright" so the sphere illuminates automatically
float dimming=0;
volatile unsigned long t0;
int t1;
int t2;
bool statusprinted=false;

//1.774 kohms between center and left pins of variable resistor for 0EV LED brightness as of 04/23/2020.

//The setup function runs once when you press the reset button or first connect the board
void setup() {
  // initialize digital pin for LEDs and camera as output.
  pinMode(led, OUTPUT);
  pinMode(focus, OUTPUT);
  pinMode(shutter, OUTPUT);
  
  Serial.begin(9600); //Enable talking to computer
}


// the loop function runs over and over again forever
void loop() {
  if(Serial.available() > 0 ){
    str = Serial.readString();
    //Serial.println(str);
    str.toLowerCase();
    //Serial.println(str.length());
    
    statusprinted=false;
  }

  if (str.startsWith("bright")) {
    unsigned long t0 = millis();
    pwm(led, 1e6, 0, 1e3);
    
    if (!statusprinted) {
      Serial.println("LED set to max brightness (EV0).");
      statusprinted=true;
    }
  }

  else if ((str.startsWith("photo")) || (str.startsWith("trigger"))) {
    digitalWrite(focus, HIGH);
    delay(1000);
    digitalWrite(shutter, HIGH);
    delay(0.3e3);
    digitalWrite(shutter, LOW);
    digitalWrite(focus, LOW);
    Serial.println("Took a photo.");
    str = "";
  }

  
  else if (str.startsWith("focus")) {
    digitalWrite(focus, HIGH);
    delay(1000);
    digitalWrite(focus, LOW);
    Serial.println("Triggered focus.");
    str = "";
  }

  else if (str.startsWith("step")) {
    Serial.print("Collecting frame ");
    Serial.print(int(round(dimming+1)));
    Serial.print(" of 11...");

    t1 = int(round(p/pow(2, dimming))); //on time
    t2 = int(round(p*(1. - 1./pow(2, dimming)))); //off time
    if ((dimming > 4) && (dimming <=6)) { //make correction so dimming is right
      t1 -= 2;
      t2 += 2;
    } else if (dimming > 6) { //make correction so dimming is right
      t1 -= 2; //was 3 before?
      t2 += 2; //was 3 before?
    }

    pwm(led, t1, t2, 3e3); //illuminate for 4 seconds so metering gets comfortable
    digitalWrite(focus, HIGH); //trigger focus so camera quits menus
    pwm(led, t1, t2, 1e3); //wait 1s
    digitalWrite(shutter, HIGH); //trigger camera
    pwm(led, t1, t2, 0.3e3); //wait 0.1s
    digitalWrite(shutter, LOW); //stop triggering camera
    digitalWrite(focus, LOW); //stop triggering camera
    attachInterrupt(digitalPinToInterrupt(button), myinterrupt, RISING); //enable pushbutton
    pwm(led, t1, t2, 33e3); //wait 33s for exposure to end
    detachInterrupt(digitalPinToInterrupt(button)); //disable pushbutton
    
    Serial.println(" Done.");
    
    dimming += 1; //one stop dimmer next time

    if (dimming>10) {
      Serial.println("Done!");
      str="";
    }
  }

  else if (str.startsWith("n=")) {
    dimming = str.substring(str.indexOf("=")+1, str.indexOf("\n")).toFloat();

    if (dimming < 0) {
      Serial.println("Please enter a positive number.");
      str="";
      
    } else if (dimming > 10) {
      Serial.println("Maximum allowable value is 10.");
      str="";
      
    } else {
      t1 = int(round(p/pow(2, dimming))); //on time
      t2 = int(round(p*(1. - 1./pow(2, dimming)))); //off time
      if ((dimming > 4) && (dimming <=6)) { //make correction so dimming is right
        t1 -= 2;
        t2 += 2;
      } else if (dimming > 6) { //make correction so dimming is right
        t1 -= 2; //was 3 before?
        t2 += 2; //was 3 before?
      }
      
      pwm(led, t1, t2, 1e3); //illuminate for a second at the specified power
  
      if (!statusprinted) {
        Serial.println("Set brightness.");
        statusprinted=true;
      }
    }
  }

  else if (str.startsWith("help")) {
    Serial.print(F("Allowable commands (no quotes):\n"
"\"bright\" - illuminates the Arduino at max brightness (calibrated to 0 EV). Equivalent to \"n=0\".\n"
"\"focus\" - Equivalent to a half-press of the shutter. Useful for testing camera connection.\n"
"\"photo\" or \"trigger\" - takes a photo. Useful for testing camera connection.\n"
"\"step\" - takes 11 photos, starting with the LEDs on 100% of the time and ending with them on \n"
"  0.1% of the time, for 11 stops of dynamic range. This collects the dataset. In this mode only,\n"
"  you can press the pushbutton and skip ahead to the next brightness level. Do this when the\n"
"  camera has finished its exposure and you don't want to wait the ~37 seconds for the next one.\n"
"\"n=x\" where x is the number of stops of dimming from 0 EV. \"n=0\" is equivalent to the command\n"
"  \"bright\". \"n=10\" is EV-10. In theory you could use non-integers here (e.g. \"n=1.333\") but I \n"
"  haven't tested this. This is useful if you want to test a particular brightness level and\n"
"  don't want to take 11 photos. Note that this does not trigger the camera. If you want that,\n"
"  you need to hit the shutter button yourself.\n"
"\"dark\" will make the sphere dark.\n"
"\"quit\" or \"abort\" to stop the current command. In \"step\", it will quit after the exposure\n"
"  has ended. After sending this command, hit the pushbutton to stop immediately.\n"
"\"help\" will print this documentation.\n\n"

"Capitalization doesn't matter. \"BRIGHT\" is the same as \"bright\" is the same as \"BrIgHt\".\n"
"Note that only one command operates at a time. If you do \"n=3\" and then \"photo\", the sphere\n"
"will go dark before taking the photo."));

  str = "";
  
  }

  else {
    if (!statusprinted) {
      Serial.println("LED turned off, now doing nothing.");
      statusprinted=true;
    }
  }

}

void pwm(byte pin, int t1, int t2, unsigned long duration) {
  //pin = pin to pwm
  //t1 = duration LED is on [us]
  //t2 = duration LED is off [us]
  //duration = how long this code operates before returning [ms]

  t0 = millis();
  while(millis() - t0 < duration) {
    digitalWrite(pin, HIGH);   // turn the LED on 
    delayMicroseconds(t1);  // wait for a fraction of a period
    digitalWrite(pin, LOW);    // turn the LED off by making the voltage LOW
    delayMicroseconds(t2);   
  }
}


void myinterrupt() { //pushbutton switch to skip to the next exposure
  if (digitalRead(button)) { //debounce
    if (digitalRead(button)) { //debounce more
      Serial.println("Skipping to next step.");
      t0 = 0;
    }
  }  
}
