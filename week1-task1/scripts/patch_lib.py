#!/usr/bin/env python3
import sys
from pathlib import Path

THRESHOLDS = '''  input_threshold_pct_rise : 50.0;\n  input_threshold_pct_fall : 50.0;\n  output_threshold_pct_rise : 50.0;\n  output_threshold_pct_fall : 50.0;\n  slew_lower_threshold_pct_rise : 20.0;\n  slew_upper_threshold_pct_rise : 80.0;\n  slew_lower_threshold_pct_fall : 20.0;\n  slew_upper_threshold_pct_fall : 80.0;\n'''


def main():
    if len(sys.argv) != 2:
        print("Usage: patch_lib.py <AMUX2_3V.lib>")
        raise SystemExit(1)

    path = Path(sys.argv[1])
    text = path.read_text()
    if "input_threshold_pct_rise" in text:
        print("Threshold fields already present; no changes made.")
        return

    needle = '  capacitive_load_unit(1,pf);\n\n'
    if needle not in text:
        print("Could not find expected insertion point.")
        raise SystemExit(2)

    text = text.replace(needle, needle + THRESHOLDS + '\n', 1)
    path.write_text(text)
    print(f"Patched {path}")


if __name__ == "__main__":
    main()
