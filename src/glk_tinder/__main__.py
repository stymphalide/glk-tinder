from glk_tinder.main import main
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process input files")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    parser.add_argument("--constraints", required=False, help="Path to constraints YAML file")
    args = parser.parse_args()
    main(args.input, args.output, args.constraints)
