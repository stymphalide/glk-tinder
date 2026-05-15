# test_selection.py

import unittest
from unittest.mock import patch

from glk_tinder.io import (
    Person,
    select_num_groups,
    select_constraint,
    select_constraints,
)

from glk_tinder.constraints import Balanced


class TestSelectionFunctions(unittest.TestCase):

    def setUp(self):
        self.people = [
            Person(
                name="Alice",
                attributes={
                    "gender": "F",
                    "department": "Engineering",
                },
            ),
            Person(
                name="Bob",
                attributes={
                    "gender": "M",
                    "department": "Design",
                },
            ),
        ]

    @patch("builtins.input", side_effect=["3"])
    def test_select_num_groups_valid(self, mock_input):
        result = select_num_groups()
        self.assertEqual(result, 3)

    @patch("builtins.input", side_effect=["abc", "-1", "2"])
    def test_select_num_groups_retries_until_valid(self, mock_input):
        result = select_num_groups()
        self.assertEqual(result, 2)

    @patch(
        "builtins.input",
        side_effect=[
            "0",  # select "balanced"
            "0",  # select first attribute
        ],
    )
    def test_select_constraint_balanced(self, mock_input):
        result = select_constraint(self.people)

        self.assertIsInstance(result, Balanced)

    @patch(
        "builtins.input",
        side_effect=[
            "invalid",  # invalid constraint type
            "0",  # valid constraint type
            "invalid",  # invalid attribute
            "0",  # valid attribute
        ],
    )
    def test_select_constraint_retries_on_invalid_input(self, mock_input):
        result = select_constraint(self.people)

        self.assertIsInstance(result, Balanced)

    @patch(
        "builtins.input",
        side_effect=[
            # First constraint
            "0",  # balanced
            "0",  # attribute
            "y",  # continue
            # Second constraint
            "0",  # balanced
            "1",  # attribute
            "n",  # stop
        ],
    )
    def test_select_constraints_multiple(self, mock_input):
        result = select_constraints(self.people)

        self.assertEqual(len(result), 2)
        self.assertTrue(all(isinstance(c, Balanced) for c in result))


if __name__ == "__main__":
    unittest.main()
