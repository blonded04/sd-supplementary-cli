# sd-supplementary-cli
![Build Status](https://github.com/blonded04/sd-supplementary-cli/actions/workflows/main.yml/badge.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

Simple command line commands interpreter in Python3.

Supported operations:

1. Basic operations
    * `cat [FILE]` — print the content of the file.
    * `echo` — print the argument (or arguments).
    * `wc [FILE]` — print the number of lines, words and bytes in the file.
    * `pwd` — print the current directory.
    * `exit` — exit the interpreter.
2. Full and weak quoting
    ```
    > echo ’What do you get if you multiply six by nine?\n Six by nine. Forty two.’
    > echo "What do you get if you multiply six by nine?\n Six by nine. Forty two."
    ```
3. Environment and variables
    ```
    > FILE=example.txt
    > cat $FILE
    ```
4. External program execution
    * If an unknown command is entered, the interpreter should attempt to execute it as an external program.
5. Pipelines
    * Support for the `|` operator to pass the output of one command as input to another

## Installation

TODO

## License

This project is licensed under the [MIT license](LICENSE)

## Contributors

* [Panov Andrew](https://www.github.com/sssi111)
* [Afonkin Pavel](https://github.com/Redvin-dt)
* [Neikov Daniil](https://github.com/cowboymalboro1884)
* [Matskevich Valery](https://www.github.com/blonded04)

HSE SPb, 2025
