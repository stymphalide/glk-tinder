from glk_tinder.constraints import Balanced, AtLeastN, AtMostN, Constraint, GroupSize
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class Person:
    id: int
    attributes: Dict[str, Any] = field(default_factory=dict)


def select_num_groups() -> int:
    while True:
        try:
            num_groups = int(
                input("\nHow many groups do you want to create? ").strip().lower()
            )

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
            print(f"{i}: " f"{item}")

        again = input("\nAdd another constraint? (y/n): ").strip().lower()

        if again != "y":
            break

    print("\nFinal constraints:")
    for i, item in enumerate(constraints):
        print(f"{i}: " f"{item}")
    return constraints


def select_attribute(attributes: List[str]) -> str:
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
    return attributes[attr_selection]


def select_group_size() -> int:
    while True:
        try:
            group_size = int(
                input("\nWhat size should the group size be? ").strip().lower()
            )

            if 1 <= group_size:
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a positive integer.")
    return group_size

def select_priority() -> int:
    priorities_to_weight = {
        "low": 1,
        "medium": 10,
        "high": 100
    }
    priorities = list(priorities_to_weight.keys())

    # Select Priority
    print(f"\nSelect Priority (default=medium)")
    for i,p in enumerate(priorities):
        print(f"{i}: {p} ")
    while True:
        try:
            priority_idx = input("Select the priority (enter for default): ")
            if priority_idx == "":
                priority = "medium"
                break
            elif 0<= int(priority_idx) < len(priorities_to_weight):
                priority = priorities[int(priority_idx)]
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a number between 0 and {len(priorities_to_weight) - 1}")
    
    print(f"\nSelected priority: {priority}")
    return priorities_to_weight[priority]
    

def select_constraint(people: List[Person]) -> Constraint:
    constraint_types = ["balanced", "at most n", "at least n", "group size"]

    attributes = list(people[0].attributes.keys())

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
    

    
    print(f"\nYou selected: ")
    print(f"Constraint Type: {selected_constraint}")

    priority_weight = select_priority()

    # Handle Group Size
    if selected_constraint == "group size":
        group_size = select_group_size()
        return GroupSize(group_size, weight=priority_weight)

    # Attribute selection
    selected_attribute = select_attribute(attributes)
    print(f"Attribute: {selected_attribute}")

    # Step 3: Different state depending on selection
    if selected_constraint == "balanced":
        return Balanced(selected_attribute, weight=priority_weight)

    print(selected_attribute)
    # Select a value
    unique_values = ["ALL"] + list(
        set([p.attributes[selected_attribute] for p in people])
    )
    print("\nAvailable Values:")
    for i, val in enumerate(unique_values):
        print(f"{i}: {val}")
    while True:
        try:
            val_selection = int(input("Select a value: "))
            if 0 <= val_selection < len(unique_values):
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a number between 0 and {len(unique_values) - 1}")

    if val_selection == 0:
        selected_value = None
    else:
        selected_value = unique_values[val_selection]

    print(f"\nYou selected:")
    print(f"Constraint Type: {selected_constraint}")
    print(f"Attribute: {selected_attribute}")
    print(f"Value: {"ALL" if selected_value is None else selected_value}")

    if selected_constraint == "at most n":
        while True:
            try:
                n_selection = int(
                    input(
                        f"\n Give an upper bound that {"ALL" if selected_value is None else selected_value} should not exceed: "
                    )
                )
                if 0 <= n_selection:
                    break
                print("Invalid selection.")
            except ValueError:
                print(f"Please enter an integer larger than 0.")
        return AtMostN(selected_attribute, n_selection, selected_value, weight=priority_weight)
    elif selected_constraint == "at least n":
        while True:
            try:
                n_selection = int(
                    input(
                        f"\n Give a lower bound that {"ALL" if selected_value is None else selected_value} should be under: "
                    )
                )
                if 0 <= n_selection:
                    break
                print("Invalid selection.")
            except ValueError:
                print(f"Please enter an integer larger than 0.")

        return AtLeastN(selected_attribute, n_selection, selected_value, weight=priority_weight)
