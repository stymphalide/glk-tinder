from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Constraint(ABC):
    @abstractmethod
    def apply(self, model, x, people, num_groups):
        pass

    def explain(self, people, x, solver, num_groups):
        return []

    def __repr__(self) -> str:
        return super().__repr__()


class Balanced(Constraint):
    def __init__(self, attr_name: str, weight: int | None = None):
        self.attr_name = attr_name
        self.weight = weight

    def apply(self, model, x, people, num_groups, objective_terms=None):

        buckets = {}

        for i, p in enumerate(people):
            key = p.attributes.get(self.attr_name)
            if key is None:
                continue
            buckets.setdefault(key, []).append(i)

        for key, idx in buckets.items():

            base = len(idx) // num_groups
            remainder = len(idx) % num_groups

            for g in range(num_groups):
                expr = sum(x[i, g] for i in idx)

                if self.weight is None:
                    # HARD (old behavior)
                    model.Add(expr == base)
                else:
                    # SOFT (allow deviation)
                    dev = model.NewIntVar(0, len(idx), f"dev_{key}_{g}")

                    model.Add(dev >= expr - base)
                    model.Add(dev >= base - expr)

                    objective_terms.append(self.weight * dev)

    def __repr__(self) -> str:
        return f"CONSTRAINT: Balance {self.attr_name} with weight {self.weight}"

    def explain(self, people, x, solver, num_groups):
        issues = []

        buckets = {}

        for i, p in enumerate(people):
            key = p.attributes.get(self.attr_name)
            if key is None:
                continue
            buckets.setdefault(key, []).append(i)

        for key, idx in buckets.items():

            base = len(idx) // num_groups

            for g in range(num_groups):
                count = sum(solver.Value(x[i, g]) for i in idx)

                if abs(count - base) > 0:
                    issues.append(
                        f"[Balanced] {self.attr_name}={key} "
                        f"group {g}: {count} vs {base}"
                    )

        return issues


class AtMostN(Constraint):
    def __init__(
        self,
        attr_name: str,
        max_count: int,
        value: Any = None,
        weight: int | None = None,
    ):
        self.attr_name = attr_name
        self.value = value
        self.max_count = max_count
        self.weight = weight

    def apply(self, model, x, people, num_groups, objective_terms=None):
        print(self.value)
        if self.value is not None:
            print("hello")
            buckets = {
                self.value: [
                    i
                    for i, p in enumerate(people)
                    if p.attributes.get(self.attr_name) == self.value
                ]
            }

        else:
            buckets = {}

            for i, p in enumerate(people):
                key = p.attributes.get(self.attr_name)

                if key is None:
                    continue

                buckets.setdefault(key, []).append(i)

        # -----------------------------------------
        # Apply constraints
        # -----------------------------------------
        for key, idx in buckets.items():

            for g in range(num_groups):

                expr = sum(x[i, g] for i in idx)

                if self.weight is None:
                    model.Add(expr <= self.max_count)

                else:
                    excess = model.NewIntVar(
                        0,
                        len(idx),
                        f"excess_{key}_{g}"
                    )

                    model.Add(excess >= expr - self.max_count)
                    model.Add(excess >= 0)

                    objective_terms.append(self.weight * excess)

    def explain(self, people, x, solver, num_groups):
        issues = []

        idx = [
            i
            for i, p in enumerate(people)
            if p.attributes.get(self.attr_name) == self.value
        ]

        for g in range(num_groups):
            count = sum(solver.Value(x[i, g]) for i in idx)

            if count > self.max_count:
                issues.append(
                    f"[AtMostN] {self.attr_name}={self.value} "
                    f"group {g}: {count} > {self.max_count}"
                )

        return issues

    def __repr__(self):
        if self.value is None:
            return f"CONSTRAINT: {self.attr_name} has at most {self.max_count}"
        return (
            f"CONSTRAINT: {self.attr_name} has at most {self.max_count} of {self.value} with weight {self.weight}"
        )


class AtLeastN(Constraint):
    def __init__(
        self, attr_name: str, min_count: int, value: Any = None, weight: int | None = None
    ):
        self.attr_name = attr_name
        self.value = value
        self.min_count = min_count
        self.weight = weight

    def apply(self, model, x, people, num_groups, objective_terms=None):

        idx = [
            i
            for i, p in enumerate(people)
            if p.attributes.get(self.attr_name) == self.value
        ]

        for g in range(num_groups):
            expr = sum(x[i, g] for i in idx)

            if self.weight is None:
                model.Add(expr >= self.min_count)
            else:
                deficit = model.NewIntVar(0, len(idx), f"def_{self.value}_{g}")

                model.Add(deficit >= self.min_count - expr)
                model.Add(deficit >= 0)

                objective_terms.append(self.weight * deficit)

    def explain(self, people, x, solver, num_groups):
        issues = []

        idx = [
            i
            for i, p in enumerate(people)
            if p.attributes.get(self.attr_name) == self.value
        ]

        for g in range(num_groups):
            count = sum(solver.Value(x[i, g]) for i in idx)

            if count < self.min_count:
                issues.append(
                    f"[AtLeastN] {self.attr_name}={self.value} "
                    f"group {g}: {count} < {self.min_count}"
                )

        return issues

    def __repr__(self):
        if self.value is None:
            return f"CONSTRAINT: {self.attr_name} has at least {self.min_count} with weight {self.weight}"
        return f"CONSTRAINT: {self.attr_name} has at least {self.min_count} of {self.value} with weight {self.weight}"


class GroupSize(Constraint):
    def __init__(self, target_size: int, weight: int = 1):
        self.target_size = target_size
        self.weight = weight

    def apply(self, model, x, people, num_groups, objective_terms):

        n = len(people)

        for g in range(num_groups):
            expr = sum(x[i, g] for i in range(n))

            # deviation variable
            dev = model.NewIntVar(0, n, f"group_size_dev_{g}")

            # dev >= difference in both directions
            model.Add(dev >= expr - self.target_size)
            model.Add(dev >= self.target_size - expr)

            # penalize deviation
            objective_terms.append(self.weight * dev)

    def explain(self, people, x, solver, num_groups):
        issues = []

        for g in range(num_groups):
            size = sum(solver.Value(x[i, g]) for i in range(len(people)))

            if size != self.target_size:
                issues.append(f"Group {g}: size={size}, target={self.target_size}")

        return issues

    def __repr__(self):
        return f"CONSTRAINT: Group Size of {self.target_size} with weight {self.weight}"
