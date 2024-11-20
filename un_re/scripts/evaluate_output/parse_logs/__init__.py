import argparse

from .parse_output_logs import RulesEngineParser


def parse_rules_engine_logs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", required=True)

    args = parser.parse_args()

    rules_engine = RulesEngineParser(file_path=args.file_path)
    result = rules_engine.error_summary()

    if result != 0:
        exit(1)

    print(f"{result} errors found in SQL files.")

