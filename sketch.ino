void setup() {
pinMode(13, OUTPUT);//inital digitalpin 13 as output.
}

void loop() {
digitalWrite(13, HIGH); //turn the led on(HIGH is the voltage level)
delay(1000); //wait for a second
digitalWrite (13, LOW); //Turn the led off by making the voltage LOW
delay(1000); //wait for a second 
}
