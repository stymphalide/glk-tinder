from ortools.sat.python import cp_model
from dataclasses import dataclass, field
from typing import Dict, Any, List
from abc import ABC, abstractmethod


# =========================================================
# DATA MODEL
# =========================================================

@dataclass
class Person:
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)


# =========================================================
# CONSTRAINT SYSTEM
# =========================================================

class Constraint(ABC):
    @abstractmethod
    def apply(self, model, x, people, num_groups):
        pass


# ---------------------------------------------------------
# GENERIC BALANCED CONSTRAINT (replaces A/B version)
# ---------------------------------------------------------

class Balanced(Constraint):
    def __init__(self, attr_name: str):
        self.attr_name = attr_name

    def apply(self, model, x, people, num_groups):

        buckets = {}

        # group indices by attribute value
        for i, p in enumerate(people):
            key = p.attributes.get(self.attr_name)
            if key is None:
                continue
            buckets.setdefault(key, []).append(i)

        # enforce equal distribution per group
        for key, idx in buckets.items():

            assert len(idx) % num_groups == 0, (
                f"Cannot evenly distribute '{key}' across {num_groups} groups"
            )

            per_group = len(idx) // num_groups

            for g in range(num_groups):
                model.Add(sum(x[i, g] for i in idx) == per_group)


# ---------------------------------------------------------
# Example: at least one attribute per group (extensible)
# ---------------------------------------------------------

class AtLeastOne(Constraint):
    def __init__(self, attr_name: str):
        self.attr_name = attr_name

    def apply(self, model, x, people, num_groups):
        for g in range(num_groups):
            model.Add(
                sum(
                    x[i, g]
                    for i, p in enumerate(people)
                    if p.attributes.get(self.attr_name)
                ) >= 1
            )


# =========================================================
# SOLVER ENGINE (GENERIC)
# =========================================================

def solver(
    people: List[Person],
    group_size: int,
    constraints: List[Constraint]
) -> List[Person]:

    model = cp_model.CpModel()

    n = len(people)
    num_groups = n // group_size

    # -----------------------------------------------------
    # Decision variables
    # -----------------------------------------------------
    x = {}
    for i in range(n):
        for g in range(num_groups):
            x[i, g] = model.NewBoolVar(f"p{i}_g{g}")

    # -----------------------------------------------------
    # BASE CONSTRAINTS
    # -----------------------------------------------------

    for i in range(n):
        model.Add(sum(x[i, g] for g in range(num_groups)) == 1)

    for g in range(num_groups):
        model.Add(sum(x[i, g] for i in range(n)) == group_size)

    # -----------------------------------------------------
    # PLUG-IN CONSTRAINTS
    # -----------------------------------------------------
    for c in constraints:
        c.apply(model, x, people, num_groups)

    # -----------------------------------------------------
    # SOLVE
    # -----------------------------------------------------
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise ValueError("No valid grouping found")

    # -----------------------------------------------------
    # WRITE RESULTS BACK
    # -----------------------------------------------------
    for i in range(n):
        for g in range(num_groups):
            if solver.Value(x[i, g]):
                people[i].attributes["group"] = g
                break

    return people


# =========================================================
# EXAMPLE USAGE
# =========================================================

if __name__ == "__main__":

    people = [
        Person("A1", {"GLK_Gruppe": "A"}),
        Person("A2", {"GLK_Gruppe": "A"}),
        Person("A3", {"GLK_Gruppe": "A"}),
        Person("A4", {"GLK_Gruppe": "A"}),

        Person("B1", {"GLK_Gruppe": "B"}),
        Person("B2", {"GLK_Gruppe": "B"}),
        Person("B3", {"GLK_Gruppe": "B"}),
        Person("B4", {"GLK_Gruppe": "B"}),
    ]

    constraints = [
        Balanced("GLK_Gruppe")
        # AtLeastOne("explainer")  # optional
    ]

    result = solver(people, group_size=2, constraints=constraints)

    for p in result:
        print(p.name, p.attributes["group"])