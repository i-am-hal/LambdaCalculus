"""
This is the full interpreter for the user's use.
This will request a line of input, and it will
process it and show the result. Later, you will be
able to do more, such as being able to see the reduction
steps, and load Lambda Calculus programs.
The notation for doing these extra things is like this:
    #<command>

Author: Alastar Slater
Date: 12/05/18
"""
from os import system #SO we can communicate with the computer
from Interpreter import Interpreter #So we can interpret programs

#The main REPL itself (Read - Eval - Print - Loop)
def main():
    global_vars = {} #The global variables
    debug_mode = False #What mode we're in

    print("Lambda Calculus Interactive Interpreter")
    print("Enter  #quit  to exit.\n")

    while True: #Continue running forever
        #Attempt to get a line of input
        try:
            line = input(chr(955) + "> ")
        except: #Exit repl
            break
        
        #Get input again if nothing was given
        if line.strip() == "": continue

        #If this is not a 'special process', continue
        if line.strip()[0] == "#":
            line = line[1:].split() #Get the command 

            if len(line) == 0: #List off commands
                print("Special process commands:")
                print("#quit / #exit") #Commands for leaving
                print("#debug on/off") #Command for turning on/off debug mode
                print("#load") #Command for loading programs
                print()

            #Quit interpreter
            elif line[0].lower() in ["quit", "exit"]:
                break #Exit program

            elif line[0].lower() == "debug": #If this is the debug command
                if len(line[1:]) == 0: #Give options
                    print("#DEBUG ON/OFF")
                    print("Shows steps for reducing an expression.\n")

                elif line[1].lower() == "on": #If the user wants it to be on
                    debug_mode = True #Turn on debug mode
                    print("Debug mode is now ON.\n") #Tell user it is on

                elif line[1] == "off": #User wants to turn it off
                    debug_mode = False #Turn off debug mode
                    print("Debug mode is now OFF.\n") #Alert the user


            elif line[0].lower() == "load": #Allow the user to load a program
                if len(line) == 1: #User didn't give a path
                    #Get the path to the program
                    path = input("Enter full path to your program:\n")

                else: #Otherwise, assume they did
                    path = "".join(line[1:])

                try:
                    prog = open(path, 'r').read() #Get contents of program

                #Tell the user we couldn't find the file
                except FileNotFoundError:
                    print("--Couln't find {}--\n".format(path))

                else: #Run program
                    try: #Catch any errors
                        #Creates the interpreter for running the program
                        execu = Interpreter(prog, debug_mode)
                        results = execu.run(global_vars) #Run the program

                    except SystemExit:
                        print() #Adds new line

                    else: #No errors occured
                        global_vars = dict(execu.globals) #Gets the variables

                        if len(results) > 0: #If we have results
                            #Print the result of each expression
                            for val in results:
                                print(repr(val))

            else: #Unrecognized command
                print("Unrecognized command #{}".format(" ".join(line)))
                print("For a list of process commands, enter '#'.\n")


        else: #Otherwise, try to eun the program
            try: #Catch any errors
                #Creates the interpreter for running the program
                execu = Interpreter(line, debug_mode)
                results = execu.run(global_vars) #Run the program

            except SystemExit:
                print() #Add a new line

            else: #If no errors occured
                global_vars = dict(execu.globals) #Gets the variables

                if len(results) > 0: #Print out the results
                    for val in results: #Go through each value
                        print(repr(val)) #Print value

if __name__ == "__main__": #If program is ran and not imported
    main()
