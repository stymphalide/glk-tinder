import argparse
import csv

from dataclasses import dataclass, field
from typing import Dict, List, Any
from glk_tinder.solver import solver, Balanced


@dataclass
class Person:
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)


def read_people_from_csv(filename: str) -> List[Person]:
    people = []

    with open(filename, mode="r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            # Extract required field
            name = row.pop("name")

            # Remaining columns become dynamic attributes
            person = Person(name=name, attributes=row)

            people.append(person)

    return people


def write_people_to_csv(filename: str, people: List[Person]):
    # Define CSV columns
    fieldnames = ["name"] + ["group"]

    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for person in people:
            row = {"name": person.name, "group": person.attributes["group"]}
            writer.writerow(row)


def main(input_file, output_file):
    """Main entry point."""
    print("test")
    # Load input file with people and data
    people = read_people_from_csv(input_file)
    constraints = [
        Balanced("GLK_Gruppe")
    ]
    people = solver(people, group_size=2,constraints=constraints)
    write_people_to_csv(output_file, people)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process input files")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()
    main(args.input, args.output)
