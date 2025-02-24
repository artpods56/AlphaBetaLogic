import os
from typing import List


def load_logical_expressions() -> List[str]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(current_dir, "..", "test_data")
    logical_expressions: List[str] = []
    for file_name in os.listdir(test_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(test_dir, file_name)
            with open(file_path, mode="r", encoding="UTF-8") as file:
                logical_expressions += [line.strip() for line in file.readlines()]
    return logical_expressions

