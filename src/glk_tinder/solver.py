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
# Your original AB balancing constraint (now plugin-based)
# ---------------------------------------------------------

class BalancedABGroups(Constraint):
    def apply(self, model, x, people, num_groups):
        group_a = [
            i for i, p in enumerate(people)
            if p.attributes.get("group_source") == "A"
        ]

        group_b = [
            i for i, p in enumerate(people)
            if p.attributes.get("group_source") == "B"
        ]

        # keep original assumption
        assert len(group_a) == len(group_b) == num_groups, \
            "A and B must match number of groups"

        for g in range(num_groups):
            model.Add(sum(x[i, g] for i in group_a) == 1)
            model.Add(sum(x[i, g] for i in group_b) == 1)


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

def solve_groups(
    people: List[Person],
    group_size: int,
    constraints: List[Constraint]
) -> List[Person]:

    model = cp_model.CpModel()

    n = len(people)
    num_groups = n // group_size

    # -----------------------------------------------------
    # Decision variables
    # x[i, g] = person i assigned to group g
    # -----------------------------------------------------
    x = {}
    for i in range(n):
        for g in range(num_groups):
            x[i, g] = model.NewBoolVar(f"p{i}_g{g}")

    # -----------------------------------------------------
    # BASE CONSTRAINTS (always required)
    # -----------------------------------------------------

    # each person in exactly one group
    for i in range(n):
        model.Add(sum(x[i, g] for g in range(num_groups)) == 1)

    # each group has fixed size
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
        Person("A1", {"group_source": "A"}),
        Person("A2", {"group_source": "A"}),
        Person("A3", {"group_source": "A"}),
        Person("A4", {"group_source": "A"}),

        Person("B1", {"group_source": "B"}),
        Person("B2", {"group_source": "B"}),
        Person("B3", {"group_source": "B"}),
        Person("B4", {"group_source": "B"}),
    ]

    constraints = [
        BalancedABGroups()
        # You can add more here:
        # AtLeastOne("explainer")
    ]

    result = solve_groups(people, group_size=2, constraints=constraints)

    for p in result:
        print(p.name, p.attributes["group"])