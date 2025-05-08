// --- Pin Definitions ---

// Group 1: MUX_BE12 (Pair 1: 2x 74LS595 = 16 bits for 4 MUXs)
// Controls MUX_BE12_1, MUX_BE12_2, MUX_BE12_3, MUX_BE12_4
const int DATA_PIN_MUX_BE12 = 3;   // Example: D3
const int CLOCK_PIN_MUX_BE12 = 4;  // Example: D4
const int LATCH_PIN_MUX_BE12 = 5;  // Example: D5

// Group 2: MUX_BE34 (Pair 2: 2x 74LS595 = 16 bits for 4 MUXs)
// Controls MUX_BE34_1, MUX_BE34_2, MUX_BE34_3, MUX_BE34_4
const int DATA_PIN_MUX_BE34 = 6;   // Example: D6
const int CLOCK_PIN_MUX_BE34 = 7;  // Example: D7
const int LATCH_PIN_MUX_BE34 = 8;  // Example: D8

// Group 3: ENABLE (Pair 3: 2x 74LS595 = 16 bits for 16 enables/devices)
const int DATA_PIN_ENABLE = 9; // Example: D9
const int CLOCK_PIN_ENABLE = 10;// Example: D10
const int LATCH_PIN_ENABLE = 11;// Example: D11

// Group 4: MUX_TE (Single SR4: 1x 74LS595 = 8 bits for 2 MUXs)
// Controls MUX_TE1, MUX_TE2
const int DATA_PIN_MUX_TE = 12;  // Example: D12
const int CLOCK_PIN_MUX_TE = 13; // Example: D13
const int LATCH_PIN_MUX_TE = A0; // Example: A0 (Analog pins can be used as digital)

/*
   General Wiring Notes for each 74LS595 chain:
   - DATA_PIN_GROUP -> SER (DS, pin 14) of the FIRST 74LS595 in that group.
   - For 16-bit pairs: QH' (Q7S, pin 9) of the FIRST 74LS595 -> SER (DS, pin 14) of the SECOND 74LS595.
   - CLOCK_PIN_GROUP -> SHCP (SRCLK, pin 11) of ALL 74LS595s WITHIN THAT GROUP.
   - LATCH_PIN_GROUP -> STCP (RCLK, pin 12) of ALL 74LS595s WITHIN THAT GROUP.
   - OE (Output Enable, pin 13) of ALL 74LS595s to GND.
   - MR (Master Reset, pin 10) of ALL 74LS595s to VCC (5V).
   - Provide VCC (5V) and GND to all chips.

   MUX Output Bit Mapping for 16-bit MUX groups (MUX_BE12, MUX_BE34):
   Input Value (16-bit): [M4_S3 M4_S2 M4_S1 M4_S0  M3_S3 M3_S2 M3_S1 M3_S0  M2_S3 M2_S2 M2_S1 M2_S0  M1_S3 M1_S2 M1_S1 M1_S0]
   - Bits 0-3:   MUXn_1 select lines
   - Bits 4-7:   MUXn_2 select lines
   - Bits 8-11:  MUXn_3 select lines
   - Bits 12-15: MUXn_4 select lines
   (This corresponds to: lowByte for MUX1/MUX2, highByte for MUX3/MUX4 when sent to write16BitsToChain)

   MUX Output Bit Mapping for 8-bit MUX group (MUX_TE):
   Input Value (8-bit): [M2_S3 M2_S2 M2_S1 M2_S0  M1_S3 M1_S2 M1_S1 M1_S0]
   - Bits 0-3: MUX_TE1 select lines
   - Bits 4-7: MUX_TE2 select lines
*/

void setup() {
  // Initialize all control pins as outputs
  pinMode(DATA_PIN_MUX_BE12, OUTPUT);
  pinMode(CLOCK_PIN_MUX_BE12, OUTPUT);
  pinMode(LATCH_PIN_MUX_BE12, OUTPUT);

  pinMode(DATA_PIN_MUX_BE34, OUTPUT);
  pinMode(CLOCK_PIN_MUX_BE34, OUTPUT);
  pinMode(LATCH_PIN_MUX_BE34, OUTPUT);

  pinMode(DATA_PIN_ENABLE, OUTPUT);
  pinMode(CLOCK_PIN_ENABLE, OUTPUT);
  pinMode(LATCH_PIN_ENABLE, OUTPUT);

  pinMode(DATA_PIN_MUX_TE, OUTPUT);
  pinMode(CLOCK_PIN_MUX_TE, OUTPUT);
  pinMode(LATCH_PIN_MUX_TE, OUTPUT);

  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect.
  }
  Serial.println("Extended 74LS595 Control Sketch Initialized (Unified MUX Input).");
  printGeneralUsage();

  // Clear all shift register chains
  write16BitsToChain(DATA_PIN_MUX_BE12, CLOCK_PIN_MUX_BE12, LATCH_PIN_MUX_BE12, 0x0000);
  write16BitsToChain(DATA_PIN_MUX_BE34, CLOCK_PIN_MUX_BE34, LATCH_PIN_MUX_BE34, 0x0000);
  write16BitsToChain(DATA_PIN_ENABLE, CLOCK_PIN_ENABLE, LATCH_PIN_ENABLE, 0x0000);
  write8BitsToChain(DATA_PIN_MUX_TE, CLOCK_PIN_MUX_TE, LATCH_PIN_MUX_TE, 0x00);
  Serial.println("All shift registers cleared.");
  printGeneralUsage();
}

void loop() {
  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');
    inputString.trim();

    Serial.print("Received: \"");
    Serial.print(inputString);
    Serial.println("\"");

    if (inputString.startsWith("muxBE12 ")) {
      String value = inputString.substring(String("muxBE12 ").length());
      parseMux4Value(value, DATA_PIN_MUX_BE12, CLOCK_PIN_MUX_BE12, LATCH_PIN_MUX_BE12, "MUX_BE12");
    } else if (inputString.startsWith("muxBE34 ")) {
      String value = inputString.substring(String("muxBE34 ").length());
      parseMux4Value(value, DATA_PIN_MUX_BE34, CLOCK_PIN_MUX_BE34, LATCH_PIN_MUX_BE34, "MUX_BE34");
    } else if (inputString.startsWith("ENABLE ")) {
      String value = inputString.substring(String("ENABLE ").length());
      parseEnableValue(value, DATA_PIN_ENABLE, CLOCK_PIN_ENABLE, LATCH_PIN_ENABLE);
    } else if (inputString.startsWith("muxTE ")) {
      String value = inputString.substring(String("muxTE ").length());
      parseMux2Value(value, DATA_PIN_MUX_TE, CLOCK_PIN_MUX_TE, LATCH_PIN_MUX_TE, "MUX_TE");
    } else if (inputString.length() > 0) {
      Serial.print("Error: Unknown command prefix in '");
      Serial.print(inputString);
      Serial.println("'.");
      printGeneralUsage();
    }
  }
}

void printGeneralUsage() {
  Serial.println("--- Available Commands ---");
  Serial.println("muxBE12 VALUE     (e.g., muxBE12 0xFFFF or 0b0001001000110100)");
  Serial.println("muxBE34 VALUE     (e.g., muxBE34 255)");
  Serial.println("ENABLE VALUE      (e.g., ENABLE 0xFFFF or 65535 or 0b1010...)");
  Serial.println("muxTE VALUE       (e.g., muxTE 0xAB or 0b10101011 or 171)");
  Serial.println("VALUE can be decimal, 0xHEX, or 0bBINARY.");
  Serial.println("For muxBE12/34, VALUE is 16-bit. For muxTE, VALUE is 8-bit.");
  Serial.println("--------------------------");
}

/**
 * @brief Sends 16 bits of data to a specified pair of daisy-chained 74LS595s.
 */
void write16BitsToChain(int dataPin, int clockPin, int latchPin, uint16_t data) {
  byte highByte = (data >> 8) & 0xFF; // For SR2 (Muxes 3 & 4)
  byte lowByte = data & 0xFF;         // For SR1 (Muxes 1 & 2)

  digitalWrite(latchPin, LOW);
  shiftOut(dataPin, clockPin, MSBFIRST, highByte);
  shiftOut(dataPin, clockPin, MSBFIRST, lowByte);
  digitalWrite(latchPin, HIGH);
}

/**
 * @brief Sends 8 bits of data to a specified single 74LS595.
 */
void write8BitsToChain(int dataPin, int clockPin, int latchPin, byte data) {
  digitalWrite(latchPin, LOW);
  shiftOut(dataPin, clockPin, MSBFIRST, data);
  digitalWrite(latchPin, HIGH);
}

/**
 * @brief Parses a single 16-bit value for a group of 4 MUXes.
 * Used for MUX_BE12 and MUX_BE34 groups.
 * The 16-bit value directly maps to the 4 MUX select lines (4 bits each).
 * Bits 0-3: MUX1, Bits 4-7: MUX2, Bits 8-11: MUX3, Bits 12-15: MUX4.
 */
void parseMux4Value(String valueInput, int dataPin, int clockPin, int latchPin, const String& muxGroupName) {
  valueInput.trim();
  uint16_t muxData = 0;
  bool parseError = false;

  if (valueInput.startsWith("0x")) {
    muxData = strtoul(valueInput.substring(2).c_str(), NULL, 16);
  } else if (valueInput.startsWith("0b")) {
    String binVal = valueInput.substring(2);
    if (binVal.length() > 16) { Serial.print("Error ("); Serial.print(muxGroupName); Serial.println("): Binary string too long (max 16 bits)."); parseError = true; }
    else { muxData = strtoul(binVal.c_str(), NULL, 2); }
  } else { // Try decimal
    bool isNumber = true;
    for (int i = 0; i < valueInput.length(); i++) {
      if (!isDigit(valueInput.charAt(i))) { isNumber = false; break; }
    }
    if (isNumber && valueInput.length() > 0) {
      unsigned long tempVal = strtoul(valueInput.c_str(), NULL, 10);
      if (tempVal > 65535) { Serial.print("Error ("); Serial.print(muxGroupName); Serial.println("): Decimal value out of 16-bit range (0-65535)."); parseError = true; }
      else { muxData = (uint16_t)tempVal; }
    } else {
      Serial.print("Error ("); Serial.print(muxGroupName); Serial.println("): Invalid format. Use decimal, 0xHEX, or 0bBINARY.");
      parseError = true;
    }
  }
  
  if (parseError) { printGeneralUsage(); return; }

  // For display purposes, extract individual MUX select values
  byte sel1 = (muxData >> 0) & 0x0F;  // MUX1 (bits 0-3 of combinedData)
  byte sel2 = (muxData >> 4) & 0x0F;  // MUX2 (bits 4-7 of combinedData)
  byte sel3 = (muxData >> 8) & 0x0F;  // MUX3 (bits 8-11 of combinedData)
  byte sel4 = (muxData >> 12) & 0x0F; // MUX4 (bits 12-15 of combinedData)

  Serial.print("Setting "); Serial.print(muxGroupName); Serial.print(" from value: "); Serial.println(valueInput);
  Serial.print("  Interpreted MUX selects -> M1:"); Serial.print(sel1);
  Serial.print(", M2:"); Serial.print(sel2);
  Serial.print(", M3:"); Serial.print(sel3);
  Serial.print(", M4:"); Serial.println(sel4);

  Serial.print("Sending 16-bit data: 0b");
  for (int i = 15; i >= 0; i--) { Serial.print(bitRead(muxData, i)); if (i % 4 == 0 && i > 0) Serial.print(" ");}
  char hexString[5]; sprintf(hexString, "%04X", muxData);
  Serial.print(" (0x"); Serial.print(hexString); Serial.println(")");

  write16BitsToChain(dataPin, clockPin, latchPin, muxData);
  Serial.print(muxGroupName); Serial.println(" values updated.");
  printGeneralUsage();
}

/**
 * @brief Parses a single 8-bit value for a group of 2 MUXes.
 * Used for MUX_TE group.
 * The 8-bit value directly maps to the 2 MUX select lines (4 bits each).
 * Bits 0-3: MUX1, Bits 4-7: MUX2.
 */
void parseMux2Value(String valueInput, int dataPin, int clockPin, int latchPin, const String& muxGroupName) {
  valueInput.trim();
  byte muxData = 0;
  bool parseError = false;

  if (valueInput.startsWith("0x")) {
    muxData = strtoul(valueInput.substring(2).c_str(), NULL, 16);
  } else if (valueInput.startsWith("0b")) {
    String binVal = valueInput.substring(2);
    if (binVal.length() > 8) { Serial.print("Error ("); Serial.print(muxGroupName); Serial.println("): Binary string too long (max 8 bits)."); parseError = true; }
    else { muxData = strtoul(binVal.c_str(), NULL, 2); }
  } else { // Try decimal
    bool isNumber = true;
    for (int i = 0; i < valueInput.length(); i++) {
      if (!isDigit(valueInput.charAt(i))) { isNumber = false; break; }
    }
    if (isNumber && valueInput.length() > 0) {
      unsigned long tempVal = strtoul(valueInput.c_str(), NULL, 10);
      if (tempVal > 255) { Serial.print("Error ("); Serial.print(muxGroupName); Serial.println("): Decimal value out of 8-bit range (0-255)."); parseError = true; }
      else { muxData = (byte)tempVal; }
    } else {
      Serial.print("Error ("); Serial.print(muxGroupName); Serial.println("): Invalid format. Use decimal, 0xHEX, or 0bBINARY.");
      parseError = true;
    }
  }

  if (parseError) { printGeneralUsage(); return; }

  // For display purposes, extract individual MUX select values
  byte sel1 = (muxData >> 0) & 0x0F; // MUX1 (bits 0-3)
  byte sel2 = (muxData >> 4) & 0x0F; // MUX2 (bits 4-7)

  Serial.print("Setting "); Serial.print(muxGroupName); Serial.print(" from value: "); Serial.println(valueInput);
  Serial.print("  Interpreted MUX selects -> M1:"); Serial.print(sel1);
  Serial.print(", M2:"); Serial.println(sel2);

  Serial.print("Sending 8-bit data: 0b");
  for (int i = 7; i >= 0; i--) { Serial.print(bitRead(muxData, i)); if (i % 4 == 0 && i > 0) Serial.print(" ");}
  char hexString[3]; sprintf(hexString, "%02X", muxData);
  Serial.print(" (0x"); Serial.print(hexString); Serial.println(")");

  write8BitsToChain(dataPin, clockPin, latchPin, muxData);
  Serial.print(muxGroupName); Serial.println(" values updated.");
  printGeneralUsage();
}

/**
 * @brief Parses a 16-bit value (decimal, hex 0x, or binary 0b) for the ENABLE group.
 */
void parseEnableValue(String valueInput, int dataPin, int clockPin, int latchPin) {
  valueInput.trim();
  uint16_t enableData = 0;
  bool parseError = false;

  if (valueInput.startsWith("0x")) {
    enableData = strtoul(valueInput.substring(2).c_str(), NULL, 16);
  } else if (valueInput.startsWith("0b")) {
    String binVal = valueInput.substring(2);
    if (binVal.length() > 16) { Serial.println("Error (ENABLE): Binary string too long (max 16 bits)."); parseError = true; }
    else { enableData = strtoul(binVal.c_str(), NULL, 2); }
  } else { // Try decimal
    bool isNumber = true;
    for (int i = 0; i < valueInput.length(); i++) {
      if (!isDigit(valueInput.charAt(i))) { isNumber = false; break; }
    }
    if (isNumber && valueInput.length() > 0) {
      unsigned long tempVal = strtoul(valueInput.c_str(), NULL, 10);
      if (tempVal > 65535) { Serial.println("Error (ENABLE): Decimal value out of 16-bit range (0-65535)."); parseError = true; }
      else { enableData = (uint16_t)tempVal; }
    } else {
      Serial.println("Error (ENABLE): Invalid format. Use decimal, 0xHEX, or 0bBINARY.");
      parseError = true;
    }
  }
  
  if (parseError) { printGeneralUsage(); return; }

  Serial.print("Setting ENABLE - Value: "); Serial.println(valueInput);
  Serial.print("Sending 16-bit data: 0b");
  for (int i = 15; i >= 0; i--) { Serial.print(bitRead(enableData, i)); if (i % 4 == 0 && i > 0) Serial.print(" ");}
  char hexString[5]; sprintf(hexString, "%04X", enableData);
  Serial.print(" (0x"); Serial.print(hexString); Serial.println(")");

  write16BitsToChain(dataPin, clockPin, latchPin, enableData);
  Serial.println("ENABLE values updated.");
  printGeneralUsage();
}
