import argparse
import sys


VERSION = "0.0.1"

class CLI:
    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser()
        self._subparser = self._parser.add_subparsers(title="command", required=True, help="Executable command group.")

        self._command_generate = self._subparser.add_parser("generate", aliases=["gen"], help="Generate CVVC or VCV recording list.")
        self._command_from_presamp = self._subparser.add_parser("from_presamp", aliases=["fp"], help="Convert phoneme dictionary from \"presamp.ini\".")
        self._command_to_presamp = self._subparser.add_parser("to_presamp", aliases=["tp"], help="Convert the syllable dictionary to \"presamp. ini\".")
        self._add_args()
    
    def _add_args(self) -> None:
        self._parser.add_argument("-v", "--version", action="version", version=VERSION)

        self._command_generate.add_argument("-i", "--input", required=True, help="Import file path.")
        self._command_generate.add_argument("-o", "--output", help="Output file path.")
        self._command_generate.add_argument("-m", "--mode", choices=["VCV", "CVVC"], help="CVVC, VCV or VCV_WITH_VC mode, default CVVC.")
        self._command_generate.add_argument( "-b", "--bpm",type=int, help="Used to specify the speed unit bpm for recording BGM, default is 120.")
        self._command_generate.add_argument("-l", "--max-length", choices=range(2, 9), type=int, help="The maximum number of syllables per line is 8, \
                                            with a default of 6.")
        self._command_generate.add_argument("-s", "--SSS-first", action="store_true", help="Specify whether to use SSS\
                                             (Three Consecutive Repeat Syllable) pattern arrangement first.")
        self._command_generate.add_argument( "-d", "--iter-depth",type=int, help="Find the maximum iteration depth of the sequential order.")
        self._command_generate.add_argument("-r", "--max-redundancy" ,type=int, help="For the maximum number of extra \
                                            syllables that can be tolerated for fluency, the default is 50.")

        self._command_from_presamp.add_argument("-i", "--input", required=True, help="Import file path.")
        self._command_from_presamp.add_argument("-o", "--output", help="Output file path.")

        self._command_to_presamp.add_argument("-i", "--input", required=True, help="Import file path.")
        self._command_to_presamp.add_argument("-o", "--output", help="Output file path.")

    def get_args(self) -> argparse.Namespace:
        return self._parser.parse_args()
    
class App:
    def __init__(self) -> None:
        if len(sys.argv) == 1:
            print("GUI access is currently not supported. Please use the -- help command to view the CLI manual.")
        else:
            cli = CLI()
            args = cli.get_args()
    
if __name__ == "__main__":
    app = App()