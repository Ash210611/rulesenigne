from typing import Dict


class RulesEngineParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.error_dict = self._parse_errors_to_dict()

    def _parse_errors_to_dict(self) -> Dict[str, list]:
        error_dict = {}
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            for i in range(0, len(lines), 2):
                file_info = lines[i].strip()
                file_name = file_info.split(', ')[-1]
                error_message = lines[i + 1].strip()
                if file_name not in error_dict:
                    error_dict[file_name] = []
                error_dict[file_name].append(error_message)
        return error_dict

    def error_summary(self) -> int:
        total_errors = 0
        for file_name, errors in self.error_dict.items():
            print(f"{file_name}: {len(errors)} errors")
            total_errors += len(errors)
        print(f"Total errors: {total_errors}")
        return total_errors
