import argparse
import logging
import math
import random
import shlex
import string
import sys
import json
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    from termcolor import colored
    from pyfiglet import Figlet
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from enigma.machine import EnigmaMachine
    import nltk
    DEPENDENCIES_INSTALLED = True
except ImportError:
    DEPENDENCIES_INSTALLED = False
    print("Required packages not found. Please install them using: ")
    print("pip install -r requirements.txt")
    sys.exit(1)

class EnigmaticConfig:
    
    ROTORS = ['I', 'II', 'III', 'IV', 'V']
    REFLECTORS = ['B', 'C']
    ENGLISH_FREQ = {'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0}
    MAX_ATTEMPTS = 100000
    TIME_LIMIT = 3600

    def __init__(self):
 
        # 
        # Download required NLTK data if not already available.

        # This data is used for text analysis and frequency calculations.
        # 
        
        try:
            nltk.data.find('corpora/words')
        except LookupError:
            print("Downloading required NLTK data...")
            nltk.download('words', quiet=True)

class EnigmaticLogger:    
    @staticmethod
    def setup(verbose: bool) -> logging.Logger:
        #
        # Configure the logging system to output logs to a file and the console.
        
        # Args:
        #     verbose (bool): If True, set the logging level to DEBUG. Otherwise, set it to INFO.
        
        # Returns:
        #     logging.Logger: The root logger.
        # 

        level = logging.DEBUG if verbose else logging.INFO
        log_filename = f"enigmatic_{datetime.now():%Y%m%d_%H%M%S}.log"
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

class EnigmaticUI:
    
    def __init__(self):
        # 
        # Initialize the UI object.

        # This sets up a Rich console object for styling and rendering text in the terminal.
        # 

        
        self.console = Console()

    def show_banner(self):
        # 
        # Print the Enigmatic banner to the console.

        # This method renders a stylized banner using Rich and prints it to the console.
        # If there is an error rendering the banner, it will be printed to the console.
        # 
        try:
            f = Figlet(font='slant')
            banner = f.renderText('ENIGMATIC')
            
            # Create a fancy panel for the banner
            panel = Panel(
                Text(banner, style="cyan bold"),
                subtitle="v1.1",
                border_style="green",
            )
            
            self.console.print(panel)
            self.console.print("[yellow]🔐 Enigma Machine Tool[/yellow]")
            self.console.print("[blue]⚡ Encryption | Decryption | Text Analysis Tool[/blue]")
            self.console.print("[blue]🚀 Developed by: [yellow]Mostafa Sensei106[/yellow][/blue]")
            self.console.print("[blue]🚀 Follow me on github: [yellow]https://github.com/MostafaSensei106[/yellow][/blue]")
            self.console.print("\n[green]Type 'help' for available commands[/green]")
            
        except Exception as e:
            print("Error rendering banner:", str(e))

    def print_success(self, message: str):
        print(colored(f"\n✓ {message}", 'green'))

    def print_error(self, message: str):
        print(colored(f"\n✗ Error: {message}", 'red'))

    def print_warning(self, message: str):
        
        
        print(colored(f"\n⚠ {message}", 'yellow'))

    def print_goodbye(self):
        print(colored("\nExiting.. Goodbye!..", 'blue'))

class Enigmatic:    
    def __init__(self, verbose: bool = False):
    # 
    # Initialize an Enigmatic instance.

    # Args:
    #     verbose (bool): If True, enables verbose logging for debugging purposes.

    # Attributes:
    #     config (EnigmaticConfig): Configuration settings for the Enigmatic tool.
    #     logger (logging.Logger): Logger instance for logging messages.
    #     ui (EnigmaticUI): User interface instance for displaying messages and banners.
    # 

        self.config = EnigmaticConfig()
        self.logger = EnigmaticLogger.setup(verbose)
        self.ui = EnigmaticUI()
        
    def setup_machine(self, rotors: List[str], reflector: str, 
                     ring_settings: str, plugboard: str = '') -> EnigmaMachine:
        
        # 
        # Sets up an EnigmaMachine instance from the given settings.

        # Args:
        #     rotors (List[str]): List of rotor names in order from left to right.
        #     reflector (str): Reflector name.
        #     ring_settings (str): String of three numbers representing the ring settings for the rotors.
        #     plugboard (str): String of letters representing the plugboard connections.

        # Returns:
        #     EnigmaMachine: The set up EnigmaMachine instance.
        # 

        try:
            return EnigmaMachine.from_key_sheet(
                rotors=' '.join(rotors),
                reflector=reflector,
                ring_settings=ring_settings,
                plugboard_settings=plugboard
            )
        except Exception as e:
            raise ValueError(f"Invalid Enigma settings: {str(e)}")

    def encrypt(self, text: str, key: Optional[Dict] = None) -> Tuple[str, Dict]:
        
        #
        # Encrypts the given text using the given key, or a randomly generated key if none is provided.

        # Args:
        #     text (str): Text to encrypt.
        #     key (Optional[Dict], optional): Key to use for encryption. Defaults to None.

        # Returns:
        #     Tuple[str, Dict]: The encrypted text and the key used.
        #

        if not key:
            self.logger.info("No key provided.. Generating random key...")
        try:
            machine = self.setup_machine(
                key['rotors'],
                key['reflector'],
                key['ring_settings'],
                key.get('plugboard', '')
            )
            
            initial_position = ''.join(random.choices(string.ascii_uppercase, k=3))
            machine.set_display(initial_position)
            key['initial_position'] = initial_position
            encrypted = machine.process_text(text.upper())
            return encrypted
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt(self, text: str, key: Dict) -> str:
        # 
        # Decrypts the given text using the given key.

        # Args:
        #     text (str): Text to decrypt.
        #     key (Dict): Key to use for decryption. Must contain the same information as the key returned by #encrypt.

        # Returns:
        #     str: The decrypted text.
        #
        try:
            machine = self.setup_machine(
                key['rotors'],
                key['reflector'],
                key['ring_settings'],
                key.get('plugboard', '')
            )
            
            machine.set_display(key['initial_position'])
            decrypted = machine.process_text(text.upper())
            decrypted = decrypted.replace('X', ' ')
            return decrypted.title()
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise

    def _generate_random_key(self) -> Dict:
        # 
        # Generates a random Enigma key.

        # Returns:
        #     Dict[str, Any]: A dictionary representing the generated key. Must contain the same information as the key returned by #encrypt.
        # 
        available_letters = list(string.ascii_uppercase)
        plugboard_pairs = []
        
        while len(available_letters) > 1 and len(plugboard_pairs) < 10:
            a, b = random.sample(available_letters, 2)
            plugboard_pairs.append(f"{a}{b}")
            available_letters.remove(a)
            available_letters.remove(b)

        return {
            'rotors': random.sample(self.config.ROTORS, 3),
            'reflector': random.choice(self.config.REFLECTORS),
            'ring_settings': ' '.join(str(random.randint(1, 26)) for _ in range(3)),
            'plugboard': ' '.join(plugboard_pairs)
        }

    def analyze_text(self, text: str) -> Dict:
        # 
        # Analyzes the given text and returns a dictionary containing the following information:

        #     length (int): The length of the text.
        #     unique_chars (int): The number of unique characters in the text.
        #     char_frequency (Dict[str, float]): A dictionary mapping each character to its frequency in the text, as a percentage.
        #     entropy (float): The entropy of the text, in bits per character.
        #     ngrams (Dict[str, float]): A dictionary mapping each ngram to its frequency in the text, as a percentage.

        # Args:
        #     text (str): The text to analyze.

        # Returns:
        #     Dict[str, Any]: The analysis results.
        # 
        return {
            'length': len(text),
            'unique_chars': len(set(text)),
            'char_frequency': self._calculate_frequencies(text),
            'entropy': self._calculate_entropy(text),
            'ngrams': self._analyze_ngrams(text, 3)
        }

    def _calculate_frequencies(self, text: str) -> Dict[str, float]:
        # 
        # Calculates the frequency of each character in the given text, as a percentage.

        # Args:
        #     text (str): The text to calculate frequencies for.

        # Returns:
        #     Dict[str, float]: A dictionary mapping each character to its frequency, as a percentage.
        # 
        freq = Counter(text.upper())
        total = len(text)
        return {char: (count/total)*100 for char, count in freq.items()}

    def _calculate_entropy(self, text: str) -> float:
        # 
        # Calculates the entropy of the given text in bits per character.

        # Args:
        #     text (str): The text to calculate entropy for.

        # Returns:
        #     float: The entropy of the text.
        # 
        freq = Counter(text.upper())
        total = len(text)
        return -sum(count/total * math.log2(count/total) for count in freq.values())

    def _analyze_ngrams(self, text: str, n: int) -> Dict[str, float]:
        # 
        # Analyzes the given text for n-grams of length n and returns their frequencies.

        # Args:
        #     text (str): The text to analyze for n-grams.
        #     n (int): The length of the n-grams to analyze.

        # Returns:
        #     Dict[str, float]: A dictionary mapping the top 10 most common n-grams to their frequency in the text, as a percentage of total n-grams.
        # 

        text = text.upper()
        ngrams = [''.join(text[i:i+n]) for i in range(len(text)-n+1)]
        freq = Counter(ngrams)
        total = sum(freq.values())
        return {ngram: count/total for ngram, count in freq.most_common(10)}

    def run_cli(self):
        # 
        # Runs the Enigmatic CLI.

        # This method runs an infinite loop which prints a prompt, reads a line of input, and executes the corresponding command.
        # The loop exits when the user enters 'exit' or 'q', or when an exception is raised.

        # :return: None
        # 
        self.ui.show_banner()
        
        while True:
            try:
                command = input(colored("\nEnigmatic> ", 'green')).strip()
                
                if not command:
                    continue
                    
                if command.lower() in ['exit', 'q']:
                    self.ui.print_goodbye()
                    break
                    
                if command.lower() == 'help':
                    self._show_help()
                    continue
                
                self._handle_command(shlex.split(command))
                
            except KeyboardInterrupt:
                print("\n")
                continue
            except Exception as e:
                self.ui.print_error(str(e))
                self.logger.error(str(e), exc_info=True)

    def _show_help(self):
        # 
        # Shows the help message for the Enigmatic CLI.

        # This method prints a help message containing the available commands and their options.
        # 
        
        help_text = """
Available commands:
  encrypt <text>     --key   <json file> Encrypt text using key Json file if not provided will be generated.
  decrypt <text>     --key   <json file> Decrypt text using key Json file Required.
  analyze <text>             Analyze text patterns and entropy.
  help                       Show this help message and available commands.
  exit | q                   Exit the program.

Options:
  --file <path>             Read input from file instead of console.
  --output <path>           Write output to file instead of console.
  --save-key <path>         Save encryption key to file instead of console.
"""
        print(help_text)

    def _handle_command(self, args: List[str]):
        # 
        # Handles a single command entered by the user in the CLI.

        # This method takes a list of strings representing the command and its arguments, and dispatches the appropriate
        # method to handle the command.

        # Raises a ValueError if the command is unknown.

        # :param args: The list of strings representing the command and its arguments.
        # :return: None
        # 
        if not args:
            return
            
        command = args[0].lower()
        
        if command == 'encrypt':
            self._handle_encrypt(args[1:])
        elif command == 'decrypt':
            self._handle_decrypt(args[1:])
        elif command == 'analyze':
            self._handle_analyze(args[1:])
        else:
            raise ValueError(f"Unknown command: {command}")

    def _handle_encrypt(self, args: List[str]):
        # 
        # Handles the encrypt command.
        #
        # This method takes a list of strings representing the command and its arguments, and encrypts the given text using the given key.
        # If no key is provided, a random key is generated.
        #
        # The method then prints the encrypted text and the key used to a file if provided, or to the console.
        #
        # :param args: The list of strings representing the command and its arguments.
        # :return: None
        # 
        parser = argparse.ArgumentParser(prog='encrypt')
        parser.add_argument('text', nargs='?', help='Text to encrypt')
        parser.add_argument('--file', help='Input file')
        parser.add_argument('--output', help='Output file')
        parser.add_argument('--save-key', help='Save key to file')
        parser.add_argument('--key', help='Key in JSON format')
        
        args = parser.parse_args(args)
        
        # Get input text
        if args.file:
            with open(args.file, 'r') as f:
                text = f.read().strip()
        elif args.text:
            text = args.text
        else:
            text = input("Enter text to encrypt: ").strip()
        
        # Encrypt
        if args.key:
               with open(args.key, 'r') as f:
                key = json.load(f)
        else:
            key = self._generate_random_key()
        encrypted = self.encrypt(text, key)
        
        # Handle output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(encrypted)
            self.ui.print_success(f"Encrypted text saved to {args.output}")
        else:
            self.ui.print_success("Encryption successful")
            print("\nEncrypted Text:", encrypted)
            
        if args.save_key:
            with open(args.save_key, 'w') as f:
                json.dump(key, f, indent=2)
            self.ui.print_success(f"Key saved to {args.save_key}")
        else:
            print("\nKey:", json.dumps(key, indent=2))

    def _handle_decrypt(self, args: List[str]):
        # 
        # Handles the decrypt command.
        #
        # This method takes a list of strings representing the command and its arguments, and decrypts the given text using the given key.
        # The method then prints the decrypted text to a file if provided, or to the console.
        #
        # :param args: The list of strings representing the command and its arguments.
        # :return: None
        # 
        parser = argparse.ArgumentParser(prog='decrypt')
        parser.add_argument('text', nargs='?', help='Text to decrypt')
        parser.add_argument('--key', required=True, help='Key file')
        parser.add_argument('--file', help='Input file')
        parser.add_argument('--output', help='Output file')
        
        args = parser.parse_args(args)
        
        # Get input text
        if args.file:
            with open(args.file, 'r') as f:
                text = f.read().strip()
        elif args.text:
            text = args.text
        else:
            text = input("Enter text to decrypt: ").strip()
            
        # Load key
        with open(args.key, 'r') as f:
            key = json.load(f)
            
        # Decrypt
        decrypted = self.decrypt(text, key)
        
        # Handle output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(decrypted)
            self.ui.print_success(f"Decrypted text saved to {args.output}")
        else:
            self.ui.print_success("Decryption successful")
            print("\nDecrypted text:", decrypted)

    def _handle_analyze(self, args: List[str]):
        """Handle text analysis command."""
        parser = argparse.ArgumentParser(prog='analyze')
        parser.add_argument('text', nargs='?', help='Text to analyze')
        parser.add_argument('--file', help='Input file')
        
        args = parser.parse_args(args)
        
        # Get input text
        if args.file:
            with open(args.file, 'r') as f:
                text = f.read().strip()
        elif args.text:
            text = args.text
        else:
            text = input("Enter text to analyze: ").strip()
            
        # Analyze
        analysis = self.analyze_text(text)
        
        # Print results
        print("\nText Analysis:")
        print(f"\nLength: {analysis['length']} characters")
        print(f"Unique characters: {analysis['unique_chars']}")
        print(f"Entropy: {analysis['entropy']:.2f} bits per character")
        
        print("\nCharacter Frequencies:")
        for char, freq in sorted(analysis['char_frequency'].items()):
            print(f"  {char}: {freq:.2f}%")
            
        print("\nMost Common Trigrams:")
        for ngram, freq in analysis['ngrams'].items():
            print(f"  {ngram}: {freq:.2f}%")

def main():
    # 
    # Entry point for the Enigmatic tool.

    # This function creates an instance of the Enigmatic class and calls its run_cli method if no command line arguments are provided.
    # If arguments are provided, it calls the _handle_command method with the arguments to handle the command.

    # If an exception is raised during execution, it will be caught and an error message will be printed.
    # If the exception was a KeyboardInterrupt, a message will be printed indicating that the operation was cancelled.
    # If the --debug flag is specified, the exception will be re-raised after printing the error message.
    # 

    try:
        tool = Enigmatic(verbose='--debug' in sys.argv)
        if len(sys.argv) > 1:
            tool._handle_command(sys.argv[1:])
        else:
            tool.run_cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        if '--debug' in sys.argv:
            raise

if __name__ == "__main__":
    main()

