import argparse
import csv
import re
from tabulate import tabulate

from dataclasses import dataclass, field
from typing import Dict, List, Any, Iterator


from glk_tinder.solver import solver
from glk_tinder.selection import select_constraints, select_num_groups, Person


def normalize_header(header: str) -> str:
    # Remove BOM
    header = header.replace("\ufeff", "")

    # Trim whitespace
    header = header.strip()

    # Lowercase
    header = header.lower()

    # Replace spaces and hyphens with underscores
    header = re.sub(r"[\s\-]+", "_", header)

    # Remove any remaining non-alphanumeric/underscore chars
    header = re.sub(r"[^a-z0-9_]", "", header)

    return header


def read_people_from_csv(filename: str) -> List[Person]:
    people = []

    with open(filename, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [normalize_header(h) for h in reader.fieldnames]

        for row in reader:
            # Extract required field
            name = row.pop("name")

            # Remaining columns become dynamic attributes
            person = Person(name=name, attributes=row)

            people.append(person)

    return people


def print_head(persons: list[Person], n: int = 5) -> None:
    if not persons:
        print("No data")
        return

    # Collect all attribute names
    columns = ["name"]
    for person in persons:
        for attr in person.attributes:
            if attr not in columns:
                columns.append(attr)

    # Build rows
    rows = []
    for person in persons[:n]:
        row = [person.name]
        row.extend(person.attributes.get(col, "") for col in columns[1:])
        rows.append(row)
    print(f"{n} / {len(persons)} rows and {len(columns)} columns printed")

    print(tabulate(rows, headers=columns, tablefmt="grid"))

def write_people_to_csv(filename: str, people: List[Person]):
    # Define CSV columns
    fieldnames = ["name"] + ["group"]

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for person in sorted(people, key=lambda x: x.attributes["group"]):
            row = {"name": person.name, "group": person.attributes["group"]}
            writer.writerow(row)


def main(input_file, output_file):
    """Main entry point."""
    # Load input file with people and data
    people = read_people_from_csv(input_file)
    print_head(people)
    num_groups = select_num_groups()
    constraints = select_constraints(people)
    people, _x, _cp_solver, _constraints = solver(
        people, num_groups=num_groups, constraints=constraints
    )
    write_people_to_csv(output_file, people)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process input files")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    main(args.input, args.output)
