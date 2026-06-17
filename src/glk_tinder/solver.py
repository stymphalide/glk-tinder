from ortools.sat.python import cp_model
from dataclasses import dataclass, field
from typing import Dict, Any, List

from glk_tinder.constraints import GroupSize, Constraint, Balanced, AtMostN, AtLeastN

# =========================================================
# DATA MODEL
# =========================================================


@dataclass
class Person:
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)


# =========================================================
# SOLVER ENGINE (GENERIC)
# =========================================================


def solver(people: List[Person], num_groups: int, constraints: List[Constraint]):

    model = cp_model.CpModel()

    n = len(people)

    objective_terms = []

    x = {}
    for i in range(n):
        for g in range(num_groups):
            x[i, g] = model.NewBoolVar(f"p{i}_g{g}")

    # each person assigned once
    for i in range(n):
        model.Add(sum(x[i, g] for g in range(num_groups)) == 1)

    # constraints
    for c in constraints:
        c.apply(model, x, people, num_groups, objective_terms)

    # objective
    if objective_terms:
        model.Minimize(sum(objective_terms))

    # SOLVE
    cp_solver = cp_model.CpSolver()
    status = cp_solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError("No valid grouping found")

    # write results
    for i in range(n):
        for g in range(num_groups):
            if cp_solver.Value(x[i, g]):
                people[i].attributes["group"] = g
                break

    return people


def validate_solution(people, constraints, num_groups):
    all_issues = []

    for c in constraints:
        all_issues.extend(c.validate(people, num_groups))

    return all_issues


def print_validation(issues: List[Any]):
    print("\n--- VALIDATION: The following constraints are not satisfied ---")

    if not issues:
        print("✓ No constraint violations found")

    for issue in issues:

        print(f"\n{issue['constraint']}")
        print(f"  Group: {issue['group']}")
        print(f"  Problem: {issue['message']}")

        if issue["people"]:
            print(f"  People involved: " f"{', '.join(str(issue['people']))}")


# =========================================================
# EXAMPLE USAGE
# =========================================================

if __name__ == "__main__":

    people = [
        Person(
            "Alice",
            {"Ampel": "red", "Gender": "F", "GLK_Gruppe": "A", "Explainer": True},
        ),
        Person("Bob", {"Ampel": "green", "Gender": "M", "GLK_Gruppe": "A"}),
        Person("Charlie", {"Ampel": "yellow", "Gender": "M", "GLK_Gruppe": "A"}),
        Person("Diana", {"Ampel": "red", "Gender": "F", "GLK_Gruppe": "A"}),
        Person(
            "Eve",
            {"Ampel": "green", "Gender": "F", "GLK_Gruppe": "B", "Explainer": True},
        ),
        Person("Frank", {"Ampel": "green", "Gender": "M", "GLK_Gruppe": "B"}),
        Person("Grace", {"Ampel": "yellow", "Gender": "F", "GLK_Gruppe": "B"}),
        Person("Henry", {"Ampel": "red", "Gender": "M", "GLK_Gruppe": "B"}),
        Person("Ivy", {"Ampel": "green", "Gender": "F", "GLK_Gruppe": "A"}),
        Person("Jack", {"Ampel": "red", "Gender": "M", "GLK_Gruppe": "B"}),
    ]

    constraints = [
        # balance original groups
        Balanced("GLK_Gruppe", weight=10),
        # balance genders
        Balanced("Gender", weight=500),
        # every group should ideally have one red
        AtLeastN("Ampel", 1, "red", weight=8),
        # avoid too many greens in one group
        AtMostN("Ampel", 1, "green", weight=3),
        # keep groups near size 3
        GroupSize(3, weight=10),
    ]

    result = solver(
        people,
        num_groups=3,
        constraints=constraints,
    )

    print("\n--- GROUPS ---")

    groups = {}

    for p in result:
        g = p.attributes["group"]
        groups.setdefault(g, []).append(p)

    for g, members in groups.items():

        print(f"\nGroup {g}")

        for p in members:
            print(
                f"  {p.id} | "
                f"Name={p.attributes.get('name')} | "
                f"Ampel={p.attributes.get('Ampel')} | "
                f"Gender={p.attributes.get('Gender')} | "
                f"GLK={p.attributes.get('GLK_Gruppe')}"
            )
    issues = validate_solution(
        result,
        constraints,
        num_groups=3,
    )
    print_validation(issues)
