/*************************
   Adri/Ardu-Scope
   Written and tested by Adrian Keating (C) 2021
   adrian.keating at uwa.edu.au
   High speed sampling from the Arudino
   Version 0.1.0
*/
// key learning ISR(ADC_vect) must disable interrupt  ADCSRA &= ~(1 << ADIE); // disable interuppts when 
// inclusion of & (N-1) in data[numSamples & (N-1)] = ADCH; is essetial to sto pscrashes which suggests N is getting outside of valid range

//#define FILLARRAY(a,n) a[0]=n, memcpy( ((int*)a)+sizeof(a[0]), a, sizeof(a)-sizeof(a[0]) );
// see http://yaab-arduino.blogspot.com/2015/02/fast-sampling-from-analog-input.html
#define baudrate 115200U  //19200 57600  
#define Nmax 1024U  // must be power of 2 - DO not exceed maximum MEMORY or ERRORS OCCUR
#define Buffer 32 // allow the data array extra space for additional ISR over-run calls
//#define N 64  // must be power of 2 - DO not exceed maximum MEMORY or ERRORS OCCUR

/*
Prescale  ADPS2,1,0  Clock MHz)  Sampling rate (KHz)
  2     0 0 1   8     615
  4     0 1 0   4     307
  8     0 1 1   2     153
  16    1 0 0   1     76.8
  32    1 0 1   0.5     38.4 <
  64    1 1 0   0.25    19.2
  128     1 1 1   0.125     9.6 (default)
*/

const int f[8]={615,307,153,77,38,19,10}; //255+65,0,255+66,0,3,4,5,6,7,8};
byte Nbits=8U;   // must be power of 2
boolean Verbose;
boolean OutputAscii;
boolean togglebit=true;
byte togglelength=0;
//unsigned long TIME0;
boolean logdataflag = false;
boolean allowkeypress=true;
byte tempADCSRA;
byte tempADCSRB;
byte Fmode=3;
byte Channel=1;
int triggerdelay =0;
byte SampleRepeats=0;
byte iSampleRepeats=1;

long time0;
long t;

//float xx;

//int N=Nmax;
volatile unsigned int numSamples=0;
volatile byte shift=0;
volatile byte carry=0;
volatile byte shiftval=0;

unsigned int N=Nmax;
volatile byte subsampleCount=0;
byte subsample=0;
volatile byte data[Nmax+Buffer];
// NOTe N*Nbits/8 MUST be an integer
//volatile int data2[16]={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16};
//volatile int data2[N]={321,321,321,321,321,321,321,321,321,321,321,321,321,321,321,321}; //255+65,0,255+66,0,3,4,5,6,7,8};
//volatile int data2[10]={321,322,323,324,325,326,327,328,329,330}; //255+65,0,255+66,0,3,4,5,6,7,8};
// defines pins numbers
const int trigPin = 4;  //D4
const int testPin = 7;  //D7
//const int echoPin = 3;  //D3
//float fs;
//float dt;


//      volatile int NumBytesAvaiable;
 // volatile int NextByte;
//  volatile long ValidNumber = 0;

  
//FILLARRAY(myx,1345);
void setup()
{
  //Serial.flush();  // remove anything left after uploading from IDE or other processes
  //Serial.begin(9600);
  //Serial.flush();  // remove anything left after uploading from IDE or other processes
  Serial.begin(baudrate); //57600  115200
  Serial.flush();  // remove anything left
  //delay(300);
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(testPin, OUTPUT); // Sets the trigPin as an Output
  Verbose = false;
  OutputAscii=false;
  tempADCSRA = ADCSRA;             // store ADCSRA register
  tempADCSRB = ADCSRB;             // store ADCSRB register
  //Serial.flush();  // remove anything left
  //delayMicroseconds(12*(1000000/baudrate));  // must wait this amount of time after a flush
  //pinMode(LED_BUILTIN, OUTPUT);
  //splash();
  //pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  //zerodata();
  //memset(data,0,sizeof(data));
  //configISR();
  //xx=0;
  //trigger();
  //time0 = micros();
  //startcapture();
}


ISR(ADC_vect,ISR_BLOCK)
{
  // see here for mthod to read 10bits fast analogVal = ADCL | (ADCH << 8);
  // http://www.glennsweeney.com/tutorials/interrupt-driven-analog-conversion-with-an-atmega328p
  // share ISR here 
  // https://atadiat.com/en/e-arduino-trick-share-interrupt-service-routines-between-libraries-application/
  // CLEAR EXPLANATION of ISR and blocking, https://busylog.net/arduino-timer-interrupt-isr-example/
    //ADCSRA &= ~(1 << ADIE); // disable interuppts when 
    //*(data + numSamples++)  = ADCH;  // read 8 bit value from ADC  The bit mask ensures NO data exceeds the array length
    //numSamples++; //=(numSamples)+1;
    
    if(subsample==0) {
    // do this fast grab
    data[numSamples ] = ADCH;  // read 8 bit value from ADC  The bit mask ensures NO data exceeds the array length
    numSamples++; //=(numSamples)+1;
    }else{
      ADCSRA &= ~(1 << ADIE); // disable interuppts when  on slow samples
      subsampleCount++;
      if(subsampleCount%(subsample)==0) {
          

        int scale;
        int rshiftval;
        int shiftedcarry;
        byte out;
        // ADLAR is left adjusted so the datasheet staes
        //ADCL must be read first, then ADCH, to ensure that the content of the data registers belongs to the same conversion
         int analogVal = (ADCL >> 6);
         analogVal |= ADCH<<2 ;
        scale= (int) (2 <<(8-shift))/2; // scale is base don last value of shift
        shiftedcarry=(int)(carry*scale);  // use the previous carry value
        shift=(byte) ((shift+(10-8)) % 10) ;  // Nbits of at least  bits
        shiftval=(byte) (shiftval % 10)+(10-8) ;  // Nbits of at least  bits
        rshiftval=(byte)(analogVal>>shiftval);
        carry= (byte) (analogVal % ((int) (2<<shift)/2) ); //      
        out=(byte) shiftedcarry+rshiftval;
        data[numSamples ] = out;
        numSamples++; //=(numSamples)+1;
         if ((byte) ((shift+(10-8)) % 10) == 0){
          // check if the next shit =0
          //set to zero
          shift=0; //(Nbits-8);
          shiftval=shift;
          //scale= (int) (2 <<(8-shift))/2; // scale is base don last value of shift
          //shiftedcarry=(int)(carry*scale);  // use the previous carry value
          data[numSamples ] =carry;
          numSamples++; //=(numSamples)+1;
        carry=0; // reset carry
        }
        
          //data[numSamples ] = ADCH;  // read 8 bit value from ADC  The bit mask ensures NO data exceeds the array length
          //numSamples++; //=(numSamples)+1;
      }
    ADCSRA |= (1 << ADIE);  // enable interrupts when routine is done
    //ADCSRA |= (1 << ADIE);  // enable interrupts when routine is done
    //>>(((subsampleCount++)-1) & (subsample-1));  // >> divides by sample count so samples are ignored until s
}
}


void loop() { 
  
  if (logdataflag) {
    getdata();
  } else checkkeypress();   // checks the kepress every loop
}

//void getdata(){}
//void checkkeypress() {}


void startcapture(){
    numSamples=0;
    subsampleCount=0;
    //delayMicroseconds(200);
    
    logdataflag = true;
    allowkeypress=false;
    trigger();
    configISR();
    //enableISR();
    
    time0 = (long) (micros());
    //xx=0;
    
    
}
          
          
void sendheader(){
    if (OutputAscii) Serial.print('A'); else Serial.write('A');
    if (OutputAscii) {Serial.print('Z');Serial.print(",");} else Serial.write('Z');
    //if (OutputAscii) {Serial.print((byte)(N/256),HEX);Serial.print("+");} else {Serial.write((byte)(N/256));}
    //if (OutputAscii) {Serial.print((byte)(N%256),HEX);Serial.print(",");}  else {Serial.write((byte)(N%256));}
    if (OutputAscii) {Serial.print((byte)(numSamples>>8 & 255),HEX);Serial.print("+");} else {Serial.write((byte)(numSamples>>8 & 255));}
    if (OutputAscii) {Serial.print((byte)(numSamples & 255),HEX);Serial.print(",");}  else {Serial.write((byte)(numSamples & 255));}
    if (OutputAscii) {Serial.print((byte)(N>>8 & 255),HEX);Serial.print("+");} else {Serial.write((byte)(N>>8 & 255));}
    if (OutputAscii) {Serial.print((byte)(N & 255),HEX);Serial.print(",");}  else {Serial.write((byte)(N & 255));}
    if (OutputAscii) {Serial.print((byte)(t>>16 & 255),HEX);Serial.print("+");} else Serial.write((byte)(t>>16 & 255));
    if (OutputAscii) {Serial.print((byte)(t>>8 & 255),HEX);Serial.print("+");} else Serial.write((byte)(t>>8 & 255));
    if (OutputAscii) {Serial.print((byte)(t>>0 & 255),HEX);Serial.print(",");} else Serial.write((byte)(t>>0 & 255));
    //if (OutputAscii) {Serial.print((byte)(t/256),HEX);Serial.print("+");} else Serial.write((byte)(t/256));
    //if (OutputAscii) {Serial.print((byte)(t%256),HEX);Serial.print(",");} else Serial.write((byte)(t%256));
    if (OutputAscii) {Serial.print((byte)(Nbits),HEX);Serial.print(",");} else Serial.write((byte)(Nbits));
    //header cRC
    long crc=(((long) Nbits)+((long) numSamples)+t);
    if (OutputAscii) {Serial.print(((byte)(crc>>8 & 255)),HEX);Serial.print(",");} else Serial.write((byte)(crc>>8 & 255));
    if (OutputAscii) {Serial.print(((byte)(crc  & 255)),HEX);Serial.print(",");} else Serial.write((byte)(crc & 255));
    //if (OutputAscii) {Serial.print(((byte)(((long) Nbits)+((long) N)+t) & 255),HEX);Serial.print(",");} else Serial.write((byte)(((long) Nbits)+((long) N)+t) & 255);
    if (OutputAscii) Serial.println();
}
void getdata()
{
  if(togglebit)   digitalWrite(testPin, LOW);
  else   digitalWrite(testPin, HIGH);
  if (numSamples%128==0) togglebit=!togglebit;

  //OutputAscii=false;
  //float dt;
  //if (Verbose) {Serial.print(numSamples);}
  if (numSamples>=N){
  // it's possible an interrupt will occur after this if statement but before disableISR(), so numSamples will change
  // at Fmode=3 and higher this happens OFTEN !!!
    disableISR();
    //disableADC();
    //if (1) { //check numSamples has not changed after entering this routine numSamples==N
      logdataflag=false;  // stop any chance of ISR happening again
      allowkeypress=false; // incase  a prescaler still have 1 conversion left it if after the interrupt is turned off, the loop() routine with logdataflag=false would force a keep press check

      // if N is redefined before code below is run, this would caue issues
      //numSamples=N; // FORCE numSamples to be N - allows for case where EXTRA samples were taken by addition ISR calls
      //numSamples=0;

      int val=0;
    byte out;
        byte valout;
      int i;
       
      //disableADC();  
      //noInterrupts();
      /*
       char    szStr[20]; 
      Serial.println('T=');
      sprintf( szStr, "%08lX\t%lu", t, t );
      Serial.println(szStr);
      sprintf( szStr, "%08lX\t%lu", time0, time0 );
      Serial.println(szStr);
      Serial.println(t);
      Serial.println(t,HEX);
      Serial.println(time0,HEX);
      */
      // see https://forum.arduino.cc/t/undoing-the-creation-of-an-interrupt/323723/5
      //numSamples=0;  // first and last command in the loop
      
      //Serial.print(OutputAscii);
      t = (( long) micros())-time0;  // calculate elapsed time
      sendheader();
      //Serial.println();
      shift=0; //MOD(shift+Nbits-8,Nbits) ;  // Nbits of at least  bits
      carry=0;
      shiftval=0;
      //Serial.println();
  
 
      for ( i= 0; i <(int)N; i ++) {
        //val=data[i];
        /*
          
         scale= (int) (2 <<(8-shift))/2; // scale is base don last value of shift
        shiftedcarry=(int)(carry*scale);  // use the previous carry value
        shift=(byte) ((shift+(Nbits-8)) % Nbits) ;  // Nbits of at least  bits
        shiftval=(byte) (shiftval % Nbits)+(Nbits-8) ;  // Nbits of at least  bits
        rshiftval=(byte)(val>>shiftval);
        carry= (byte) (val % ((int) (2<<shift)/2) ); //      
        out=(byte) shiftedcarry+rshiftval;
        */
        //next=data2[i]%(2^shift);
        out=data[i];
        if (OutputAscii) {Serial.print(out,HEX);Serial.print(",");} else Serial.write(out);
        /*
         if ((byte) ((shift+(Nbits-8)) % Nbits) == 0){
          // check if the next shit =0
          //set to zero
          shift=0; //(Nbits-8);
          shiftval=shift;
          //scale= (int) (2 <<(8-shift))/2; // scale is base don last value of shift
          //shiftedcarry=(int)(carry*scale);  // use the previous carry value
          if (OutputAscii) {Serial.print(carry,HEX); Serial.print(",");} else Serial.write(carry); 
        carry=0; // reset carry
        }
        */
      }
      if (OutputAscii) {Serial.println((byte) cksum(),HEX);} else Serial.write((byte) cksum());
      
      //Serial.println();
      //Serial.flush();  // clear the buffer
      //Serial.begin(baudrate); //57600  115200
      //delay(100);
      //for (i=0;i<10;i++) {
      //interrupts();
      //
      //noInterrupts();
      logdataflag=true;
      allowkeypress=true;
      checkkeypress();  //checkkey press  
      trigger();  
      //interrupts();

      //  delay(100);
      //}
      //checkkeypress();  //checkkey press
      //delay(100);
      //zerodata();
      //xx=0;
      //trigger();
      //delayMicroseconds(700);
      
      // restart
  
  
      
      numSamples=0;
      subsampleCount=0; //subsample;
      //delay(20);
      // Next line is essential to ensure the stop [X] command actually stops a grab of data
      //Serial.println();
  
      if (logdataflag==true) {
        //interrupts();
        time0 = ( long) micros();
        //enableADC();
        enableISR();
        if (SampleRepeats!=0)
          if(SampleRepeats==iSampleRepeats) {
          logdataflag = false;
          disableISR();
          //disableADC();
          numSamples=0;
          subsampleCount=0;
          //logdataflag=false;  // stop any chance of ISR happening again
          allowkeypress=true;
          iSampleRepeats=1;
          }else {iSampleRepeats++;}
        
        } // else nothing in case he checkkeypress resulted in X that stopped the grab
    //} // end of 2nd numSamples==N check
  } /*else if (numSamples>N) {
      disableISR();  // stop interrupts until we reset all
      // possibly here due to false triggers - timing will be off in N>Nmax, so dump
      // oocurs alot at high speeds f3
      numSamples=0;
      subsampleCount=subsample;
      noInterrupts();
      //logdataflag=true;  // return to true state
      allowkeypress=true;
      checkkeypress();  //checkkey press 
      trigger();
      interrupts();
      //interrupts();
      
      time0 = ( long) micros();
      //Serial.println();
      //Serial.println("Dumping Data");
      if (OutputAscii) {Serial.print("Dumping Data");} 
      enableISR(); // last action before leaving loop
    }
    */
}

void trigger() {
    //Ultrasonic trigger pulse
    if(1) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    // Sets the trigPin on HIGH state for 10 micro seconds
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
     // add a trigger delay
    delayMicroseconds(triggerdelay);
    }
}

void disableISR(){
  ADCSRA &= ~(1 << ADIE); // disable interuppts when 
}
void enableISR(){
  numSamples=0;
  subsampleCount=0;
  ADCSRA |= (1 << ADIE);  // enable interrupts when routine is done
}
void disableADC() {

  // reset clock to make UART work
  //ADCSRA = tempADCSRA;             // clear ADCSRA register
  //ADCSRB = tempADCSRB;  
  //ADCSRA &= ~(1 << ADSC);  // stop ADC measurements
  //ADCSRA &= ~(1 << ADEN);  // disable ADC  do not turn off
  disableISR();
  //ADCSRA &= ~(1 << ADIE); // disable interuppts when 
  //ADCSRA &= ~(1 << ADATE); // disable auto trigger
  
  ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // default needed for UART and millisec timmer
  //ADCSRA=tempADCSRA;
  //ADCSRA &= ~(1 << ADSC);  // stop ADC measurements
  //ADCSRA &= ~(1 << ADEN);  // disable ADC
  //ADCSRA &= ~(1 << ADIE); // disable interuppts when 
  //ADCSRA &= ~(1 << ADATE); // disable auto trigger
}
void enableADC() {
  ADCSRA = 0;             // clear ADCSRA register
  //ADCSRB = 0;             // clear ADCSRB register
  //ADCSRA |=  (1 << ADPS1) | (1 << ADPS0);    // 8 prescaler for 153.8 KHz
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // default needed for UART and millisec timmer
  ADCSRA |= min(Fmode,7);    // 8 prescaler for 153.8 KHz
  //if (Verbose) {Serial.print("Sample Frequency = ");Serial.println(Fmode);}
  ADCSRA |= (1 << ADATE); // enable auto trigger
  //ADCSRA |= (1 << ADIE);  // enable interrupts when routine is done
  //ADCSRA |= (1 << ADIE);  // enable interrupts when measurement complete
  ADCSRA |= (1 << ADEN);  // enable ADC
  ADCSRA |= (1 << ADSC);  // start ADC measurements
  enableISR();
}

void configISR() {
  ADCSRA = 0;             // clear ADCSRA register
  ADCSRB = 0;             // clear ADCSRB register, only needs to be set once
  //analog comparator multiplexer enable bit (ACME in ADCSRB) is set and the ADC is switched off (ADEN in ADCSRA is zero),
  //ADCSRA &= ~(1 << ADSC);  // stop ADC measurements
  //ADCSRA &= ~(1 << ADEN);  // disable ADC  do not turn off
  //ADCSRA &= ~(1 << ADIE); // disable interuppts when 
  //ADCSRA &= ~(1 << ADATE); // disable auto trigger
  delayMicroseconds(2); // wait for conversions to end
  ADMUX = ((Channel-1) & 15);    // set analog input pin last 4 bits
  ADMUX |= (1 << REFS0);  // set reference voltage
  ADMUX |= (1 << ADLAR);  // left align ADC value to 8 bits from ADCH register. NOT DEFAULT
  //ADCSRA &= ~(1 << ADEN);  // clear to push ADMUX values
  enableADC();
  // sampling rate is [ADC clock] / [prescaler] / [conversion clock cycles]
  // for Arduino Uno ADC clock is 16 MHz and a conversion takes 13 clock cycles
  //ADCSRA |= (1 << ADPS2) | (1 << ADPS0);    // 32 prescaler for 38.5 KHz
 //ADCSRA |= (1 << ADPS2);                     // 16 prescaler for 76.9 KHz
 //ADCSRA |= (1 << ADPS1) | (1 << ADPS0);    // 8 prescaler for 153.8 KHz
 //ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // default needed for UART and millisec timmer
  /*ADCSRA |= min(Fmode,7);
  // ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // default needed for UART and millisec timmer  
  ADCSRA |= (1 << ADATE); // enable auto trigger
  ADCSRA |= (1 << ADIE);  // enable interrupts when measurement complete
  ADCSRA |= (1 << ADEN);  // enable ADC
  ADCSRA |= (1 << ADSC);  // start ADC measurements
  */
  }

byte cksum() {
  unsigned long x=0;
  for(int i=0;i<  N;i++)  // Current VERSION MUST have N divisible by 8 !!
  //for(int i=0;i<  numSamples;i++)  
  // checksum uses numSamples as the number of samples may be >N
        x+=data[i];
 return ((byte) x);
 }

void zerodata() {
  for(int j=0;j< (int) Nmax;j++)
        data[j] = 0;
}



void splash (void) {
  Serial.println(F("ArduinoScope - By Adrian Keating (C) 2021"));
  Serial.println(F("Command Set (use either upper or lower case, end with CR):"));
  Serial.println(F("? - Help [?]"));
  Serial.println(F("A - Set [A]SCII output (long)"));
  Serial.println(F("B - Set [B]INARY output (short)"));
  
  Serial.print(F("Nnn - [N]umber of Samples nn=to 1 to "));Serial.println(Nmax);
  Serial.println(F("F - Sampling [F]requency: 1=615kHz,2=307kHz,3=153kHz,4=76.8kHz(default),5=38.4kHz,6=19.27=9.6kHz"));
  Serial.println(F("H - [H]eader"));
  Serial.println(F("Cn - [C]channel 1<n<6"));
  Serial.println(F("Dn - Trigger [D]elay 0<n<32768"));
  Serial.println(F("R[nn] - [R]epeat Capture, infinite or optional nn<256"));
  Serial.println(F("X - Stop Capture [X]"));
  Serial.println(F("V - [V]erbose"));
  Serial.println(F("S - [S]ilent)"));
  
}

int GetNumber2 ()
{
  boolean ExitFlag = false;
  int charval = 0;
  int chval = 0;

  //           if (Verbose) Serial.print(" BytesAtSerialPort");
  //     if (Verbose) Serial.println( BytesAtSerialPort,DEC);
  while (ExitFlag == false)
    {
      if (true)
        chval = Serial.read ();
       else
        ExitFlag = true;
      //BytesAtSerialPort-=1;
      //             if (Verbose) Serial.print(";");
      //      if (Verbose) Serial.print(chval,DEC);
      if (chval >= '0' && chval <= '9')
  {     // is ch a number?  
    charval = charval * 10 + chval - '0'; // yes, accumulate the value
  }
      else if (chval == ';' || chval == 13 || chval == 10)
  {     // is ch an x or a CR
    ExitFlag = true;
  }
    }
  // if (Verbose) Serial.println();
  return charval;
}

 /*
int GetNumber2 (int &BytesAtSerialPort)
{
  boolean ExitFlag = false;
  long charval = 0;
  int chval = 0;

  //           if (Verbose) Serial.print(" BytesAtSerialPort");
  //     if (Verbose) Serial.println( BytesAtSerialPort,DEC);
  while (ExitFlag == false)
    {
      chval = Serial.read ();
      BytesAtSerialPort-=1;
      //             if (Verbose) Serial.print(";");
      //      if (Verbose) Serial.print(chval,DEC);
      if (chval >= '0' && chval <= '9')
  {     // is ch a number?  
    charval = charval * 10 + chval - '0'; // yes, accumulate the value
  }
      else if (chval == ';' || chval == 13 || chval == 10)
  {     // is ch an x or a CR
    ExitFlag = true;
  }
    }
  // if (Verbose) Serial.println();
  return charval;
}
*/
 
int xxGetNumber2 () {
  // returns a float from entered data, allows white space
  volatile int NumBytesAvaiable;
  volatile int NextByte;
  volatile boolean ExitFlag = false;
  volatile long val = 0;
  volatile float valfloat;
  volatile float scale;
  volatile int chval = 0;
  volatile int indexponent = 0;
  volatile int ind = 0;
  volatile int sign = 1;
  while (ExitFlag == false)
  {
    chval = Serial.read ();
    if (chval == '-' & ind == 0)
    { //  loop as many times as required to cheak for minus
      // do nothing
      sign = sign * -1;;
    }
    else {
      if (chval == '.' & indexponent == 0)
      { // note the location of a decimal pt
        // the check & indexponent==0 ensure that is a 2nd decimal point is entered, it is ignored
        ind = ind + 1;
        indexponent = ind;
      }
      else
      {
        if (chval >= '0' && chval <= '9')
        { // is ch a number?
          val = val * 10 + chval - '0'; // yes, accumulate the value
          ind = ind + 1;
        }
        else if (chval == ';' || chval == 13 || chval == 10)
        { // is ch an ; or a CR
          if (ind == 0)
            valfloat = val; // traps case when only ; entered and no number
          else
          {
            if (indexponent == 0) indexponent = ind;
            scale = pow (10, (ind - indexponent));
            valfloat = ((float) sign * val) / scale;
          }
          ExitFlag = true;
        }     // end check for decimal pt
      }   // check for leading + or - sign
    }
  }
  return ((volatile int) valfloat);
}
 
void checkkeypress() {
   int Bytes2Read = 0;
   int myinteger = 0;
   int inByte= 0;
  //float myfloat = 0;
  //Serial.flush();
  if(allowkeypress) {
    Bytes2Read = Serial.available();
    //Bytes2Read=1;
    while (Bytes2Read > 0) {
     //Serial.print("Found Bytes=");
     //Serial.print(Bytes2Read);
      //int inByte = Serial.read();
  
  
      inByte = Serial.read();
      /*Serial.print("Found Bytes=");
      Serial.print(Bytes2Read);
      Serial.print(",");
      Serial.println(inByte);
      */
      //Serial.flush();
      Bytes2Read = Serial.available(); //update bytes available
      //inByte='R';
      //int inByte ='R';
  
  
      if (inByte > 96) inByte = inByte - 32; //convert to upper case
      switch (inByte) {
        case 'R':
          // Repeated Grabs
          if (logdataflag==false) {
            if (Verbose && !logdataflag) {Serial.println("Repeated Grab");}
            // only start if nto yet started
            myinteger=GetNumber2();
            SampleRepeats=min(myinteger,(byte) 255);
            iSampleRepeats=1;
            startcapture();
            /*
             *
            delayMicroseconds(200);
            numSamples=0;
            configISR();
            enableISR();
            trigger();
            //xx=0;
            t0 = micros();
            logdataflag = true;
            */
          }
          break;
        case '?':
          splash();
          break;
        case 'V':
          Verbose = true;
          if (Verbose && !logdataflag) {Serial.println("Verbose MODE");}       
          break;
        case 'S':
          Verbose = false;
          break;
        case 'A':
        // Set output to ASCII mode
        if (Verbose && !logdataflag) {Serial.println("ASCII (Long) MODE");}
          OutputAscii=true;
          //Serial.print("SET OutputAscii = ");
          //Serial.println(OutputAscii ? "HIGH" : "LOW");
          break;
        case 'B':
        // Set output to Bininary (compact) mode = Default
          if (Verbose && !logdataflag) {Serial.println("Binary (Compact) MODE");}
          OutputAscii=false;
          ///Serial.print("SET OutputAscii = ");
          //Serial.println(OutputAscii ? "HIGH" : "LOW");
          break;
        case 'N':
          //myfloat = ReturnFloat(Bytes2Read);
          myinteger=GetNumber2();
          //N = min(((int) myfloat),Nmax);
          // only change N if it is !=0
          if(myinteger!=0){
            myinteger = min(myinteger,(int) Nmax);
            N=((unsigned int) max(myinteger,1));
            //zerodata();  // reset all data before next read
            //Serial.flush();
            /*
                numSamples=0;
                subsampleCount=subsample;
                if (logdataflag==true) {
                  // if the new N value can after data was sent, restart the interrupts
                  trigger();  
                interrupts();
                  time0 = ( long) micros();
                  enableISR();
                    }
                   */
          }
          //if (Verbose && !logdataflag) {Serial.print("Samples=");Serial.println((int) N, DEC);Serial.println(Bytes2Read, DEC);Serial.println(myinteger, DEC);}
          //Serial.println();Serial.print("Samples=");Serial.println((int) N, DEC);
          if (Verbose && !logdataflag) {Serial.print("Samples=");Serial.println((int) N, DEC);}
          break;
        case 'H':
          sendheader();
          break;
        case 'C':
        // select channel
          myinteger=GetNumber2();
          //N = min(((int) myfloat),Nmax);
          // only change N if it is !=0
          if (myinteger <1 | myinteger >7)  {
            // do nothing if returned value out of range
            //Fmode=3;  // set to default
          }  else {
            Channel = (byte) myinteger;  // must be 1 to 7
            if (Verbose && !logdataflag) {Serial.print("Channel (");Serial.print(ADMUX,HEX); Serial.print(") = ");Serial.println(Channel);}
          }
          break;
        case 'X':
          // Turn logging off
          logdataflag = false;
          disableISR();
          //disableADC();
          numSamples=0;
          //logdataflag=false;  // stop any chance of ISR happening again
          allowkeypress=true;
          // only send SERIAL OUT once disabled !!!
          //ADCSRA=tempADCSRA;            // retrieve ADCSRA register
          //ADCSRB=tempADCSRB;            // retrieve ADCSRB register
          //delayMicroseconds(100);
          //Serial.flush();  // remove anything left
          //delayMicroseconds(100);
          //Serial.flush();  // remove anything left
          //delayMicroseconds(100);
          if (Verbose && !logdataflag) {Serial.println ("STOPPING GRAB");}
  
          //logdataflag = false;
          break;
        case 'F':
          //  Set Frequency
          myinteger=GetNumber2();
          
          //myfloat = ReturnFloat(Bytes2Read);
          if (myinteger <1)  {
            // do nothing if returned value out of range
            //Fmode=3;  // set to default
          } else if (myinteger >7) {
            subsample=(byte) min((byte)2<<max(myinteger-8,0),128); // min1 max 128
            subsampleCount=0;
            Nbits=10;
            if (Verbose && !logdataflag) {Serial.print("Sample Frequency = ");Serial.print(f[7-1]*1000/((int) subsample));Serial.println(" Hz");Serial.println(((int) subsample),DEC);}
            }
          else {
            Fmode = max(min(myinteger,7),1);  // must be 1 to 7
            subsample=0; // grab fastest
            subsampleCount=0;
            Nbits=8;
            if (Verbose && !logdataflag) {Serial.print("Sample Frequency = ");Serial.print(f[Fmode-1]);Serial.println(" kHz");}
          }
          break;
          case 'D':
          //  Set delay in microseconds
          myinteger=GetNumber2();
          
          //myfloat = ReturnFloat(Bytes2Read);
          if (myinteger <1)  {
            // do nothing if returned value out of range
            triggerdelay=0;
          } else  {
            triggerdelay=myinteger;
            if (Verbose && !logdataflag) {Serial.print("Trigger Delay= ");Serial.print(triggerdelay);Serial.println(" microseconds");Serial.println(triggerdelay,DEC);}
            }
          break;
          //default:
          // do nothing
          //default:
          // do nothing
      }
      //Serial.flush();
      //Bytes2Read-=1;  // removes any bytes not regonized
    }
}
}
