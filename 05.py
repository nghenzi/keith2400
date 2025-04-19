*IDN?;*RST;
:SOUR:FUNC VOLT;:SOUR:VOLT 0.100000;:CURR:PROT 0.001000;


SOUR:MEM:SAVE 1;
SOUR:MEM:REC 1;

:ARM:COUN 1; :TRIG:COUN 1;
:SOUR:VOLT:MODE LIST;
:SOUR:CURR:MODE LIST; # SWE # FIX 

ARM:SOUR IMM; :ARM:TIM 0.010000; :TRIG:SOUR IMM;:TRIG:DEL 0.000000;

OUTP ON;


SOUR:FUNC MEM;:SOUR:MEM:STAR 1;:SOUR:MEM:POIN 5;

:FETC?



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
:*RST
:TRAC:CLE ‘clear buffer and set for 10 readings
:TRAC:POIN 10
:STAT:MEAS:ENAB 512 ‘generate an SRQ upon buffer full (GPIB only!)
:*SRE 1
:TRIG:COUN 10 ‘trigger count
:SYST:AZER:STAT OFF ‘Auto Zero off
:SOUR:FUNC CURR ‘source current
:SENS:FUNC:CONC OFF ‘concurrent readings off
:SENS:FUNC "VOLT" ‘measure voltage
:SENS:VOLT:NPLC 0.08
:SENS:VOLT:RANG 20
:SENS:VOLT:PROT:LEV 10 ‘voltage compliance
:FORM:ELEM VOLT ‘read back voltage only
:SOUR:CURR 0.01 ‘source current level
:TRIG:DEL 0 ‘trigger and source delay – we will modify this below***
:SOUR:DEL 0
:TRAC:FEED:CONT NEXT
:SOUR:CLE:AUTO ON ‘source auto clear
:DISP:ENAB OFF ‘display set up
:INIT
‘On receiving SRQ.
:TRAC:DATA?
‘Enter 10K bytes of data from 2400 & process data
‘clean up registers
*RST;
*CLS;
*SRE 0;
:STAT:MEAS:ENAB 0



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5555
SOUR:LIST:VOLT 0.000000E+0,100.000000E-3,200.000000E-3,300.000000E-3;
:TRIG:CLE;:INIT;
*OPC;

Change two lines in the above code with:
:TRIG:DEL 0.00438 ‘adjust trigger & source delay to achieve required pulse
:SOUR:DEL 0.00046

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


Here are the remote control commands listed in the manual:

Common Commands (Section 16) 
*IDN? - Identification query
*OPC - Operation complete
*OPC? - Operation complete query
*SAV <NRf> - Save setup
*RCL <NRf> - Recall setup
*RST - Reset
*TRG - Trigger
*TST? - Self-test query
*WAI - Wait-to-continue
*CLS - Clear status    
*ESE <NRf> - Event status enable    
*ESE? - Event status enable query    
*ESR? - Event status register query    
*OPT? - Options Query    
*SRE <NRf> - Service request enable    
*SRE? - Service request enable query    
*STB? - Status byte query    
SCPI Signal Oriented Measurement Commands (Section 17) 
:CONFigure:<function> - Configures the instrument for measurements on the specified function
:CONFigure? - Queries the active measurement function(s)    
:FETCh? - Requests the latest post-processed readings
[:SENSe[1]]:DATA[:LATest]? - Returns only the most recent reading
:READ? - Triggers and acquires readings
:MEASure[:<function>]? - Performs a one-shot measurement and acquires the reading
SCPI Command Reference (Section 18) 
CALCulate Subsystems
CALCulate[1]

:CALCulate[1]:MATH[:EXPRession]:CATalog? - Query list of expression names
:CALCulate[1]:MATH[:EXPRession]:NAME <name> - Select or create math expression name
:CALCulate[1]:MATH[:EXPRession]:NAME? - Query selected math expression name    
:CALCulate[1]:MATH[:EXPRession]:DELete[:SELected] <name> - Delete user-defined math expression
:CALCulate[1]:MATH[:EXPRession]:DELete:ALL - Delete all user-defined math expressions
:CALCulate[1]:MATH:UNITs <name> - Specify units for user-defined calculation
:CALCulate[1]:MATH:UNITs? - Query units for user-defined calculation    
:CALCulate[1]:MATH[:EXPRession] <form> - Define math formula
:CALCulate[1]:MATH[:EXPRession][:DEFine] <form> - Define math formula
:CALCulate[1]:MATH? - Query user-defined math expression    
:CALCulate[1]:STATe <b> - Enable/disable math expression
:CALCulate[1]:STATe? - Query state of math expression
:CALCulate[1]:DATA? - Read CALC1 result
:CALCulate[1]:DATA:LATest? - Read latest CALC1 result CALCulate2
:CALCulate2:FEED <name> - Select input path for limit tests
:CALCulate2:FEED? - Query input path for limit tests    
:CALCulate2:NULL:OFFSet <n> - Specify null offset (REL) value
:CALCulate2:NULL:OFFSet? - Query null offset value    
:CALCulate2:NULL:ACQuire - Automatically acquire REL value
:CALCulate2:NULL:STATe <b> - Enable/disable REL
:CALCulate2:NULL:STATe? - Query state of REL    
:CALCulate2:DATA? - Read CALC2 result (REL or Limit data)
:CALCulate2:DATA:LATest? - Read latest CALC2 data
:CALCulate2:LIMit[1]:COMPliance:FAIL <name> - Set Limit 1 fail condition (IN/OUT compliance)
:CALCulate2:LIMit[1]:COMPliance:FAIL? - Query Limit 1 fail condition    
:CALCulate2:LIMit[1]:COMPliance:SOURce2 <NRf>|<NDN> - Specify pattern for LIMIT 1 failure
:CALCulate2:LIMit[1]:COMPliance:SOURce2? - Query LIMIT 1 failure pattern    
:CALCulate2:LIMit[1]:STATe <b> - Enable/disable Limit 1 test
:CALCulate2:LIMit[1]:STATe? - Query state of Limit 1 test    
:CALCulate2:LIMit[1]:FAIL? - Read LIMIT 1 test result
:CALCulate2:LIMitx:LOWer[:DATA] <n> - Specify lower LIMIT x (x = 2, 3, 5-12)
:CALCulate2:LIMitx:LOWer? - Query lower LIMIT x value    
:CALCulate2:LIMitx:UPPer[:DATA] <n> - Specify upper LIMIT x (x = 2, 3, 5-12)
:CALCulate2:LIMitx:UPPer? - Query upper LIMIT x value    
:CALCulate2:LIMitx:LOWer:SOURce2 <NRf>|<NDN> - Specify pattern for grading mode; lower LIMIT x failure
:CALCulate2:LIMitx:LOWer:SOURce2? - Query lower LIMIT x failure pattern    
:CALCulate2:LIMitx:UPPer:SOURce2 <NRf>|<NDN> - Specify pattern for grading mode; upper LIMIT x failure
:CALCulate2:LIMitx:UPPer:SOURce2? - Query upper LIMIT x failure pattern    
:CALCulate2:LIMitx:PASS:SOURce2 <NRf>|<NDN> - Set sorting mode pass pattern (x = 2, 3, 5-12)
:CALCulate2:LIMitx:PASS:SOURce2? - Query sorting mode pass pattern    
:CALCulate2:LIMitx:STATe <b> - Enable/disable LIMIT x test (x = 2, 3, 5-12)
:CALCulate2:LIMitx:STATe? - Query state of LIMIT x test    
:CALCulate2:LIMitx:FAIL? - Read LIMIT x test result (x = 2, 3, 5-12)
:CALCulate2:LIMit4:SOURce2 <NRf>|<NDN> - Specify pattern for LIMIT 4 (Contact Check) failure
:CALCulate2:LIMit4:SOURce2? - Query LIMIT 4 failure pattern    
:CALCulate2:LIMit4:STATe <b> - Enable/disable Limit 4 test
:CALCulate2:LIMit4:STATe? - Query state of Limit 4 test    
:CALCulate2:LIMit4:FAIL? - Read LIMIT 4 test result
:CALCulate2:CLIMits:PASS:SOURce2 <NRf>|<NDN> - Specify composite pass pattern
:CALCulate2:CLIMits:PASS:SOURce2? - Query composite pass pattern    
:CALCulate2:CLIMits:FAIL:SOURce2 <NRf>|<NDN> - Specify composite fail pattern (sorting mode)
:CALCulate2:CLIMits:FAIL:SOURce2? - Query composite fail pattern    
:CALCulate2:CLIMits:FAIL:SMLocation <NRf>|NEXT - Specify "fail" source memory location for sweep branching
:CALCulate2:CLIMits:FAIL:SMLocation? - Query "fail" source memory location    
:CALCulate2:CLIMits:PASS:SMLocation <NRf>|NEXT - Specify "pass" source memory location for sweep branching
:CALCulate2:CLIMits:PASS:SMLocation? - Query "pass" source memory location    
:CALCulate2:CLIMits:BCONtrol <name> - Control Digital I/O port pass/fail update timing (IMMediate/END)
:CALCulate2:CLIMits:BCONtrol? - Query binning control timing    
:CALCulate2:CLIMits:MODE <name> - Control Digital I/O pass/fail output mode (GRADing/SORTing)
:CALCulate2:CLIMits:MODE? - Query Digital I/O mode    
:CALCulate2:CLIMits:CLEar[:IMMediate] - Clears test results and resets Digital I/O Port
:CALCulate2:CLIMits:CLEar:AUTO <b> - Control auto-clear for test results
:CALCulate2:CLIMits:CLEar:AUTO? - Query state of auto-clear  CALCulate3   
:CALCulate3:FORMat <name> - Specify statistic format (MEAN, SDEV, MAX, MIN, PKPK)
:CALCulate3:FORMat? - Query statistic format    
:CALCulate3:DATA? - Read CALC3 statistic result
DISPlay Subsystem

:DISPlay:DIGits <n> - Set display resolution (4 to 7 for 3.5 to 6.5 digits)
:DISPlay:DIGits? - Query display resolution    
:DISPlay:ENABle <b> - Enable/disable front panel display circuitry
:DISPlay:ENABle? - Query state of display    
:DISPlay[:WINDow[1]]:ATTRibutes? - Query attributes (blinking) for top display
:DISPlay:WINDow2:ATTRibutes? - Query attributes (blinking) for bottom display
:DISPlay:CNDisplay - Return to source-measure display state
:DISPlay[:WINDow[1]]:DATA? - Read top display content
:DISPlay:WINDow2:DATA? - Read bottom display content    
:DISPlay[:WINDow[1]]:TEXT:DATA <a> - Define text message for top display
:DISPlay:WINDow2:TEXT:DATA <a> - Define text message for bottom display    
:DISPlay[:WINDow[1]]:TEXT:DATA? - Query top text message    
:DISPlay:WINDow2:TEXT:DATA? - Query bottom text message    
:DISPlay[:WINDow[1]]:TEXT:STATe <b> - Enable/disable message for top display
:DISPlay:WINDow2:TEXT:STATe <b> - Enable/disable message for bottom display    
:DISPlay[:WINDow[1]]:TEXT:STATe? - Query message state for top display    
:DISPlay:WINDow2:TEXT:STATe? - Query message state for bottom display    
FORMat Subsystem

:FORMat[:DATA] <type>[,length] - Select data format for bus transfer (ASCii, REAL, SREal)
:FORMat[:DATA]? - Query data format    
:FORMat:ELEMents[:SENSe[1]] <item list> - Specify data elements for SENSE data string (VOLT, CURR, RES, TIME, STAT)
:FORMat:ELEMents[:SENSe[1]]? - Query SENSE data elements    
:FORMat:ELEMents:CALCulate <item list> - Set CALC data elements (CALC, TIME, STAT)
:FORMat:ELEMents:CALCulate? - Query CALC data element list    
:FORMat:BORDer <name> - Specify binary byte order (NORMal, SWAPped)
:FORMat:BORDer? - Query byte order    
:FORMat:SREGister <name> - Select data format for reading status registers (ASCii, HEX, OCT, BIN)
:FORMat:SREGister? - Query format for reading status registers    
:FORMat:SOURce2 <name> - Set SOURce2 and TTL query response format (ASCii, HEX, OCT, BIN)
:FORMat:SOURce2? - Query SOURce2 response format    
OUTPut Subsystem

:OUTPut[1][:STATe] <b> - Turn source on/off
:OUTPut[1][:STATe]? - Query state of source    
:OUTPut[1]:ENABle[:STATe] <b> - Enable/disable output enable line control
:OUTPut[1]:ENABle[:STATe]? - Query state of output enable line control    
:OUTPut[1]:ENABle:TRIPped? - Query if output enable line is tripped
:OUTPut[1]:SMODe <name> - Select output-off mode (HIMP, NORM, ZERO, GUAR)
:OUTPut[1]:SMODe? - Query output-off mode    
ROUTe Subsystem

:ROUTe:TERMinals <name> - Select front or rear panel terminals (FRONt, REAR)
:ROUTe:TERMinals? - Query selected terminals    
SENSe1 Subsystem

[:SENSe[1]]:DATA[:LATest]? - Return only most recent reading
[:SENSe[1]]:FUNCtion:CONCurrent <b> - Enable/disable concurrent measurements
[:SENSe[1]]:FUNCtion:CONCurrent? - Query concurrent state    
[:SENSe[1]]:FUNCtion[:ON] <function list> - Enable specified measurement functions
[:SENSe[1]]:FUNCtion[:ON]? - Query enabled functions    
[:SENSe[1]]:FUNCtion:OFF <function list> - Disable specified measurement functions
[:SENSe[1]]:FUNCtion:OFF? - Query disabled functions    
[:SENSe[1]]:FUNCtion[:ON]:ALL - Enable all measurement functions (or ohms if concurrent disabled)
[:SENSe[1]]:FUNCtion:OFF:ALL - Disable all measurement functions
[:SENSe[1]]:FUNCtion[:ON]:COUNt? - Query number of enabled functions
[:SENSe[1]]:FUNCtion:OFF:COUNt? - Query number of disabled functions    
[:SENSe[1]]:FUNCtion:STATe? <name> - Query state of a specified function
[:SENSe[1]]:CURRent[:DC]:RANGe[:UPPer] <n>|UP|DOWN - Select current measurement range
[:SENSe[1]]:CURRent[:DC]:RANGe? - Query current range    
[:SENSe[1]]:VOLTage[:DC]:RANGe[:UPPer] <n>|UP|DOWN - Select voltage measurement range
[:SENSe[1]]:VOLTage[:DC]:RANGe? - Query voltage range    
[:SENSe[1]]:RESistance:RANGe[:UPPer] <n>|UP|DOWN - Select resistance measurement range
[:SENSe[1]]:RESistance:RANGe? - Query resistance range    
[:SENSe[1]]:CURRent[:DC]:RANGe:AUTO <b> - Enable/disable auto range for current
[:SENSe[1]]:CURRent[:DC]:RANGe:AUTO? - Query current auto range state    
[:SENSe[1]]:VOLTage[:DC]:RANGe:AUTO <b> - Enable/disable auto range for voltage
[:SENSe[1]]:VOLTage[:DC]:RANGe:AUTO? - Query voltage auto range state    
[:SENSe[1]]:RESistance:RANGe:AUTO <b> - Enable/disable auto range for resistance
[:SENSe[1]]:RESistance:RANGe:AUTO? - Query resistance auto range state    
[:SENSe[1]]:CURRent[:DC]:RANGe:AUTO:LLIMit <n> - Set auto ranging lower limit for amps
[:SENSe[1]]:CURRent[:DC]:RANGe:AUTO:LLIMit? - Query amps auto range lower limit    
[:SENSe[1]]:VOLTage[:DC]:RANGe:AUTO:LLIMit <n> - Set auto ranging lower limit for volts
[:SENSe[1]]:VOLTage[:DC]:RANGe:AUTO:LLIMit? - Query volts auto range lower limit    
[:SENSe[1]]:RESistance:RANGe:AUTO:LLIMit <n> - Set auto ranging lower limit for ohms
[:SENSe[1]]:RESistance:RANGe:AUTO:LLIMit? - Query ohms auto range lower limit    
[:SENSe[1]]:CURRent[:DC]:RANGe:AUTO:ULIMit? - Query auto ranging upper limit for amps
[:SENSe[1]]:VOLTage[:DC]:RANGe:AUTO:ULIMit? - Query auto ranging upper limit for volts
[:SENSe[1]]:RESistance:RANGe:AUTO:ULIMit <n> - Set auto ranging upper limit for ohms
[:SENSe[1]]:RESistance:RANGe:AUTO:ULIMit? - Query ohms auto range upper limit    
[:SENSe[1]]:CURRent[:DC]:NPLCycles <n> - Specify integration rate for current
[:SENSe[1]]:VOLTage[:DC]:NPLCycles <n> - Specify integration rate for voltage
[:SENSe[1]]:RESistance:NPLCycles <n> - Specify integration rate for resistance
[:SENSe[1]]:CURRent[:DC]:NPLCycles? - Query current integration rate    
[:SENSe[1]]:VOLTage[:DC]:NPLCycles? - Query voltage integration rate    
[:SENSe[1]]:RESistance:NPLCycles? - Query resistance integration rate    
[:SENSe[1]]:CURRent[:DC]:PROTection[:LEVel] <n> - Set current compliance limit
[:SENSe[1]]:CURRent[:DC]:PROTection[:LEVel]? - Query current compliance limit    
[:SENSe[1]]:VOLTage[:DC]:PROTection[:LEVel] <n> - Set voltage compliance limit
[:SENSe[1]]:VOLTage[:DC]:PROTection[:LEVel]? - Query voltage compliance limit    
[:SENSe[1]]:CURRent[:DC]:PROTection:TRIPped? - Query if in current compliance
[:SENSe[1]]:VOLTage[:DC]:PROTection:TRIPped? - Query if in voltage compliance
[:SENSe[1]]:CURRent[:DC]:PROTection:RSYNchronize <b> - Sync current measure and compliance ranges
[:SENSe[1]]:VOLTage[:DC]:PROTection:RSYNchronize <b> - Sync voltage measure and compliance ranges
[:SENSe[1]]:CURRent[:DC]:PROTection:RSYNchronize? - Query current range sync state    
[:SENSe[1]]:VOLTage[:DC]:PROTection:RSYNchronize? - Query voltage range sync state    
[:SENSe[1]]:RESistance:MODE <name> - Select ohms mode (MANual, AUTO)
[:SENSe[1]]:RESistance:MODE? - Query ohms mode    
[:SENSe[1]]:RESistance:OCOMpensated <b> - Enable/disable offset-compensated ohms
[:SENSe[1]]:RESistance:OCOMpensated? - Query state of offset-compensated ohms    
[:SENSe[1]]:CURRent[:DC]:RANGe:HOLDoff <b> - Enable/disable current range holdoff
[:SENSe[1]]:CURRent[:DC]:RANGe:HOLDoff? - Query current range holdoff state    
[:SENSe[1]]:CURRent[:DC]:RANGe:HOLDoff:DELay <NRf> - Set holdoff delay
[:SENSe[1]]:CURRent[:DC]:RANGe:HOLDoff:DELay? - Query holdoff delay    
[:SENSe[1]]:AVERage:TCONtrol <name> - Specify filter type (MOVing, REPeat)
[:SENSe[1]]:AVERage:TCONtrol? - Query filter type    
[:SENSe[1]]:AVERage:COUNt <n> - Specify filter count (1-100)
[:SENSe[1]]:AVERage:COUNt? - Query filter count    
[:SENSe[1]]:AVERage[:STATe] <b> - Enable/disable filter
[:SENSe[1]]:AVERage[:STATe]? - Query state of filter    
SOURce Subsystem
SOURce[1]

:SOURce[1]:CLEar[:IMMediate] - Turn source output off
:SOURce[1]:CLEar:AUTO <b> - Enable/disable auto output-off
:SOURce[1]:CLEar:AUTO? - Query state of auto output-off    
:SOURce[1]:CLEar:AUTO:MODE <name> - Select auto output-off mode (ALWays, TCOunt)
:SOURce[1]:CLEar:AUTO:MODE? - Query auto output-off mode    
:SOURce[1]:FUNCtion:SHAPe <name> - (Model 2430 Only) Select output mode (DC, PULSe)
:SOURce[1]:FUNCtion:SHAPe? - Query output mode    
:SOURce[1]:FUNCtion[:MODE] <name> - Select source mode (VOLT, CURR, MEM)
:SOURce[1]:FUNCtion[:MODE]? - Query source mode    
:SOURce[1]:CURRent:MODE <name> - Select DC sourcing mode for I-Source (FIX, LIST, SWE)
:SOURce[1]:CURRent:MODE? - Query I-Source DC mode    
:SOURce[1]:VOLTage:MODE <name> - Select DC sourcing mode for V-Source (FIX, LIST, SWE)
:SOURce[1]:VOLTage:MODE? - Query V-Source DC mode    
:SOURce[1]:CURRent:RANGe <n>|UP|DOWN - Select range for I-Source
:SOURce[1]:CURRent:RANGe? - Query I-Source range    
:SOURce[1]:VOLTage:RANGe <n>|UP|DOWN - Select range for V-Source
:SOURce[1]:VOLTage:RANGe? - Query V-Source range    
:SOURce[1]:CURRent:RANGe:AUTO <b> - Select auto range for I-Source
:SOURce[1]:CURRent:RANGe:AUTO? - Query I-Source auto range state    
:SOURce[1]:VOLTage:RANGe:AUTO <b> - Select auto range for V-Source
:SOURce[1]:VOLTage:RANGe:AUTO? - Query V-Source auto range state    
:SOURce[1]:CURRent[:LEVel][:IMMediate][:AMPLitude] <n> - Set fixed I-Source amplitude immediately
:SOURce[1]:CURRent[:LEVel][:IMMediate][:AMPLitude]? - Query I-Source amplitude    
:SOURce[1]:VOLTage[:LEVel][:IMMediate][:AMPLitude] <n> - Set fixed V-Source amplitude immediately
:SOURce[1]:VOLTage[:LEVel][:IMMediate][:AMPLitude]? - Query V-Source amplitude    
:SOURce[1]:CURRent[:LEVel]:TRIGgered[:AMPLitude] <n> - Set fixed I-Source amplitude when triggered
:SOURce[1]:CURRent[:LEVel]:TRIGgered[:AMPLitude]? - Query triggered I-Source amplitude    
:SOURce[1]:VOLTage[:LEVel]:TRIGgered[:AMPLitude] <n> - Set fixed V-Source amplitude when triggered
:SOURce[1]:VOLTage[:LEVel]:TRIGgered[:AMPLitude]? - Query triggered V-Source amplitude    
:SOURce[1]:VOLTage:PROTection[:LEVel] <n> - Set voltage protection limit for V-Source
:SOURce[1]:VOLTage:PROTection[:LEVel]? - Query voltage protection limit    
:SOURce[1]:VOLTage:PROTection:TRIPped? - Query if voltage limit detected    
:SOURce[1]:DELay <n> - Manually set source delay
:SOURce[1]:DELay? - Query source delay    
:SOURce[1]:DELay:AUTO <b> - Enable/disable auto source delay
:SOURce[1]:DELay:AUTO? - Query state of auto delay    
:SOURce[1]:SWEep:RANGing <name> - Select source ranging mode for sweeps (BEST, AUTO, FIX)
:SOURce[1]:SWEep:RANGing? - Query sweep source ranging mode    
:SOURce[1]:SWEep:SPACing <name> - Select sweep scale (LINear, LOGarithmic)
:SOURce[1]:SWEep:SPACing? - Query sweep scale    
:SOURce[1]:CURRent:STARt <n> - Specify start current level for sweep
:SOURce[1]:CURRent:STARt? - Query current sweep start level    
:SOURce[1]:VOLTage:STARt <n> - Specify start voltage level for sweep
:SOURce[1]:VOLTage:STARt? - Query voltage sweep start level    
:SOURce[1]:CURRent:STOP <n> - Specify stop current level for sweep
:SOURce[1]:CURRent:STOP? - Query current sweep stop level    
:SOURce[1]:VOLTage:STOP <n> - Specify stop voltage level for sweep
:SOURce[1]:VOLTage:STOP? - Query voltage sweep stop level    
:SOURce[1]:CURRent:CENTer <n> - Specify center point of current sweep
:SOURce[1]:CURRent:CENTer? - Query current sweep center point    
:SOURce[1]:VOLTage:CENTer <n> - Specify center point of voltage sweep
:SOURce[1]:VOLTage:CENTer? - Query voltage sweep center point    
:SOURce[1]:CURRent:SPAN <n> - Specify span of the current sweep
:SOURce[1]:CURRent:SPAN? - Query current sweep span    
:SOURce[1]:VOLTage:SPAN <n> - Specify span of the voltage sweep
:SOURce[1]:VOLTage:SPAN? - Query voltage sweep span    
:SOURce[1]:CURRent:STEP <n> - Specify step size for current sweep
:SOURce[1]:CURRent:STEP? - Query current sweep step size    
:SOURce[1]:VOLTage:STEP <n> - Specify step size for voltage sweep
:SOURce[1]:VOLTage:STEP? - Query voltage sweep step size    
:SOURce[1]:SWEep:POINts <n> - Set number of source-measure points for sweep
:SOURce[1]:SWEep:POINts? - Query number of sweep points    
:SOURce[1]:SWEep:DIRection <name> - Set direction of sweep (UP, DOWn)
:SOURce[1]:SWEep:DIRection? - Query sweep direction    
:SOURce[1]:SWEep:CABort <name> - Control abort on compliance (NEVer, EARLy, LATE)
:SOURce[1]:SWEep:CABort? - Query abort on compliance state    
:SOURce[1]:LIST:CURRent <NRf list> - Define I-Source list for custom sweep
:SOURce[1]:LIST:CURRent? - Query I-Source list    
:SOURce[1]:LIST:VOLTage <NRf list> - Define V-Source list for custom sweep
:SOURce[1]:LIST:VOLTage? - Query V-Source list    
:SOURce[1]:LIST:CURRent:APPend <NRf list> - Add value(s) to I-Source list
:SOURce[1]:LIST:VOLTage:APPend <NRf list> - Add value(s) to V-Source list
:SOURce[1]:LIST:CURRent:POINts? - Query length of I-Source list
:SOURce[1]:LIST:VOLTage:POINts? - Query length of V-Source list
:SOURce[1]:LIST:CURRent:STARt <n> - Set current list start point
:SOURce[1]:LIST:CURRent:STARt? - Query current list start point    
:SOURce[1]:LIST:VOLTage:STARt <n> - Set voltage list start point
:SOURce[1]:LIST:VOLTage:STARt? - Query voltage list start point    
:SOURce[1]:MEMory:SAVE <NRf> - Save current setup in specified source memory location (1-100)
:SOURce[1]:MEMory:RECall <NRf> - Recall setup from specified source memory location (1-100)
:SOURce[1]:MEMory:POINts <NRf> - Specify number of sweep points for source memory sweep (1-100)
:SOURce[1]:MEMory:POINts? - Query number of source memory sweep points    
:SOURce[1]:MEMory:STARt <NRf> - Select start location for source memory sweep (1-100)
:SOURce[1]:MEMory:STARt? - Query source memory sweep start location    
:SOURce[1]:CURRent[:LEVel]:TRIGgered:SFACtor <n> - Set current scaling factor for source memory sweep
:SOURce[1]:CURRent[:LEVel]:TRIGgered:SFACtor? - Query current scaling factor    
:SOURce[1]:VOLTage[:LEVel]:TRIGgered:SFACtor <n> - Set voltage scaling factor for source memory sweep
:SOURce[1]:VOLTage[:LEVel]:TRIGgered:SFACtor? - Query voltage scaling factor    
:SOURce[1]:CURRent[:LEVel]:TRIGgered:SFACtor:STATe <b> - Enable/disable current scaling factor
:SOURce[1]:CURRent[:LEVel]:TRIGgered:SFACtor:STATe? - Query current scaling factor state    
:SOURce[1]:VOLTage[:LEVel]:TRIGgered:SFACtor:STATe <b> - Enable/disable voltage scaling factor
:SOURce[1]:VOLTage[:LEVel]:TRIGgered:SFACtor:STATe? - Query voltage scaling factor state    
:SOURce[1]:SOAK <NRf> - Set first sweep point soak time for MULTIPLE auto range mode
:SOURce[1]:SOAK? - Query soak time    
:SOURce[1]:PULSe:WIDTh <n> - (Model 2430 Only) Set pulse width
:SOURce[1]:PULSe:WIDTh? - Query pulse width    
:SOURce[1]:PULSe:DELay <n> - (Model 2430 Only) Set pulse delay
:SOURce[1]:PULSe:DELay? - Query pulse delay  SOURce2   
:SOURce2:BSIZe <n> - Set Digital I/O port bit size (3 or 4)
:SOURce2:BSIZe? - Query Digital I/O bit size    
:SOURce2:TTL[:LEVel][:DEFault] <NRf>|<NDN> - Specify digital output pattern
:SOURce2:TTL[:LEVel][:DEFault]? - Query default output pattern    
:SOURce2:TTL:ACTual? - Read actual output pattern    
:SOURce2:TTL4:MODE <name> - Set Digital I/O line 4 mode (EOTest, BUSY)
:SOURce2:TTL4:MODE? - Query Digital I/O line 4 mode    
:SOURce2:TTL4:BSTate <b> - Set BUSY and EOT polarity (HI/LO)
:SOURce2:TTL4:BSTate? - Query BUSY and EOT polarity    
:SOURce2:CLEar[:IMMediate] - Clear digital output lines to default pattern
:SOURce2:CLEar:AUTO <b> - Enable/disable digital output auto clear
:SOURce2:CLEar:AUTO? - Query state of auto-clear    
:SOURce2:CLEar:AUTO:DELay <n> - Specify pulse-width delay for pass/fail pattern before auto-clear
:SOURce2:CLEar:AUTO:DELay? - Query auto-clear delay    
STATus Subsystem

:STATus:MEASurement[:EVENt]? - Read Measurement Event Register
:STATus:QUEStionable[:EVENt]? - Read Questionable Event Register
:STATus:OPERation[:EVENt]? - Read Operation Event Register
:STATus:MEASurement:ENABle <NDN>|<NRf> - Program Measurement Event Enable Register
:STATus:MEASurement:ENABle? - Read Measurement Event Enable Register    
:STATus:QUEStionable:ENABle <NDN>|<NRf> - Program Questionable Event Enable Register
:STATus:QUEStionable:ENABle? - Read Questionable Event Enable Register    
:STATus:OPERation:ENABle <NDN>|<NRf> - Program Operation Event Enable Register
:STATus:OPERation:ENABle? - Read Operation Event Enable Register    
:STATus:MEASurement:CONDition? - Read Measurement Condition Register
:STATus:QUEStionable:CONDition? - Read Questionable Condition Register
:STATus:OPERation:CONDition? - Read Operation Condition Register
:STATus:PRESet - Return status registers to default states
:STATus:QUEue[:NEXT]? - Read the most recent error message from the queue
:STATus:QUEue:ENABle <list> - Enable specified error/status messages for Error Queue
:STATus:QUEue:ENABle? - Query list of enabled messages    
:STATus:QUEue:DISable <list> - Disable specified messages from Error Queue
:STATus:QUEue:DISable? - Query list of disabled messages    
:STATus:QUEue:CLEar - Clears all messages from Error Queue
SYSTem Subsystem

:SYSTem:PRESet - Return to :SYSTem:PRESet defaults (bench defaults)
:SYSTem:POSetup <name> - Program power-on defaults (RST, PRESet, SAV0-4)
:SYSTem:POSetup? - Query power-on setup    
:SYSTem:VERSion? - Query SCPI version
:SYSTem:ERRor[:NEXT]? - Read and clear oldest error message
:SYSTem:ERRor:ALL? - Read and clear all error messages
:SYSTem:ERRor:COUNt? - Return the number of errors in the queue
:SYSTem:ERRor:CODE[:NEXT]? - Read and clear oldest error code only
:SYSTem:ERRor:CODE:ALL? - Read and clear all error codes only
:SYSTem:ERRor:CLEar - Clears messages from Error Queue
:SYSTem:RSENse <b> - Enable/disable remote sensing
:SYSTem:RSENse? - Query state of remote sensing    
:SYSTem:CCHeck <b> - Enable/disable contact check
:SYSTem:CCHeck? - Query state of contact check    
:SYSTem:CCHeck:RESistance <NRf> - Set contact check threshold resistance
:SYSTem:CCHeck:RESistance? - Query contact check threshold resistance    
:SYSTem:KEY <n> - Simulate key-press (1-32)
:SYSTem:KEY? - Query the last pressed key    
:SYSTem:GUARd <name> - Select guard mode (OHMS, CABLe)
:SYSTem:GUARd? - Query guard mode    
:SYSTem:BEEPer[:IMMediate] <freq, time> - Beep at specified frequency and duration
:SYSTem:BEEPer:STATe <b> - Enable/disable beeper
:SYSTem:BEEPer:STATe? - Query state of beeper    
:SYSTem:AZERo[:STATe] <name> - Control auto zero (ON, OFF, ONCE)
:SYSTem:AZERo[:STATe]? - Query auto zero state    
:SYSTem:AZERo:CACHing[:STATe] <b> - Enable/disable NPLC caching
:SYSTem:AZERo:CACHing[:STATe]? - Query NPLC caching state    
:SYSTem:AZERo:CACHing:REFResh - Update NPLC cache values
:SYSTem:AZERo:CACHing:RESet - Clear NPLC values from cache
:SYSTem:AZERo:CACHing:NPLCycles? - Return list of NPLC values in cache
:SYSTem:LFRequency <freq> - Select line frequency (50, 60)
:SYSTem:LFRequency? - Query line frequency    
:SYSTem:LFRequency:AUTO <b> - Enable/disable auto frequency detection
:SYSTem:LFRequency:AUTO? - Query state of auto frequency detection    
:SYSTem:TIME? - Query timestamp
:SYSTem:TIME:RESet - Reset timestamp to zero
:SYSTem:TIME:RESet:AUTO <b> - Enable/disable timestamp reset when exiting idle
:SYSTem:TIME:RESet:AUTO? - Query auto timestamp reset state    
:SYSTem:MEMory:INITialize - Initialize battery backed RAM
:SYSTem:LOCal - (RS-232 Only) Take unit out of remote
:SYSTem:RWLock <b> - (RS-232 Only) Enable/disable local lockout
:SYSTem:RWLock? - Query local lockout state    
:SYSTem:RCMode <name> - Set auto range on compliance mode (SINGle, MULTiple)
:SYSTem:RCMode? - Query auto range on compliance mode    
:SYSTem:MEP[:STATe]? - Query GPIB protocol (1=SCPI, 0=488.1)
:SYSTem:MEP:HOLDoff <b> - (488.1 Only) Enable/disable NDAC hold-off
TRACe Subsystem

:TRACe:DATA? - Read contents of the buffer (data store)
:TRACe:CLEar - Clear readings from buffer
:TRACe:FREE? - Query available buffer memory status
:TRACe:POINts <NRf> - Specify size of buffer (1-2500)
:TRACe:POINts? - Query buffer size    
:TRACe:POINts:ACTual? - Query number of readings stored in the buffer
:TRACe:FEED <name> - Specify source of readings for buffer (SENSe[1], CALC[1], CALC2)
:TRACe:FEED? - Query buffer feed source    
:TRACe:FEED:CONTrol <name> - Start or stop buffer storage (NEXT, NEVer)
:TRACe:FEED:CONTrol? - Query buffer control mode    
:TRACe:TSTamp:FORMat <name> - Select timestamp format for buffer (ABSolute, DELTa)
:TRACe:TSTamp:FORMat? - Query timestamp format    
TRIGger Subsystem

:TRIGger:CLEar - Clear any pending input triggers
:INITiate[:IMMediate] - Take SourceMeter out of idle state to start measurements
:ABORt - Abort operation and return to idle state
:ARM[:SEQuence[1]][:LAYer[1]]:COUNt <n> - Set arm count (1-2500 or INF)
:ARM[:SEQuence[1]][:LAYer[1]]:COUNt? - Query arm count    
:TRIGger[:SEQuence[1]]:COUNt <n> - Set trigger count (1-2500)
:TRIGger[:SEQuence[1]]:COUNt? - Query trigger count    
:ARM[:SEQuence[1]][:LAYer[1]]:SOURce <name> - Specify arm event control source (IMM, TIM, MAN, BUS, TLINk, NST, PST, BST)
:ARM[:SEQuence[1]][:LAYer[1]]:SOURce? - Query arm control source    
:TRIGger[:SEQuence[1]]:SOURce <name> - Specify trigger event control source (IMM, TLINk)
:TRIGger[:SEQuence[1]]:SOURce? - Query trigger control source    
:ARM[:SEQuence[1]][:LAYer[1]]:TIMer <n> - Set interval for arm layer timer
:ARM[:SEQuence[1]][:LAYer[1]]:TIMer? - Query timer interval    
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:DIRection <name> - Control arm bypass (SOURce, ACCeptor)
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:DIRection? - Query state of arm bypass    
:TRIGger[:SEQuence[1]][:TCONfigure]:DIRection <name> - Control trigger bypass (SOURce, ACCeptor)
:TRIGger[:SEQuence[1]][:TCONfigure]:DIRection? - Query state of trigger bypass    
:TRIGger[:SEQuence[1]]:DELay <n> - Set trigger layer delay
:TRIGger[:SEQuence[1]]:DELay? - Query trigger delay    
:TRIGger[:SEQuence[1]][:TCONfigure][:ASYNchronous]:INPut <event list> - Enable trigger layer event detectors (SOURce, DELay, SENSe, NONE)
:TRIGger[:SEQuence[1]][:TCONfigure][:ASYNchronous]:INPut? - Query enabled trigger layer event detectors    
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:ILINe <NRf> - Select arm layer input line (1-4)
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:ILINe? - Query arm layer input line    
:TRIGger[:SEQuence[1]][:TCONfigure]:ILINe <NRf> - Select trigger layer input line (1-4)
:TRIGger[:SEQuence[1]][:TCONfigure]:ILINe? - Query trigger layer input line    
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:OLINe <NRf> - Select arm layer output line (1-4)
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:OLINe? - Query arm layer output line    
:TRIGger[:SEQuence[1]][:TCONfigure]:OLINe <NRf> - Select trigger layer output line (1-4)
:TRIGger[:SEQuence[1]][:TCONfigure]:OLINe? - Query trigger layer output line    
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:OUTPut <event list> - Select arm layer output trigger events (TENTer, TEXit, NONE)
:ARM[:SEQuence[1]][:LAYer[1]][:TCONfigure]:OUTPut? - Query arm layer output trigger events    
:TRIGger[:SEQuence[1]][:TCONfigure]:OUTPut <event list> - Select trigger layer output trigger events (SOURce, DELay, SENSe, NONE)
:TRIGger[:SEQuence[1]][:TCONfigure]:OUTPut? - Query trigger layer output trigger events    
Contact Check Commands (Appendix F) 
:SYSTem:CCHeck <b> - Enable/disable contact check
:SYSTem:CCHeck:RESistance <NRf> - Set contact check threshold resistance
:CALCulate2:LIMit4:STATe <b> - Enable/disable Limit 4 (contact check) test
:CALCulate2:LIMit4:SOURce2 <NRf>|<NDN> - Specify Limit 4 fail bit pattern
:TRIGger:SEQuence2:SOURce <name> - Enable/disable contact check event detection (CCHeck/IMMediate)
:TRIGger:SEQuence2:TOUT <NRf> - Specify contact check timeout