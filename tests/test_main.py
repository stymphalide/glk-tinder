import sys

from glk_tinder.main import *

import subprocess
from pathlib import Path


def test_main(tmp_path):
    input_file = Path("tests/data/input_file1.csv")
    output_file = tmp_path / "out.csv"

    main(input_file, output_file)

    actual = output_file.read_text()

    expected = Path("tests/data/expected_file1.csv").read_text()
    assert len(actual) == len(expected)



def test_cli(tmp_path):
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
        ],
        check=True,
    )

    expected = Path("tests/data/expected_file1.csv").read_text()
    actual = output_file.read_text()

    assert len(actual) == len(expected)
