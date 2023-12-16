import argparse
from arbitrage.arbitrage import ArbitrageBot
import logging 

class Cli:
    def __init__(self):
        self.bot = ArbitrageBot() 

    def init_logger(self, args):
        level = logging.INFO 
        if args.verbose:
            level = logging.VERBOSE 
        if args.debug:
            level = logging.DEBUG

        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=level)

    def exec_command(self, args):
        if "watch" in args.command:
            self.bot.watch(args)

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", help="debug verbose mode")
        parser.add_argument("-v", "--verbose", help="info verbose mode", action="store_true")
        parser.add_argument("-o", "--observers", type=str, help="observers, example: -oLogger,Emailer")
        parser.add_argument(
            "-m", "--markets", type=str, help="markets, example: -m BitstampEUR,KrakenEUR"
        )
        parser.add_argument(
            "command",
            nargs="*",
            default="watch",
            help='verb: "watch|replay-history|get-balance|list-public-markets"',
        )

        args = parser.parse_args()
        self.init_logger(args)
        self.exec_command(args)


    

    

def main():
    cli = Cli()
    cli.run()

if __name__ == "__main__":
    main()
    