from glk_tinder.constraints import (
    Constraint,
    Balanced,
    AtLeastN,
    AtMostN,
    Constraint,
    GroupSize,
    DEFAULT_PRIORITY,
    VALID_TYPES,
    PRIORITIES_AND_WEIGHTS,
)
from dataclasses import dataclass, field
from typing import Dict, List, Any


from pathlib import Path
import yaml


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


def select_constraints(people: List[Person], num_groups: int) -> List[Constraint]:
    constraints = []
    while True:
        constraint = select_constraint(people, num_groups)
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


# def select_group_size() -> int:
#     while True:
#         try:
#             group_size = int(
#                 input("\nWhat size should the group size be? ").strip().lower()
#             )

#             if 1 <= group_size:
#                 break
#             print("Invalid selection.")
#         except ValueError:
#             print(f"Please enter a positive integer.")
#     return group_size


def select_priority() -> int:
    priorities = list(PRIORITIES_AND_WEIGHTS.keys())

    # Select Priority
    print(f"\nSelect Priority (default=medium)")
    for i, p in enumerate(priorities):
        print(f"{i}: {p} ")
    while True:
        try:
            priority_idx = input("Select the priority (enter for default): ")
            if priority_idx == "":
                priority = DEFAULT_PRIORITY
                break
            elif 0 <= int(priority_idx) < len(PRIORITIES_AND_WEIGHTS):
                priority = priorities[int(priority_idx)]
                break
            print("Invalid selection.")
        except ValueError:
            print(
                f"Please enter a number between 0 and {len(PRIORITIES_AND_WEIGHTS) - 1}"
            )

    print(f"\nSelected priority: {priority}")
    return PRIORITIES_AND_WEIGHTS[priority]


def select_constraint(people: List[Person], num_groups: int) -> Constraint:

    attributes = list(people[0].attributes.keys())

    # Step 1: Select constraint type
    print("Available constraint types:")
    for i, constraint in enumerate(VALID_TYPES):
        print(f"{i}: {constraint}")
    while True:
        try:
            selection = int(input("Select a constraint type: "))
            if 0 <= selection < len(VALID_TYPES):
                break
            print("Invalid selection.")
        except ValueError:
            print(f"Please enter a number. between 0 and {len(VALID_TYPES) - 1}")

    selected_constraint = VALID_TYPES[selection]
    print(f"\nSelected: {selected_constraint}")

    print(f"\nYou selected: ")
    print(f"Constraint Type: {selected_constraint}")

    priority_weight = select_priority()

    # Handle Group Size
    if selected_constraint == "balanced group size":
        group_size = int(len(people) / num_groups)
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
        return AtMostN(
            selected_attribute, n_selection, selected_value, weight=priority_weight
        )
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

        return AtLeastN(
            selected_attribute, n_selection, selected_value, weight=priority_weight
        )


def read_constraints_file(
    filename: str | Path, attributes: List[str], number_of_rows: int
) -> tuple[int, List[Constraint]]:
    with open(filename, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")

    if "num_groups" not in data:
        raise ValueError("Missing required field: num_groups")

    if "constraints" not in data:
        raise ValueError("Missing required field: constraints")

    num_groups = data["num_groups"]
    constraints = data["constraints"]

    if not isinstance(num_groups, int) or num_groups <= 0:
        raise ValueError("num_groups must be a positive integer")

    if not isinstance(constraints, list):
        raise ValueError("constraints must be a list")

    normalized_constraints = []
    for i, constraint in enumerate(constraints):

        if not isinstance(constraint, dict):
            raise ValueError(f"Constraint #{i} must be a mapping")
        constraint_type = constraint.get("type")
        if constraint_type not in VALID_TYPES:
            raise ValueError(f"Constraint #{i}: invalid type '{constraint_type}'")
        priority = constraint.get("priority", DEFAULT_PRIORITY)
        if priority not in PRIORITIES_AND_WEIGHTS:
            raise ValueError(f"Constraint #{i}: invalid priority '{priority}'")

        match constraint_type:
            case "balanced":
                if "attribute" not in constraint:
                    raise ValueError(f"Constraint #{i}: balanced requires 'attribute'")
                attribute = constraint.get("attribute")
                if attribute not in attributes:
                    raise ValueError(
                        f"Constraint #{i}: attribute must match column names in data."
                    )
                normalized = Balanced(
                    attribute, weight=PRIORITIES_AND_WEIGHTS[priority]
                )
            case "balanced group size":
                normalized = GroupSize(
                    int(number_of_rows / num_groups),
                    weight=PRIORITIES_AND_WEIGHTS[priority],
                )

            case "at most n":
                if "attribute" not in constraint:
                    raise ValueError(
                        f"Constraint #{i}: {constraint_type} requires 'attribute'"
                    )
                attribute = constraint.get("attribute")
                if attribute not in attributes:
                    raise ValueError(
                        f"Constraint #{i}: attribute must match column names in data."
                    )

                if "limit" not in constraint:
                    raise ValueError(
                        f"Constraint #{i}: {constraint_type} requires 'limit'"
                    )
                limit = constraint.get("limit")
                if not isinstance(limit, int) or limit < 0:
                    raise ValueError("num_groups must be a non-negative integer")

                value = constraint.get("value", None)

                normalized = AtMostN(
                    attribute,
                    max_count=limit,
                    value=value,
                    weight=PRIORITIES_AND_WEIGHTS[priority],
                )

            case "at least n":
                if "attribute" not in constraint:
                    raise ValueError(
                        f"Constraint #{i}: {constraint_type} requires 'attribute'"
                    )
                attribute = constraint.get("attribute")
                if attribute not in attributes:
                    raise ValueError(
                        f"Constraint #{i}: attribute must match column names in data."
                    )

                if "limit" not in constraint:
                    raise ValueError(
                        f"Constraint #{i}: {constraint_type} requires 'limit'"
                    )
                limit = constraint.get("limit")
                if not isinstance(limit, int) or limit < 0:
                    raise ValueError("num_groups must be a non-negative integer")

                value = constraint.get("value", None)

                normalized = AtLeastN(
                    attribute,
                    min_count=limit,
                    value=value,
                    weight=PRIORITIES_AND_WEIGHTS[priority],
                )

        normalized_constraints.append(normalized)
    return num_groups, normalized_constraints
