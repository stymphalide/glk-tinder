from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Constraint(ABC):
    @abstractmethod
    def apply(self, model, x, people, num_groups):
        pass

    def validate(self, people, num_groups):
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
        return f"CONSTRAINT: Balance {self.attr_name}"

    def validate(self, people, num_groups):
        issues = []

        buckets = {}

        for p in people:
            key = p.attributes.get(self.attr_name)

            if key is None:
                continue

            buckets.setdefault(key, []).append(p)

        for key, persons in buckets.items():

            base = len(persons) // num_groups
            remainder = len(persons) % num_groups

            # Valid counts are either base or base+1
            allowed = {base}

            if remainder > 0:
                allowed.add(base + 1)

            for g in range(num_groups):

                members = [
                    p
                    for p in persons
                    if p.attributes.get("group") == g
                ]

                count = len(members)

                if count not in allowed:
                    issues.append(
                        {
                            "constraint": repr(self),
                            "group": g,
                            "message": (
                                f"{key}: {count} "
                                f"(expected {sorted(allowed)})"
                            ),
                            "people": [p.name for p in members],
                        }
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
        if self.value is not None:
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

    def validate(self, people, num_groups):
        issues = []

        for g in range(num_groups):

            group_people = [
                p for p in people
                if p.attributes.get("group") == g
            ]

            offenders = [
                p for p in group_people
                if p.attributes.get(self.attr_name) == self.value
            ]

            if len(offenders) > self.max_count:
                issues.append({
                    "constraint": repr(self),
                    "group": g,
                    "message": f"{len(offenders)} > {self.max_count}",
                    "people": [p.name for p in offenders],
                })

        return issues

    def __repr__(self):
        if self.value is None:
            return f"CONSTRAINT: {self.attr_name} has at most {self.max_count}"
        return (
            f"CONSTRAINT: {self.attr_name} has at most {self.max_count} of {self.value}"
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

    def validate(self, people, num_groups):
        issues = []

        for g in range(num_groups):

            matching = [
                p
                for p in people
                if p.attributes.get("group") == g
                   and p.attributes.get(self.attr_name) == self.value
            ]

            if len(matching) < self.min_count:
                members = [
                    p
                    for p in people
                    if p.attributes.get("group") == g
                ]

                issues.append(
                    {
                        "constraint": repr(self),
                        "group": g,
                        "message": (
                            f"{len(matching)} < {self.min_count}"
                        ),
                        "people": [p.name for p in members],
                    }
                )

        return issues

    def __repr__(self):
        if self.value is None:
            return f"CONSTRAINT: {self.attr_name} has at least {self.min_count}"
        return f"CONSTRAINT: {self.attr_name} has at least {self.min_count} of {self.value}"


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

    def validate(self, people, num_groups):
        issues = []

        for g in range(num_groups):

            members = [
                p
                for p in people
                if p.attributes.get("group") == g
            ]

            size = len(members)

            if size != self.target_size:
                issues.append(
                    {
                        "constraint": repr(self),
                        "group": g,
                        "message": (
                            f"size={size}, target={self.target_size}"
                        ),
                        "people": [p.name for p in members],
                    }
                )

        return issues

    def __repr__(self):
        return f"CONSTRAINT: Group Size of {self.target_size}"
