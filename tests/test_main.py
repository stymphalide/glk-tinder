import sys
import subprocess
from pathlib import Path
from unittest.mock import patch

from glk_tinder.main import main


def test_main(tmp_path):
    input_file = Path("tests/data/input_file1.csv")
    output_file = tmp_path / "out.csv"

    # Mock interactive input:
    # 2 groups
    # constraint type = balanced (0)
    # attribute = first attribute (0)
    # do not add another constraint
    with patch(
        "builtins.input",
        side_effect=[
            "6",
            "0",
            "0",
            "n",
        ],
    ):
        main(input_file, output_file)

    actual = output_file.read_text()
    expected = Path("tests/data/expected_file1.csv").read_text()

    assert len(actual) == len(expected)


def test_cli(tmp_path):
    input_file = Path("tests/data/input_file1.csv")
    output_file = tmp_path / "out.csv"

    # Simulate stdin for interactive prompts
    user_input = "\n".join(
        [
            "6",  # number of groups
            "0",  # balanced constraint
            "0",  # first attribute
            "n",  # stop adding constraints
        ]
    ) + "\n"

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