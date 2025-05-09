# Documentation: Arduino Multi-Group 74LS595 Control

## 1. Introduction

This document provides detailed information about the Arduino sketch (`arduino_74ls595_mux_extended`) designed to control multiple groups of 74LS595 shift registers. These shift registers are used to manage:
* Two groups of four 16-channel multiplexers each (named MUX_BE12 and MUX_BE34).
* One group of 16 general-purpose digital enable lines (named ENABLE).
* One group of two 16-channel multiplexers (named MUX_TE).

The sketch allows users to send commands via the Arduino's serial interface to set the state of these multiplexers and enable lines.

## 2. Hardware Requirements & Setup

### 2.1. Components
* **Arduino Mega (or compatible):** The sketch is designed for a board with sufficient digital pins.
* **74LS595 Shift Registers:**
    * Two pairs (4 total) for MUX_BE12 and MUX_BE34 (each pair forms a 16-bit register).
    * One pair (2 total) for the ENABLE group (forms a 16-bit register).
    * One single 74LS595 for the MUX_TE group (forms an 8-bit register).
* **Multiplexers:**
    * Eight 16-channel analog/digital multiplexers for MUX_BE12 and MUX_BE34. These are the 4 BE layers
    * Two 16-channel analog/digital multiplexers for MUX_TE. this is the TE pads. 
* **Connecting Wires**
* **Power Supply (5V)** for the shift registers and multiplexers.

### 2.2. Arduino Pin Connections

The sketch defines specific Arduino pins for controlling each group of shift registers. **You may need to adjust these pin numbers in the code to match your wiring.**

**Group 1: MUX_BE12** (Controls four 16-channel MUXes)
* Data Pin (SER of first 595): `DATA_PIN_MUX_BE12` (Example: D3)
* Clock Pin (SHCP of both 595s): `CLOCK_PIN_MUX_BE12` (Example: D4)
* Latch Pin (STCP of both 595s): `LATCH_PIN_MUX_BE12` (Example: D5)

**Group 2: MUX_BE34** (Controls four 16-channel MUXes)
* Data Pin (SER of first 595): `DATA_PIN_MUX_BE34` (Example: D6)
* Clock Pin (SHCP of both 595s): `CLOCK_PIN_MUX_BE34` (Example: D7)
* Latch Pin (STCP of both 595s): `LATCH_PIN_MUX_BE34` (Example: D8)

**Group 3: ENABLE** (Controls 16 enable/device lines)
* Data Pin (SER of first 595): `DATA_PIN_ENABLE` (Example: D9)
* Clock Pin (SHCP of both 595s): `CLOCK_PIN_ENABLE` (Example: D10)
* Latch Pin (STCP of both 595s): `LATCH_PIN_ENABLE` (Example: D11)

**Group 4: MUX_TE** (Controls two 16-channel MUXes)
* Data Pin (SER of the 595): `DATA_PIN_MUX_TE` (Example: D12)
* Clock Pin (SHCP of the 595): `CLOCK_PIN_MUX_TE` (Example: D13)
* Latch Pin (STCP of the 595): `LATCH_PIN_MUX_TE` (Example: A0 - Analog pin A0 used as digital)

### 2.3. 74LS595 Shift Register Wiring (General for each group)
* **SER (DS, Pin 14):** Connect to the corresponding `DATA_PIN_GROUP` on the Arduino for the *first* shift register in a chain.
* **QH' (Q7S, Pin 9):** For 16-bit pairs (MUX_BE12, MUX_BE34, ENABLE), connect the QH' of the *first* 74LS595 to the SER (Pin 14) of the *second* 74LS595 in that pair. This daisy-chains them.
* **SHCP (SRCLK, Pin 11):** Connect to the corresponding `CLOCK_PIN_GROUP` on the Arduino. All 595s *within the same group* share this clock line.
* **STCP (RCLK, Pin 12):** Connect to the corresponding `LATCH_PIN_GROUP` on the Arduino. All 595s *within the same group* share this latch line.
* **OE (Output Enable, Pin 13):** Connect to **GND** (Ground) to enable the outputs of the shift register.
* **MR (Master Reset, Pin 10):** Connect to **VCC (5V)** for normal operation (to prevent accidental reset).
* **VCC (Pin 16):** Connect to 5V.
* **GND (Pin 8):** Connect to Ground.
* **Outputs (Q0-Q7 or QA-QH):** These are the 8 output lines from each 74LS595.
    * For MUX groups, these connect to the select lines (S0, S1, S2, S3) of the multiplexers.
    * For the ENABLE group, these are your 16 individual enable/control lines.

### 2.4. Multiplexer Wiring
* **Select Lines (S0, S1, S2, S3):** Connect to the appropriate 4 output bits from the controlling shift register group.
* **Signal Input/Output (Common Pin):** This is the pin where the selected channel's signal will appear (or be input from).
* **Channel Pins (C0-C15):** These are the 16 channels you can select from.
* **Enable Pin (E or EN):** Typically, tie to GND to enable the multiplexer (refer to your MUX datasheet).
* **VCC and GND:** Connect to 5V and Ground as per the datasheet.

## 3. Software Overview

The Arduino sketch is structured to handle serial commands and update the shift registers accordingly.

### 3.1. Pin Definitions
At the beginning of the sketch, `const int` variables define the Arduino pins used for data, clock, and latch signals for each of the four control groups.

### 3.2. `setup()` Function
* **Pin Initialization:** Sets all defined control pins to `OUTPUT` mode.
* **Serial Communication:** Initializes serial communication at `9600` baud. It also prints an initial welcome message and usage instructions.
* **Register Clearing:** Calls `write16BitsToChain()` and `write8BitsToChain()` for each group, sending `0x0000` or `0x00` respectively. This ensures all outputs start in a known (LOW) state.

### 3.3. `loop()` Function
* **Serial Check:** Continuously checks if data is available on the serial port using `Serial.available()`.
* **Read Input:** If data is available, it reads the incoming string until a newline character (`\n`) using `Serial.readStringUntil('\n')` and trims any whitespace.
* **Command Parsing:**
    * It checks if the input string `startsWith()` one of the known command prefixes:
        * `"muxBE12 "`
        * `"muxBE34 "`
        * `"ENABLE "`
        * `"muxTE "`
    * If a prefix matches, it extracts the `value` part of the string.
    * It then calls the appropriate parsing function for that group (e.g., `parseMux4Value()` for `muxBE12`).
    * If no known prefix is found but input exists, an error message is printed.

### 3.4. Helper Functions

* **`printGeneralUsage()`**
    * Prints a help message to the Serial Monitor, listing all available commands and their expected formats.

* **`write16BitsToChain(int dataPin, int clockPin, int latchPin, uint16_t data)`**
    * Takes the data, clock, and latch pins for a 16-bit group, and the 16-bit data to send.
    * Splits the 16-bit `data` into a `highByte` and `lowByte`.
    * Sets the `latchPin` LOW.
    * Uses `shiftOut(dataPin, clockPin, MSBFIRST, highByte)` to send the most significant byte first. This byte will end up in the second shift register of the pair (controlling MUXes 3 & 4 or devices 9-16).
    * Uses `shiftOut(dataPin, clockPin, MSBFIRST, lowByte)` to send the least significant byte. This byte will end up in the first shift register (controlling MUXes 1 & 2 or devices 1-8).
    * Sets the `latchPin` HIGH to transfer the shifted data to the output latches of the 74LS595s.

* **`write8BitsToChain(int dataPin, int clockPin, int latchPin, byte data)`**
    * Similar to `write16BitsToChain` but for a single 8-bit shift register (used for MUX_TE).
    * Sends the single `data` byte using `shiftOut()`.

* **`parseMux4Value(String valueInput, int dP, int cP, int lP, const String& groupName)`**
    * Used for `muxBE12` and `muxBE34` commands.
    * Parses `valueInput` which is expected to be a single 16-bit number.
    * Supports decimal (e.g., `65535`), hexadecimal (e.g., `0xFFFF`), or binary (e.g., `0b1111000011110000`) formats.
    * Converts the input string to a `uint16_t muxData`.
    * For display purposes, it extracts the individual 4-bit select values for each of the four MUXes from `muxData`.
    * Calls `write16BitsToChain()` to send `muxData` to the specified group.
    * Prints status and error messages to the Serial Monitor.

* **`parseMux2Value(String valueInput, int dP, int cP, int lP, const String& groupName)`**
    * Used for the `muxTE` command.
    * Similar to `parseMux4Value` but expects and parses an 8-bit number.
    * Extracts two 4-bit select values for display.
    * Calls `write8BitsToChain()` to send the 8-bit `muxData`.

* **`parseEnableValue(String valueInput, int dP, int cP, int lP)`**
    * Used for the `ENABLE` command.
    * Parses `valueInput` as a 16-bit number (decimal, hex, or binary).
    * Calls `write16BitsToChain()` to send the 16-bit `enableData`.

## 4. Serial Command Interface

### 4.1. Connecting
1.  Upload the sketch to your Arduino Mega.
2.  Open the Arduino IDE's Serial Monitor (Tools > Serial Monitor).
3.  Ensure the baud rate in the Serial Monitor is set to **9600 bps**.
4.  Ensure the line ending is set to **Newline** (or "Both NL & CR").

### 4.2. Command Format
All commands consist of a command prefix followed by a space and a `VALUE`.

`COMMAND_PREFIX VALUE`

### 4.3. Available Commands

**1. `muxBE12 VALUE`**
   * **Purpose:** Controls the four 16-channel multiplexers in the MUX_BE12 group.
   * **`VALUE`:** A 16-bit number representing the combined select states for the four MUXes.
        * Format: Decimal (0-65535), Hexadecimal (e.g., `0xABCD`), or Binary (e.g., `0b1100101010100011`).
   * **Bit Mapping for `VALUE` (16-bit):**
        * `[M4_S3 M4_S2 M4_S1 M4_S0  M3_S3 M3_S2 M3_S1 M3_S0  M2_S3 M2_S2 M2_S1 M2_S0  M1_S3 M1_S2 M1_S1 M1_S0]`
        * Bits 0-3:   MUX_BE12_1 select lines (0-15)
        * Bits 4-7:   MUX_BE12_2 select lines (0-15)
        * Bits 8-11:  MUX_BE12_3 select lines (0-15)
        * Bits 12-15: MUX_BE12_4 select lines (0-15)
   * **Example:** `muxBE12 0b0001001000110100`
        * This sets MUX_BE12_1 to channel 4 (`0100`)
        * MUX_BE12_2 to channel 3 (`0011`)
        * MUX_BE12_3 to channel 2 (`0010`)
        * MUX_BE12_4 to channel 1 (`0001`)
   * **Example:** `muxBE12 0x1234` (Same as above)
   * **Example:** `muxBE12 4660` (Same as above)

**2. `muxBE34 VALUE`**
   * **Purpose:** Controls the four 16-channel multiplexers in the MUX_BE34 group.
   * **`VALUE`:** A 16-bit number, same format and bit mapping as `muxBE12 VALUE`.
   * **Example:** `muxBE34 0xFFFF` (Sets all four MUXes in this group to select channel 15).

**3. `ENABLE VALUE`**
   * **Purpose:** Controls the 16 general-purpose enable/digital output lines.
   * **`VALUE`:** A 16-bit number. Each bit corresponds to one enable line.
        * Bit 0 controls the first enable line, Bit 15 controls the 16th.
   * **Example:** `ENABLE 0b1000000000000001` (Enables the 1st and 16th lines, others off).
   * **Example:** `ENABLE 0xFF00` (Enables the upper 8 lines, lower 8 off).
   * **Example:** `ENABLE 65535` (Enables all 16 lines).

**4. `muxTE VALUE`**
   * **Purpose:** Controls the two 16-channel multiplexers in the MUX_TE group.
   * **`VALUE`:** An 8-bit number representing the combined select states for the two MUXes.
        * Format: Decimal (0-255), Hexadecimal (e.g., `0xAB`), or Binary (e.g., `0b10101011`).
   * **Bit Mapping for `VALUE` (8-bit):**
        * `[M2_S3 M2_S2 M2_S1 M2_S0  M1_S3 M1_S2 M1_S1 M1_S0]`
        * Bits 0-3: MUX_TE1 select lines (0-15)
        * Bits 4-7: MUX_TE2 select lines (0-15)
   * **Example:** `muxTE 0b10100101`
        * This sets MUX_TE1 to channel 5 (`0101`)
        * MUX_TE2 to channel 10 (`1010`)
   * **Example:** `muxTE 0xA5` (Same as above)
   * **Example:** `muxTE 165` (Same as above)

## 5. How to Use
1.  **Hardware Setup:** Wire the Arduino, 74LS595s, and multiplexers according to section 2. Double-check all connections, especially VCC, GND, and control lines.
2.  **Modify Pin Definitions (If Necessary):** Open the Arduino sketch (`arduino_74ls595_mux_extended.ino`) and adjust the `const int` pin definitions at the top if your wiring differs from the examples.
3.  **Upload Sketch:** Connect your Arduino Mega to your computer and upload the sketch using the Arduino IDE.
4.  **Open Serial Monitor:** Tools > Serial Monitor. Set baud rate to 9600 and line ending to "Newline".
5.  **Send Commands:** Type one of the commands described in section 4.3 into the input field of the Serial Monitor and press Enter or click "Send".
6.  **Observe Output:** The Arduino will print the received command, the interpreted values (for MUX commands), the binary/hex data being sent to the shift registers, and a confirmation message. The physical outputs of the shift registers should change accordingly.

## 6. Customization
* **Pin Assignments:** The most common customization will be changing the pin assignments at the top of the sketch to match your specific hardware layout.
* **Command Names:** If desired, the command prefix strings (e.g., `"muxBE12 "`) can be changed in the `loop()` function and `printGeneralUsage()`.
* **Adding More Groups:** The structure allows for adding more shift register groups by defining new pins, adding new command handling in `loop()`, and potentially creating new parsing functions if the data format differs.

