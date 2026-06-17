import sys
import subprocess
from pathlib import Path
from unittest.mock import patch

from glk_tinder.main import main


def test_main_with_input(tmp_path):
    input_file = Path("tests/data/input_file1.csv")
    output_file = tmp_path / "out.csv"

    # Mock interactive input:
    # 2 groups
    # constraint type = balanced (0)
    # priority = medium (1)
    # attribute = first attribute (0)
    # do not add another constraint
    with patch(
        "builtins.input",
        side_effect=[
            "2",
            "0",
            "1",
            "0",
            "n",
        ],
    ):
        main(input_file, output_file)
    actual = output_file.read_text()
    expected = Path("tests/data/expected_file1.csv").read_text()
    assert len(actual) == len(expected)

def test_main_with_constraints(tmp_path):
    input_file = Path("tests/data/input_file1.csv")
    constraints_file = Path("tests/data/constraints1.yaml")
    output_file = tmp_path / "out.csv"

    main(input_file, output_file, constraints_file)

    actual = output_file.read_text()
    expected = Path("tests/data/expected_file1.csv").read_text()
    assert len(actual) == len(expected)

def test_cli(tmp_path):
    input_file = Path("tests/data/input_file1.csv")
    output_file = tmp_path / "out.csv"

    # Simulate stdin for interactive prompts
    user_input = (
        "\n".join(
            [
                "2",  # number of groups
                "0",  # balanced constraint
                "1",  # priority = medium
                "0",  # first attribute
                "n",  # stop adding constraints
            ]
        )
        + "\n"
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "glk_tinder",
            "--input",
            str(input_file),
            "--output",
            str(output_file),
        ],
        input=user_input,
        text=True,
        check=True,
    )

    actual = output_file.read_text()
    expected = Path("tests/data/expected_file1.csv").read_text()

    assert len(actual) == len(expected)

def test_cli_with_constraints(tmp_path):
    constraints_file = Path("tests/data/constraints1.yaml")
    input_file = Path("tests/data/input_file1.csv")
    output_file = tmp_path / "out.csv"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "glk_tinder",
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--constraints",
            str(constraints_file)
        ],
        text=True,
        check=True,
    )

    actual = output_file.read_text()
    expected = Path("tests/data/expected_file1.csv").read_text()

    assert len(actual) == len(expected)