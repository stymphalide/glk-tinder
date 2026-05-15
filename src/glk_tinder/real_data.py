from pathlib import Path

from glk_tinder.main import read_people_from_csv
from solver import *
from constraints import *

csv_path = (
    Path(__file__).resolve().parent
    / "../../tests/data/input_glk.csv"
).resolve()


people = read_people_from_csv(csv_path)

constraints = [
    Balanced('geschlecht', weight=5),
    AtMostN('ortsgruppe', max_count=1, weight=10),
    GroupSize(6),
]

result, x, cp_solver, constraints = solver(
    people, num_groups=5, constraints=constraints
)
issues = explain_solution(result, x, cp_solver, constraints, num_groups=5)

print("\n--- ISSUES ---")
for i in issues:
        print(i)

print("\n--- GROUPS ---")

groups = {}

for p in result:
    g = p.attributes["group"]
    groups.setdefault(g, []).append(p)

for g, members in groups.items():

    print(f"\nGroup {g}")

    for p in members:
        print(
            f"  {p.name} | "
            f"Ortsgruppe={p.attributes.get('ortsgruppe')} | "
            f"Geschlecht={p.attributes.get('geschlecht')} | "
        )






