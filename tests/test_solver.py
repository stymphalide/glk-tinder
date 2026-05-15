from glk_tinder.solver import solver, Balanced, AtLeastN, AtMostN
from glk_tinder.main import Person


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
