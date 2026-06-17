# test_selection.py

import unittest
from unittest.mock import patch

from glk_tinder.selection import (
    Person,
    select_num_groups,
    select_constraint,
    select_constraints,
    select_priority,
)

from glk_tinder.constraints import Balanced, AtMostN, AtLeastN, GroupSize

class TestSelectionFunctions(unittest.TestCase):
    def setUp(self):
        self.people = [
            Person(
                id=0,
                attributes={
                    "name":"Alice",
                    "gender": "F",
                    "department": "Engineering",
                },
            ),
            Person(
                id=1,
                attributes={
                    "name":"Bob",
                    "gender": "M",
                    "department": "Design",
                },
            ),
            Person(
                id=3,
                attributes={
                    "name":"Clara",
                    "gender": "F",
                    "department": "Design",
                },
            ),
            Person(
                id=4,
                attributes={
                    "name":"Daniel",
                    "gender": "M",
                    "department": "Engineering",
                },
            ),
        ]
        self.num_groups = 2

    @patch("builtins.input", side_effect=["3"])
    def test_select_num_groups_valid(self, mock_input):
        result = select_num_groups()
        self.assertEqual(result, 3)

    @patch("builtins.input", side_effect=["invalid", "0"])
    def test_select_priority(self, mock_input):
        result = select_priority()
        self.assertEqual(result, 1)
    @patch("builtins.input", side_effect=[""])
    def test_select_priority_default(self, mock_input):
        result = select_priority()
        self.assertEqual(result, 10)


    @patch("builtins.input", side_effect=["abc", "-1", "2"])
    def test_select_num_groups_retries_until_valid(self, mock_input):
        result = select_num_groups()
        self.assertEqual(result, 2)

    @patch(
        "builtins.input",
        side_effect=[
            "0",  # select "balanced"
            "0",  # valid constraint type
            "0",  # select first attribute
        ],
    )
    def test_select_constraint_balanced(self, mock_input):
        result = select_constraint(self.people,self.num_groups)

        self.assertIsInstance(result, Balanced)

    @patch(
        "builtins.input",
        side_effect=[
            "invalid",  # invalid constraint type
            "0",  # valid constraint type
            "invalid",  # invalid attribute
            "0",  # low
            "0",  # valid attribute
        ],
    )
    def test_select_constraint_retries_on_invalid_input(self, mock_input):
        result = select_constraint(self.people, self.num_groups)

        self.assertIsInstance(result, Balanced)

    @patch(
        "builtins.input",
        side_effect=[
            # First constraint
            "0",  # balanced
            "0",  # low
            "0",  # attribute
            "y",  # continue
            # Second constraint
            "0",  # balanced
            "0",  # low
            "1",  # attribute
            "n",  # stop
        ],
    )
    def test_select_constraints_multiple(self, mock_input):
        result = select_constraints(self.people, self.num_groups)

        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(c, Balanced) for c in result))

    @patch(
        "builtins.input",
        side_effect=[
            "1",  # select "AtMostN"
            "0",  # low
            "0",  # select first attribute
            "0",  # select first value
            "5",  # Select n
        ],
    )
    def test_select_constraint_at_most_n(self, mock_input):
        result = select_constraint(self.people, self.num_groups)

        self.assertIsInstance(result, AtMostN)

    @patch(
        "builtins.input",
        side_effect=[
            "2",  # select "AtLeastN"
            "0",  # low
            "0",  # select first attribute
            "0",  # select ALL
            "1",  # Select n
        ],
    )
    def test_select_constraint_at_least_n(self, mock_input):
        result = select_constraint(self.people, self.num_groups)

        self.assertIsInstance(result, AtLeastN)

    @patch(
        "builtins.input",
        side_effect=[
            "2",  # select "AtLeastN"
            "0",  # low
            "1",  # select gender attribute
            "1",  # select F
            "4",  # Select n
        ],
    )
    def test_select_constraint_at_least_n_with_value(self, mock_input):
        result = select_constraint(self.people, self.num_groups)
        self.assertIsInstance(result, AtLeastN)
        assert result.__repr__().startswith("CONSTRAINT: gender has at least 4 of")

    @patch(
        "builtins.input",
        side_effect=[
            "2",  # select "AtLeastN"
            "0",  # low
            "1",  # select first attribute
            "0",  # select ALL
            "4",  # Select n
        ],
    )
    def test_select_constraint_at_least_n_with_all(self, mock_input):
        result = select_constraint(self.people, self.num_groups)
        self.assertIsInstance(result, AtLeastN)
        self.assertEqual(result.__repr__(), "CONSTRAINT: gender has at least 4 with weight 1")

    @patch(
        "builtins.input",
        side_effect=[
            "3",  # select "GroupSize"
            "0",  # low
            "1",  # select group size 1
        ],
    )
    def test_select_group_size(self, mock_input):
        result = select_constraint(self.people, self.num_groups)

        self.assertIsInstance(result, GroupSize)


if __name__ == "__main__":
    unittest.main()
