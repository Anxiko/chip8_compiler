import sys

from decompiler import decompile


def print_decompiler_usage() -> None:
	print("chip8.py input.chip8 output.code8")
	print_decompiler_usage()


def print_usage() -> None:
	print("CHIP 8 (De)Compiler")


if __name__ == '__main__':
	match sys.argv:
		case [_]:
			print_usage()
		case [_, "decompile", input_file, output_file]:
			decompile(input_file, output_file)
		case [_, "decompile", *_]:
			print("Wrong number of arguments!")
			print_decompiler_usage()
