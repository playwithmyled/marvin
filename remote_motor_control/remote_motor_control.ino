
// Left wheels
#define RIGHT_WHEEL_SPEED 3
#define RIGHT_WHEEL_DIR_A 4
#define RIGHT_WHEEL_DIR_B 5
// Right wheels
#define LEFT_WHEEL_SPEED 10
#define LEFT_WHEEL_DIR_A 9
#define LEFT_WHEEL_DIR_B 8

String serialString;




String splitString(String s, char parser, int index);

// Action move.
void actionMove(int leftSpeed, int rightSpeed);

void setup() {
	
	// initialize serial communication:
	Serial.begin(115200);
  
	pinMode(RIGHT_WHEEL_SPEED, OUTPUT);
	pinMode(RIGHT_WHEEL_DIR_A, OUTPUT);
	pinMode(RIGHT_WHEEL_DIR_B, OUTPUT);
	
	pinMode(LEFT_WHEEL_SPEED, OUTPUT);
	pinMode(LEFT_WHEEL_DIR_A, OUTPUT);
	pinMode(LEFT_WHEEL_DIR_B, OUTPUT);	

	analogWrite(RIGHT_WHEEL_SPEED, 0);
	analogWrite(LEFT_WHEEL_SPEED, 0);  
}



void loop()
{
	// establish variables for duration of the ping, 
	// and the distance result in inches and centimeters:

	while(Serial.available() > 0 ) {
		delay(3);					//delay to allow buffer to fill 
		char c = Serial.read();		//gets one byte from serial buffer
		serialString += c;			//makes the string.
	}
	
	if(serialString.length() > 0 ) {
		serialString.trim();
	
		Serial.println(serialString);
		
		// Ask to read from the ping.
		if(serialString.startsWith("$MOVE")) {
			
			String action = splitString(serialString,',',0);
			String leftSpeedString = splitString(serialString,',',1);
			String rightSpeedString = splitString(serialString,',',2);

			actionMove(leftSpeedString.toInt(), rightSpeedString.toInt());
			
		}
		
		serialString = ""; // Reset serialString input.
	}
	
}

void actionMove(int leftSpeed, int rightSpeed)
{
	analogWrite(LEFT_WHEEL_SPEED, abs(leftSpeed));
	analogWrite(RIGHT_WHEEL_SPEED, abs(rightSpeed));

	if (leftSpeed > 0) {
		digitalWrite(LEFT_WHEEL_DIR_A, LOW);
		digitalWrite(LEFT_WHEEL_DIR_B, HIGH);		
	} else {
		digitalWrite(LEFT_WHEEL_DIR_A, HIGH);
		digitalWrite(LEFT_WHEEL_DIR_B, LOW);		
	}  

	if (rightSpeed > 0) {
		digitalWrite(RIGHT_WHEEL_DIR_A, LOW);
		digitalWrite(RIGHT_WHEEL_DIR_B, HIGH);
	} else {
		digitalWrite(RIGHT_WHEEL_DIR_A, HIGH);
		digitalWrite(RIGHT_WHEEL_DIR_B, LOW);		
	}
			
}





// https://github.com/despild/SplitStringExample/blob/master/SplitStringExample.ino

String splitString(String s, char parser,int index){
  String rs='\0';
  int parserIndex = index;
  int parserCnt=0;
  int rFromIndex=0, rToIndex=-1;

  while(index>=parserCnt){
    rFromIndex = rToIndex+1;
    rToIndex = s.indexOf(parser,rFromIndex);

    if(index == parserCnt){
      if(rToIndex == 0 || rToIndex == -1){
        return '\0';
      }
      return s.substring(rFromIndex,rToIndex);
    }
    else{
      parserCnt++;
    }

  }
  return rs;
}
