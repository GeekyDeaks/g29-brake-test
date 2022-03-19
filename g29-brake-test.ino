
#include <Wire.h>     //Include the Wire library to talk I2C
#define DAC_CMD_LEN 3

int byte_count = 0;
unsigned char dac_buffer[DAC_CMD_LEN];

//This is the I2C Address of the MCP4725, by default (A0 pulled to GND).
//Please note that this breakout is for the MCP4725A0. 
#define MCP4725_ADDR 0x60

unsigned long startMillis;  //some global variables available anywhere in the program
unsigned long currentMillis;
const unsigned long period = 5000;  //the value is a number of milliseconds

void setup () {
  Serial.begin (115200);
  Wire.begin();
  startMillis = millis();  //initial start time
} // end of setup

void update_dac(int data) {

  dac_buffer[byte_count] = data & 0xff;
  byte_count += 1;
  if(byte_count < DAC_CMD_LEN) {
    return;
  }

  Serial.print("DAC CMD:");
  Wire.beginTransmission(MCP4725_ADDR);
  for(int i = 0; i < byte_count; i++) {
      Wire.write(dac_buffer[i]);
      Serial.print(" 0x");
      Serial.print(dac_buffer[i], HEX);
  }
  Wire.endTransmission();
  
  Serial.println(" END");
  byte_count = 0;
}

void loop()
{
  // if serial data available, process it
  if(Serial.available()) {
    update_dac(Serial.read()); 
  }
  currentMillis = millis();  //get the current "time" (actually the number of milliseconds since the program started)
  if (currentMillis - startMillis >= period)  //test whether the period has elapsed
  {
    Serial.print("ALIVE: ");
    Serial.println(byte_count);
    startMillis = currentMillis;
  }

}  // end of loop
