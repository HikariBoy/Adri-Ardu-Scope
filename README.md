# Adri/Ardu-Scope
 Creates the basic functionality of an [oscilloscope](https://en.wikipedia.org/wiki/Oscilloscope) ( plus [spectrum analyser](https://en.wikipedia.org/wiki/Spectrum_analyzer) Spectrum Analyser and Cross-correlation scope) from a very low cost [Arduino](https://www.arduino.cc/) to allow the ability to explore signals, collect data and complete high-school/University laboratories even when students are completing portions of their studies remotely.

 ## QuickStart
  Follow these steps to get up and runnign with with Adri/Ardu-Scope Quickly:
  1. *Upload the [AdriArduScope.ino](AdriArduScope.ino) file to your Arduino.* Use your favorite upload tool, most likely the [Arudino IDE](https://www.arduino.cc/en/software).  Select the type or Arduino - this has been tested on a Nano, Uno and Mega
  2. *Download the remaining files (.py file and png files) to a single directory.* Run under python 3 - the only dependency required is matplotlib.  [Install matplotlib](https://matplotlib.org/stable/users/installing.html) appropriately for either conda or pip versions.  At this time, executables for Windows and MACs have not been produced but may be in the future.

  ## Motivation
   <img src="images\UWA-Full-Ver-CMYK3.png" alt="UWA logo"  align="right" width="150"/><br>
On many occasions you might need a [oscilloscope](https://en.wikipedia.org/wiki/Oscilloscope) or spectrum analyser.  The cost of USB scopes has significantly dropped over the last few years, allowing me for example to use the [2-channel, 10 MHz pico-scope 2000 series](https://www.picotech.com/oscilloscope/2000/picoscope-2000-overview) in my teaching at [The University of Western Australia](https://www.uwa.edu.au/) - this is as a excellent tool to looking and generating signals and giving students a face-to-face demonstration of data collection.   <b>But what if the cost and specifications of even a USB scope like this is beyond that required.</b> <br>
This work considered how to make an [oscilloscope](https://en.wikipedia.org/wiki/Oscilloscope) and [spectrum analyser](https://en.wikipedia.org/wiki/Spectrum_analyzer) that could sample signals at around 153 kHz, more than adequate for audio, accelerometer, vibration and ultrasonic (40 kHz) investigations.  The hope here was to be able to create University level laboratories for our students who are remote (isolated by COVID), to get hands on, practical experience with signals and [time-series](https://en.wikipedia.org/wiki/Time_series) data collection.  All that's required is a ~$5 Arduino and the software tools on this site to create a very practical learning environment.  If you try this tool and think it useful, please let me know and where used/publicised, please promote and cite the project in any published work (see link on this site).   
Features of the [AdriArduScope.py](AdriArduScope.py) interface include: <img src="images\About.png" alt="About"  align="right" width="550"/><br>
* Two (2) channels supported, allowing (sequential) display of both channels
* High speed update to the display interface allows "real-time" interaction with the signals being received
* Sampling at up to 153 kHz - the sampling rate (display range) can be changed to allow sampling over many seconds
* External trigger (10 microsecond pulse) generated on Arduino port D4 - this is consistent with the wiring using for standard [HR-S04 Ultrasonic sensors](https://core-electronics.com.au/tutorials/how-to-use-ultrasonic-sensors.html).  Trigger delay allows signal capture after trigger event
* Amplitude and offset adjust available from the interface
* Save data to internal memory
* Save data to local drive (for post analysis in tools such as excel)
* Oscilloscope, Spectrum analyser and Cross-correlation analyser - The cross correlation analyser works in two modes: In a screen shot is saved to memory, the cross-correlation of the signal is obtained with the stored memory.  If the scope if setup to acquire data from both channel 1 and channel 2, the cross-correlation can be performed between Channel 1 &2.


 ## Testing:  
 If any of the above steps didn't work, or you want to use the Arduino to stream ADC data without the python interface you can try the following.  After Step 1 above you can test Adri/Ardu-Scope by opening up a serial monintor (again from the Arduino IDE).  The I/O uses a serial rate of 115200 baud which must be set for valid data to be read over the serial monitor.  From the serial monitor screen type "?" to see the help screen with most functions described.  The help screen should show the following:
 ArduinoScope - By Adrian Keating (C) 2021
 * Command Set (use either upper or lower case, end with CR):
 * ? - Help [?]
 * A - Set [A]SCII output (long)
 * B - Set [B]INARY output (short)
 * Nnn - [N]umber of Samples nn=to 1 to 1024
 * F - Sampling [F]requency: 1=615kHz,2=307kHz,3=153kHz,4=76.8kHz(default),5=38.4kHz,6=19.27=9.6kHz
 * H - [H]eader
 * Cn - [C]channel 1<n<6
 * Dn - Trigger [D]elay 0<n<32768
 * R[nn] - [R]epeat Capture, infinite or optional nn<256
 * X - Stop Capture [X]
 * V - [V]erbose
 * S - [S]ilent)

By default the Adri/Ardu-scope is set to send data in binary format (as this allows faster data update).  To understand the data returned by the Adri/Ardu-scope from the serial monitor, send the "A" command (upper or lower case) to send the data in human readable [ASCII](https://www.asciitable.com/) form.

 ## Screen Shots

 <span><div style="float: left  color: blue font-style: italic">
 <img src="images\ScopeImage.PNG" alt="Steps 1 and 2"  align="right" width="500"/><br></div> </span>
  <p></p><span> <figcaption > <I><b>Figure 1:</b>Screen shot from Adri/Ardu-Scope when in Oscilliscope mode. The analogue signal received by the [HR-S04 Ultrasonic sensor](https://core-electronics.com.au/tutorials/how-to-use-ultrasonic-sensors.html) obtained by direct connection to [Pin 7 of the LM324 in the circuit](http://www.pcserviceselectronics.co.uk/arduino/Ultrasonic/HC-SR04-cct.pdf) </I> </figcaption> </span><br>
<br>

<span><div style="float: left  color: blue font-style: italic">
<img src="images\SpectrumImage.PNG" alt="Steps 1 and 2"  align="right" width="500"/><br></div> </span>
 <p></p><span> <figcaption > <I><b>Figure 2:</b>Screen shot from Adri/Ardu-Scope when in Spectrum mode. Here the center frequency of the 40 kHz  [HR-S04 Ultrasonic sensor](https://core-electronics.com.au/tutorials/how-to-use-ultrasonic-sensors.html) can be seen.</I> </figcaption> </span><br>
<br>

<span><div style="float: left  color: blue font-style: italic">
<img src="images\CrossCorrelationImage.PNG" alt="Steps 1 and 2"  align="right" width="500"/><br></div> </span>
 <p></p><span> <figcaption > <I><b>Figure 3:</b>Screen shot from Adri/Ardu-Scope when in Cross-Correlation mode. Here the data in Figure 3 was stored in memory (after recording it in AC mode), then the Cross-corelation function activated and the absolute option (ABS) set</I> </figcaption> </span><br>
<br>


 ## Source
 The source code [AdriArduScope.py](AdriArduScope.py) was created under python 3.7.10.

 ##Issues:
   the Rubric cannot contain any spaces - this needs to be fixed
