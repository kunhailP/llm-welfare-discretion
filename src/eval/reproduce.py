"""Run CPU checks and regenerate the paper's analyses from the shipped outputs.

Run from any directory: python /path/to/repo/src/eval/reproduce.py
No model inference, API calls or external data downloads occur here.
"""
import argparse
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="also recompute the slow consequence bootstrap")
    args = parser.parse_args()
    tests = runpy.run_path(str(ROOT / "tests/test_snap_rules.py"))
    checks = [(name, fn) for name, fn in tests.items() if name.startswith("test_") and callable(fn)]
    for name, fn in sorted(checks):
        fn()
    print(f"Rule tests: {len(checks)} passed", flush=True)
    scripts = ["score_common_scale.py", "score_household_sign.py", "score_abawd_hardship.py"]
    if args.full:
        scripts.append("consequence.py")
    scripts += ["make_paper1_tables.py", "make_paper1_appendix.py"]
    for script in scripts:
        print(f"Running {script}", flush=True)
        subprocess.run([sys.executable, str(ROOT / "src/eval" / script)], cwd=ROOT, check=True)
    print("Reproduced analyses and tables. Build the PDF with: make -C paper", flush=True)


if __name__ == "__main__":
    main()
