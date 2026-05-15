from glk_tinder.constraints import Balanced, AtLeastN, AtMostN, Constraint
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class Person:
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)


def select_num_groups() -> int:
    while True:
        try:
            num_groups = int(input("\nHow many groups do you want to create? ").strip().lower())
            
            if 1 <= num_groups:
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a positive integer.")
    return num_groups


def select_constraints(people: List[Person]) -> List[Constraint]:
    constraints = []
    while True:
        constraint = select_constraint(people)
        constraints.append(constraint)

        print("\nCurrent selections:")
        for i, item in enumerate(constraints):
            print(
                f"{i}: "
                f"{item}"
            )

        again = input("\nAdd another constraint? (y/n): ").strip().lower()

        if again != "y":
            break
        
    print("\nFinal constraints:")
    for i, item in enumerate(constraints):
        print(
            f"{i}: "
            f"{item}"
        )
    return constraints


def select_constraint(people : List[Person]) -> Constraint:
    constraint_types = ['balanced', 'at most n', 'at least n']
    attributes = people[0].attributes.keys()

    # Step 1: Select constraint type
    print("Available constraint types:")
    for i, constraint in enumerate(constraint_types):
        print(f"{i}: {constraint}")

    while True:
        try:
            selection = int(input("Select a constraint type: "))
            if 0 <= selection < len(constraint_types):
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a number. between 0 and {len(constraint_types) - 1}")

    selected_constraint = constraint_types[selection]
    print(f"\nSelected: {selected_constraint}")

    # Step 2: Select Attribute:
    print("\nAvailable attributes:")
    for i, attr in enumerate(attributes):
        print(f"{i}: {attr}")
    while True:
        try:
            attr_selection = int(input("Select an attribute: "))
            if 0 <= attr_selection < len(attributes):
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a number between 0 and {len(attributes) - 1}")
    selected_attribute = attr_selection
    print(f"\nYou selected: ")
    print(f"Constraint Type: {selected_constraint}")
    print(f"Attribute: {selected_attribute}")

    # Step 3: Different state depending on selection
    if selected_constraint == 'balanced':
        return Balanced(selected_attribute)
    


    # Select a value
    uniqe_values = set([p.attributes[selected_attribute] for p in people])
    print("\nAvailable Values:")
    for i, val in enumerate(uniqe_values):
        print(f"{i}: {attr}")
    while True:
        try:
            val_selection = int(input("Select a value: "))
            if 0 <= val_selection < len(uniqe_values):
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a number between 0 and {len(uniqe_values) - 1}")
    selected_value = unique_values[val_selection]
    print(f"\nYou selected:")
    print(f"Constraint Type: {selected_constraint}")
    print(f"Attribute: {selected_attribute}")
    print(f"Value: {selected_value}")

    if selected_constraint == 'at most n':
        while True:
            try:
                n_selection = int(input(f"\n Give an upper bound that this {selected_value} should not exceed: "))
                if 0 <= n_selection:
                    break
                print("Invalid selection.")
            except ValueError:
                print(f"Please enter an integer larger than 0.")
        return AtMostN(selected_attribute, selected_value, n_selection)
    elif selected_constraint == 'at_least_n':
        while True:
            try:
                n_selection = int(input(f"\n Give an upper bound that this {selected_value} should not exceed: "))
                if 0 <= n_selection:
                    break
                print("Invalid selection.")
            except ValueError:
                print(f"Please enter an integer larger than 0.")

        return AtLeastN(selected_attribute, selected_value, n_selection)
