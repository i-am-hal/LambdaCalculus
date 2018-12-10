What is this?
==============
This is a small interpreter for one of the oldest
programming language ever concieved. That language
being Lambda Calculus. The rules for 'running'
any program in lambda calculus is so simple, you
can evaluate it yourself on paper.

How do I use this interpreter?
===============================
To use this interpreter- simply run the program
'repl.py', either by double-clicking or running it
through the command line. There you will be met
with a prompt looking like:
λ>

Here you can enter in an expression for evaluation.
For more information on syntax, refer to the documentation
below.

Special commands
=================
The following is a listing of information on every
special commands for the interpreter (repl).
The commands supported are as follows:
- #quit / #exit
- #debug on/off
- #load

The commands #quit and #exit simply exit the repl
and returns you back to the command line (if being
ran through the command line).

The command #debug on/off toggles if the interpreter
should show the 'steps' it takes to reduce the given
expression. #debug on  will show these steps, #debug off
will not show these steps. This is useful for.. debugging.

The command #load will run a program stored in a file-
and if any variables are created, it will save those
variables for use in the repl. You can give a filename
in two ways:
- #load <filename>
- #load
In the latter case, it will then prompt the user for
the path (name) of the file that the user wishes to open.

Lambda Calculus (Syntax)
=========================
For informatio non the syntax of the Lambda Calculus, 
please refer to the DOC.txt file in the directory.
There you will find an in-depth explanation of
the syntax and how the lambda calulus operates.
"# LambdaCalculus" 
