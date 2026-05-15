from glk_tinder.solver import *
from glk_tinder.main import Person


def test_solver_diagnostics():
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
        AtLeastN("Ampel", "red", 1, weight=8),
        # avoid too many greens in one group
        AtMostN("Ampel", "green", 1, weight=3),
        # keep groups near size 3
        GroupSize(3, weight=10),
    ]

    result, x, cp_solver, constraints = solver(
        people, num_groups=3, constraints=constraints
    )

    issues = explain_solution(result, x, cp_solver, constraints, num_groups=3)

    assert len(issues) == 9


def test_balanced_solver():
    people = [
        Person("A", {"ampel": 0}),
        Person("B", {"ampel": 1}),
        Person("C", {"ampel": 0}),
        Person("D", {"ampel": 1}),
    ]
    constraints = [Balanced("ampel")]
    num_groups = 2
    result, _x, _cp_solver, _constraints = solver(
        people.copy(), num_groups, constraints
    )
    group0 = [p for p in result if p.attributes["group"] == 0]
    group1 = [p for p in result if p.attributes["group"] == 1]
    assert len(group0) == 2
    assert len(group1) == 2


def test_at_most_n_solver():
    people = [
        Person("A", {"ampel": 0}),
        Person("B", {"ampel": 0}),
        Person("C", {"ampel": 0}),
        Person("D", {"ampel": 1}),
        Person("E", {"ampel": 1}),
        Person("F", {"ampel": 0}),
    ]
    constraints = [AtMostN("ampel", 0, 2)]
    num_groups = 2
    result, _x, _cp_solver, _constraints = solver(
        people.copy(), num_groups, constraints
    )
    group0 = [p for p in result if p.attributes["group"] == 0]
    group1 = [p for p in result if p.attributes["group"] == 1]

    assert len([p for p in group0 if p.attributes["ampel"] == 0]) <= 2
    assert len([p for p in group1 if p.attributes["ampel"] == 0]) <= 2


def test_at_least_n_solver():
    people = [
        Person("A", {"ampel": 0}),
        Person("B", {"ampel": 0}),
        Person("C", {"ampel": 0}),
        Person("D", {"ampel": 1}),
        Person("E", {"ampel": 1}),
        Person("F", {"ampel": 0}),
    ]
    constraints = [AtLeastN("ampel", 0, 1)]
    num_groups = 3
    result, _x, _cp_solver, _constraints = solver(
        people.copy(), num_groups, constraints
    )
    group0 = [p for p in result if p.attributes["group"] == 0]
    group1 = [p for p in result if p.attributes["group"] == 1]

    assert len([p for p in group0 if p.attributes["ampel"] == 0]) >= 1
    assert len([p for p in group1 if p.attributes["ampel"] == 0]) >= 1
