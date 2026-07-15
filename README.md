# NTC Thermistor Lookup Table Generator

Generates C header lookup tables (8/10/12-bit ADC → temperature) from an NTC
thermistor resistance-vs-temperature CSV, for use in embedded firmware
(e.g. PIC/AVR/ESP temperature sensing without runtime math).

## What it does

1. Reads `sensorTable.csv` (columns: temperature, resistance).
2. Computes divider voltage and raw ADC counts (8/10/12-bit) for a given
   `VREF` and pull-up resistor value.
3. Saves an expanded CSV (`NewSensorTable.csv`) with the computed columns.
4. Builds full-range lookup tables (one temperature value per possible ADC
   code, via linear interpolation) and writes them to a C header file
   (`tblTemperatureSensor.h`).

## Configuration

Edit the constants at the top of `generate_lookup_table.py` to match your
setup:

```python
DATA_FOLDER = r"D:\path\to\your\data\folder"  # where sensorTable.csv lives
INPUT_FILENAME = "sensorTable.csv"

VREF = 5.0      # ADC reference voltage
PULLUP = 32.4   # Pull-up resistor value in kΩ
```

`DATA_FOLDER` is independent of where the script itself is saved — the
script can live anywhere, and it will read/write files in `DATA_FOLDER`.

## Usage

```bash
pip install -r requirements.txt

# Uses DATA_FOLDER / INPUT_FILENAME from the script, writes outputs
# back into DATA_FOLDER
python generate_lookup_table.py
```

Optional overrides if you need a one-off input/output location without
editing the script:

```bash
python generate_lookup_table.py --input "D:\other\folder\sensorTable.csv" --outdir "D:\other\folder"
```

## Input CSV format

Expected columns (as exported from typical thermistor datasheets):

| T(℃) | Rcent(㏀) |
|-------|-----------|
| -20   | 190.0     |
| -15   | 148.0     |
| ...   | ...       |

## Output

- `NewSensorTable.csv` — original data plus Voltage/ADC8/ADC10/ADC12 columns.
- `tblTemperatureSensor.h` — C header with three `const int8_t` arrays:
  `tblTemperatureSensor8bit`, `tblTemperatureSensor10bit`,
  `tblTemperatureSensor12bit`.

## Note

Lookup values are stored as `int8_t`, so temperatures outside the
-128…127 °C range will overflow. Adjust the type if your sensor range
requires it.
