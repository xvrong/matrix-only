import argparse
from sys import stdout
from error import ParseError, SemanticError
from lexer import create_lexer
from parser import create_parser
import ast1


def run():
    # arg_parser = argparse.ArgumentParser()
    # arg_parser.add_argument("source_file", type=str)
    # args = arg_parser.parse_args()

    # with open(args.source_file, 'r', encoding='utf8') as f:

    with open('test/variable', 'r', encoding='utf8') as f:
        code_str = f.read()

    lexer = create_lexer()
    parser = create_parser()
    try:
        ast_root = parser.parse(code_str)
        stdout.write(str(ast_root))
    except ParseError as err:
        error_message = str(err)
        stdout.write(str(error_message))


if __name__ == "__main__":
    run()

