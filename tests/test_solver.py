from glk_tinder.solver import solver, Balanced
from glk_tinder.main import Person


def test_balanced_solver():
    people = [
        Person('A', {'ampel':0}),
        Person('B', {'ampel':1}),
        Person('C', {'ampel':0}),
        Person('D', {'ampel':1})
    ]
    constraints = [Balanced('ampel')]
    n = 2
    out_people = solver(people.copy(),n,constraints)
    group0 = [p for p in out_people if p.attributes['group'] == 0]
    group1 = [p for p in out_people if p.attributes['group'] == 1]
    assert len(group0) == 2
    assert len(group1) == 2

def test_at_most_n_solver():
    people = [
        Person('A', {'ampel':0}),
        Person('B', {'ampel':0}),
        Person('C', {'ampel':0}),
        Person('D', {'ampel':1}),
        Person('E', {'ampel':1}),
        Person('F', {'ampel':0}),
    ]
    constraints = [AtMostN('ampel', 0, 2)]
    n = 2
    out_people = solver(people.copy(),n,constraints)
    group0 = [p for p in out_people if p.attributes['group'] == 0]
    group1 = [p for p in out_people if p.attributes['group'] == 1]
    
    assert len(group0) == 3
    assert len(group1) == 3
    assert len([p for p in group0 if p.attributes['ampel'] == 0]) <= 2
    assert len([p for p in group1 if p.attributes['ampel'] == 0]) <= 2

def test_at_least_n_solver():
    people = [
        Person('A', {'ampel':0}),
        Person('B', {'ampel':0}),
        Person('C', {'ampel':0}),
        Person('D', {'ampel':1}),
        Person('E', {'ampel':1}),
        Person('F', {'ampel':0}),
    ]
    constraints = [AtLeastN('ampel', 0, 1)]
    n = 2
    out_people = solver(people.copy(),n,constraints)
    group0 = [p for p in out_people if p.attributes['group'] == 0]
    group1 = [p for p in out_people if p.attributes['group'] == 1]
    
    assert len([p for p in group0 if p.attributes['ampel'] == 0]) >= 1
    assert len([p for p in group1 if p.attributes['ampel'] == 0]) >= 1
