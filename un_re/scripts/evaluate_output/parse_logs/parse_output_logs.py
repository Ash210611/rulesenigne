class RulesEngineParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.error_dict = self._parse_errors_to_dict()

    def _parse_errors_to_dict(self):
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

    def error_summary(self):
        total_errors = 0
        for file_name, errors in self.error_dict.items():
            print(f"{file_name}: {len(errors)} errors")
            total_errors += len(errors)
        print(f"Total errors: {total_errors}")
        return total_errors
    
file_path = 'example_logs/error_log.txt'
parser = RulesEngineParser(file_path)
total_errors = parser.error_summary() 


# def _parse_errors_to_dict(file_path):
#     error_dict = {}
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
#         for i in range(0, len(lines), 2):
#             file_info = lines[i].strip()
#             file_name = file_info.split(', ')[-1]
#             error_message = lines[i + 1].strip()
#             if file_name not in error_dict:
#                 error_dict[file_name] = []
#             error_dict[file_name].append(error_message)
#     return error_dict
#
# def error_summary(error_dict):
#     total_errors=0
#     for file_name, errors in error_dict.items():
#         print(f"{file_name}: {len(errors)} errors")
#         total_errors+=len(errors)
#     return total_errors

# file_path = 'example_logs/error_log.txt'
# error_dict = _parse_errors_to_dict(file_path)
# print(error_dict)
# total_errors = error_summary(error_dict)
# print(f"Total errors: {total_errors}")