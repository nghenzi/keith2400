# Keithley IV Sweep for 2400 SourceMeter

# Variable intake and assignment
import sys
startv = sys.argv[1]
stopv = sys.argv[2]
stepv = sys.argv[3]
gatev = sys.argv[4]
filename = sys.argv[5]
startvprime = float(startv)
stopvprime = float(stopv)
stepvprime = float(stepv)
steps = (stopvprime - startvprime) / stepvprime 

# Import PyVisa and choose GPIB Channel 25 as Drain-Source and 26 as Gate
import visa
rm = visa.ResourceManager()
rm.list_resources()
Keithley = rm.open_resource('GPIB0::25::INSTR')
Keithleygate = rm.open_resource('GPIB0::26::INSTR')
Keithley.write("*RST")
Keithleygate.write("*RST")
Keithley.timeout = 25000
Keithleygate.timeout = 25000

# Turn off concurrent functions and set sensor to current with fixed voltage
Keithley.write(":SENS:FUNC:CONC OFF")
Keithley.write(":SOUR:FUNC VOLT")
Keithley.write(":SENS:FUNC 'CURR:DC' ")

# Set
Keithleygate.write(":SOUR:FUNC VOLT")
Keithleygate.write(":SOUR:VOLT:MODE FIXED")
Keithleygate.write(":SOUR:VOLT:RANG 20")
Keithleygate.write(":SOUR:VOLT:LEV ", gatev)
Keithleygate.write(":SENS:CURR:PROT 1")

# Voltage starting, ending, and spacing values based on input
Keithley.write(":SOUR:VOLT:STAR ", startv)
Keithley.write(":SOUR:VOLT:STOP ", stopv)
Keithley.write(":SOUR:VOLT:STEP ", stepv)
Keithley.write(":SOUR:SWE:RANG AUTO")

# Set compliance current (in A), sweep direction, and data acquisition
Keithley.write(":SENS:CURR:PROT 1")
Keithley.write(":SOUR:SWE:SPAC LIN")
Keithley.write(":SOUR:SWE:POIN ", str(int(steps)))
Keithley.write(":SOUR:SWE:DIR UP")
Keithley.write(":TRIG:COUN ", str(int(steps)))
Keithley.write(":FORM:ELEM CURR")

# Set sweep mode and turn output on
Keithley.write(":SOUR:VOLT:MODE SWE")
Keithleygate.write(":OUTP ON")
Keithley.write(":OUTP ON")

# Initiate sweep, collect ACSII current values, and turn output off
result = Keithley.query(":READ?")
yvalues = Keithley.query_ascii_values(":FETC?")
Keithley.write(":OUTP OFF")
Keithleygate.write(":OUTP OFF")
Keithley.write(":SOUR:VOLT 0")
Keithleygate.write(":SOUR:VOLT 0")

# Import Pyplot, NumPy, and SciPy
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Create xvalues array and calculate conductance
xvalues = np.arange(startvprime,stopvprime,stepvprime)
slope, intercept, r_value, p_value, std_error = stats.linregress(xvalues, yvalues)

# Plot values and output conductance to command line
print("Conductance:", slope, "Siemens")
plt.plot(xvalues,yvalues)
plt.xlabel(' Drain-Source Voltage (V)')
plt.ylabel(' Drain-Source Current (A)')
plt.title('IV Curve')
plt.figtext(0.7, 0.2, 'Vg=' + str(gatev) + 'V', fontsize=15)
plt.show()
np.savetxt(filename, (xvalues,yvalues)) 