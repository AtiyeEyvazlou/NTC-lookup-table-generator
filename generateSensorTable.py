"""
NTC Thermistor Lookup Table Generator
--------------------------------------
Reads an NTC thermistor resistance-vs-temperature CSV table and generates:
  1. A CSV with computed voltage and ADC (8/10/12-bit) values.
  2. A C header file (tblTemperatureSensor.h) with lookup tables for firmware use.

Usage:
    python generate_lookup_table.py --input sensorTable.csv --outdir ./output
"""

import argparse
import os

import numpy as np
import pandas as pd

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
# Folder where sensorTable.csv lives, and where the outputs
# (NewSensorTable.csv, tblTemperatureSensor.h) will be written.
# This is independent of where this .py file itself is stored.
DATA_FOLDER = r"...path/to/your/File"
INPUT_FILENAME = "sensorTable.csv"

VREF = 5.0
PULLUP = 32.4          # kΩ

ADC12_MAX = 4095
ADC10_MAX = 1023
ADC8_MAX = 255


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding="utf-8")

    df = df.rename(columns={
        "T(℃) ": "Temp",
        "Rcent(㏀) ": "Resistance",
    })

    return df[["Temp", "Resistance"]]


def compute_adc_columns(df: pd.DataFrame) -> pd.DataFrame:
    df["Voltage"] = VREF * df["Resistance"] / (df["Resistance"] + PULLUP)

    df["ADC12"] = (
        df["Resistance"] * ADC12_MAX / (df["Resistance"] + PULLUP)
    ).round().astype(int)

    df["ADC10"] = (
        df["Resistance"] * ADC10_MAX / (df["Resistance"] + PULLUP)
    ).round().astype(int)

    df["ADC8"] = (
        df["Resistance"] * ADC8_MAX / (df["Resistance"] + PULLUP)
    ).round().astype(int)

    return df


def generate_lookup(dataframe: pd.DataFrame, adc_column: str, adc_max: int) -> np.ndarray:
    table = (
        dataframe.groupby(adc_column, as_index=False)
        .mean(numeric_only=True)
        .sort_values(adc_column)
    )

    adc = table[adc_column].to_numpy()
    temp = table["Temp"].to_numpy()

    lookup = np.interp(np.arange(adc_max + 1), adc, temp)

    return np.round(lookup).astype(np.int8)


def write_header(header_file: str, lookup8, lookup10, lookup12) -> None:
    with open(header_file, "w") as f:
        f.write("#ifndef TBL_TEMPERATURE_SENSOR_H\n")
        f.write("#define TBL_TEMPERATURE_SENSOR_H\n\n")
        f.write("#include <stdint.h>\n\n")

        def write_array(name, table):
            f.write(f"const int8_t {name}[] =\n{{\n")

            for i, value in enumerate(table):
                if i % 16 == 0:
                    f.write("    ")

                f.write(f"{value:4d}")

                if i != len(table) - 1:
                    f.write(",")

                if i % 16 == 15:
                    f.write("\n")

            if len(table) % 16 != 0:
                f.write("\n")

            f.write("};\n\n")

        write_array("tblTemperatureSensor8bit", lookup8)
        write_array("tblTemperatureSensor10bit", lookup10)
        write_array("tblTemperatureSensor12bit", lookup12)

        f.write("#endif\n")


def main():
    default_input = os.path.join(DATA_FOLDER, INPUT_FILENAME)

    parser = argparse.ArgumentParser(description="Generate NTC thermistor lookup tables.")
    parser.add_argument("--input", default=default_input, help="Path to input sensorTable.csv")
    parser.add_argument("--outdir", default=DATA_FOLDER, help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    df = load_data(args.input)
    df = compute_adc_columns(df)

    output_csv = os.path.join(args.outdir, "NewSensorTable.csv")
    df.to_csv(output_csv, index=False)
    print("CSV saved:", output_csv)

    lookup8 = generate_lookup(df, "ADC8", ADC8_MAX)
    lookup10 = generate_lookup(df, "ADC10", ADC10_MAX)
    lookup12 = generate_lookup(df, "ADC12", ADC12_MAX)

    header_file = os.path.join(args.outdir, "tblTemperatureSensor.h")
    write_header(header_file, lookup8, lookup10, lookup12)
    print("Header saved:", header_file)


if __name__ == "__main__":
    main()