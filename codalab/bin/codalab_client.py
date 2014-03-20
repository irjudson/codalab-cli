#!/usr/bin/env python
import sys
import os

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from codalab.config.config_parser import ConfigParser

if __name__ == '__main__':
    config_parser = ConfigParser(sys.argv[1])
    cli = config_parser.cli()
    if '--verbose' in sys.argv[2:]:
        cli.verbose = True
    args = [arg for arg in sys.argv[2:] if arg != '--verbose']
    cli.do_command(args)
