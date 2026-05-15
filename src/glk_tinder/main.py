import argparse
import csv

def main(input_file, output_file):
    """Main entry point."""
    # Load input file with people and data
    with open(input_file, mode='r', newline='') as infile:
        reader = csv.reader(infile)

        with open(output_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)

            for row in reader:
                writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process input files")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    main(args.input, args.output)