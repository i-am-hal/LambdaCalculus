"""
This program interprets a given program written in the Lambda
Calculus, and finishes- if an expression no longer can be reduced,
the final result is outputted to the screen.
Author: Alastar Slater
Date: 12/03/18
"""
from functools import reduce #So we can easily reduce values
#from functools import reduce #Use this for ease
from Parser import Parser #Get the Parser so we can work on this program
#Since we may return AST nodes
from Parser import Application, Function, Name, Token
#Import all of the types that we may use in our interpreter
from Parser import  DOT, DEFINE, RPAREN, NAME, LET, ASSIGN, SEMI, NONE, EOF

#Returns the name of a node
def nodeType(node):
    return type(node).__name__

def copyFunction(func): #Copies function
    return eval(str(func)) #Return the copied function

def copyApplication(func): #Copies a function application
    return eval(str(func)) #Return applied functions

def copyName(func): #Copies a name
    return eval(str(func))

#Class will visit the functions to run a given node
class NodeVisitor:
    def visit(self, node): #Visits a node
        #Get the name of the function to call
        visitor = 'visit_' + type(node).__name__
        #Attempt to get this function for visiting this type
        method = getattr(self, visitor, self.generic_visit)

        return method(node) #Visits the node with that method

    def generic_visit(self, node): #Raises an error
        print("No, visit_{} method!".format(type(node).__name__))
        raise SystemExit #Quits program


class Interpreter(NodeVisitor): #Will interpret a program
    def __init__(self, program, debug=False):
        #Gets the list of statements
        self.ast = Parser(program).parse().children
        self.debug = debug #If we are debug mode
        self.globals = {} #Globally defined values

    def isDefinedValue(self, val): #Checks if a variable has this value
        env = {repr(self.globals[k]):k for k in self.globals} #Make a new dictionary that makes values to names
        #print("ENV..: ", env)

        #print(repr(val), "in", list(env), "?:", repr(val) in list(env))
        #If this is one of those values (and there aren't other values with the same type
        if repr(val) in list(env) and len([x for x in (filter(lambda x: x==val, list(env)))]) < 2:
            return True
        return False

    def getDefinedValue(self, val): #get the name of the corresponding value
        env = {repr(self.globals[k]):k for k in self.globals} #Make a new dictionary that makes values to names

        return Name(Token(0, env[repr(val)], 0, 0)) #Return that value

    def read(self, name): #Attempts to read this name from memory
        env = self.globals #Gets the environment variables
        if name in env: #If this variable exists, return result
            val = env[name] #Get the value

            #If this is a function- copy and return the value
            if nodeType(val) == "Function":
                return copyFunction(val)

            #Returns copy of the function application
            elif nodeType(val) == "Application":
                return copyApplication(val)

            #This one I don't think should happen- but just as a fail-safe
            #If somehow it is not a function- or function application, return the value itself
            else:
                return val


        else: #Otherwise, raise an error
            print("Undeclared variable {}".format(name))
            print("Error occured during runtime")
            raise SystemExit

    def write(self, name, value): #Will add a new variable to the globals
        env = self.globals #Gets the environment variables

        #if name in env: #Raise error-- cannot change values of variables
        #    print("Reassignment error!")
        #    print("Cannot change value of {}, it's value was already given.".format(name))
        #    print("Error occured during runtime.")
        #    raise SystemExit

        env[name] = value #Make the variable with this value

    def freezeGlobals(self, diction): #Given a dictionary, turns it into the new globals
        #Makes a series of pairs for each key - value pair
        env = tuple([(name, diction[name]) for name in diction])
        self.globals = frozenset(env) #'Freeze' values so they cannot be directly changed

    def varExists(self, name): #Returns boolean on if this variable exists
        env = dict(self.globals.copy()) #Get global memory
        return name in env #Returns if this varable has been declared

    #Returns True / False if this function is flat (a function is flat
    #if there are no nested function applications or functions)
    def isFlatFunction(self, func):
        #If there is only one value, and it isn't a function, return True
        if len(func) == 1 and nodeType(func.code) != "Function":
            return True

        elif len(func) > 1 and nodeType(func) == "Application": #Is a function applications
            isFlat = True #If this function is flat
            for func in func.code.funcs:
                #If there is a nested function application, not flat
                if nodeType(func) == "Application":
                    return False

                #If there is another function- this isn't a flat function
                elif nodeType(func) == "Function":
                    return False

            #Otherwise if there are no nested functions / applications, it is flat
            return True

        else: #Otherwise, one value, but is a function, NOT a flat function
            return False

    #Returns list of functions where all sub expressions are evaluated
    def checkForSub(self, funcs):
        #Keeps track of the value(s) each sub expression evaluates to
        vals = {k: [] for k in range(len(funcs))}

        i = 0 #Index in the funcs list
        for x in funcs: #Go through each function call
            if nodeType(x) == "Application": #If function application
                #Get the result and save it
                vals[i] = self.visit(funcs[i])

            else: #Just save the value
                vals[i] = x

            i += 1 #Move to the next index

        #Make it so we can easily concatenate all the elements of this list
        vals = [([x] if type(x) != type([]) else x) for x in list(vals.values())]

        #Get the new list of functions / values to use
        return reduce(lambda x,y: x + y, vals)

    #Goes through the body of some function and replaces
    # every variable matching `target` to the new value
    def changeScope(self, code, target, newName):
        if nodeType(code) == "Function": #Make no changes
            return code

        elif nodeType(code) == "Name": #Single name, check value
            if code == target: #Names match, make change
                return newName

            else: #Otherwise, make no change
                return code

        elif nodeType(code) == "Application": #If a series of values
            i = 0 #Iterator into the functions
            for func in code.funcs: #Go through every function
                #If a name matches, make the change
                if nodeType(func) == "Name" and func == target:
                    code.funcs[i] = newName

                i += 1 #Move to the next function

            return code #Return the modified section

    #Goes through the nested functions, if any functions have the same argument
    # name as `name`, we modify that arguemnt's name and all variables in that
    # functions body
    def checkForRepeat(self, code, name, seen=0):
        #If this is a function (directly edit values
        if nodeType(code) == "Function":
            #If any argument's name is the same as this, change it
            if len(code.args) > 0 and reduce(lambda x,y: x or y, map(lambda n: n == name, code.args)) == True:

                exists = False #If there is an argument matching this name
                i = 0 #Iterator variable
                for arg in code.args:
                    #Adds substript to each variable
                    if arg == name:
                        code.args[i].name = arg.name + str(seen)
                        exists = True #There was a matching variable name
                    i += 1 #Go to next value

                newName = copyName(name) #Make a copy
                #Make the new name with the substript to use
                newName.name = newName.name + str(seen)
                #Change any local variables in this function to make this change
                code.code = self.changeScope(code.code, name, newName)

                #Incriment the seen value by 1 (for the subscript)
                if exists == True: seen += 1

                #Make changes to this set of code (if any can be made)
                code.code = self.checkForRepeat(code.code, name, seen)

                return code #Return the modified function

            return code #Otherwise make no changes

        elif nodeType(code) == "Name": #If this is just some name we can check
            return code #Return the name, make no change

        elif nodeType(code) == "Application": #Make changes for all functions
            i = 0 #iterator variable for each function
            for func in code.funcs: #Go through each function
                #Checks for repeats for this single value
                code.funcs[i] = self.checkForRepeat(code.funcs[i], name, seen)
                i += 1 #Moves onto the next value

            return code #Return the modified function application

    #Uses the check for repeat function on all values in the body-
    #but skips over the first names
    def afterFirstAfter(self, code, name):
        if nodeType(code) == "Function": #Just continue into this function
            code.code = self.checkForRepeat(code.code, name)
            return code #Return the modfied function

        elif nodeType(code) == "Application": #Go thropugh each value
            i = 0 #Iterator for each function
            for func in code.funcs:
                #Only re-abel variable names if this is a function, not shared value
                if nodeType(func) == "Function":
                    #Get the result of checking this value, and save result
                    code.funcs[i] = self.checkForRepeat(func, name)

                i += 1 #Move onto the next value

            return code #Return the modfied code

    #Goes through the code of a function, substitutes all matching
    # variable names for the given value (uses recursion..)
    def substitute(self, code, name, value):
        if nodeType(code) == "Function": #Go through body of the function
            #Substitute the body of this function (change the body)
            code.code = self.substitute(code.code, name, value)
            return copyFunction(code)  #Change body of this function

        elif nodeType(code) == "Name": #If this is some varibale
            if code == name: #If this is the target variable, replace it
                return value

            else: #Otherwise, make no change
                return code

        elif nodeType(code) == "Application": #Try substituting each value in the application
            i = 0 #Iterator through applied functions in this Function Application
            for x in code.funcs: #Go through each value
                #Substitutes variable names if they match
                if nodeType(x) == "Name" and x.name == name:
                    code.funcs[i] = value

                #Use recursion to change these values
                elif nodeType(x) ==  "Function":
                    code.funcs[i] = self.substitute(x, name, value)

                #If this is function application
                elif nodeType(x) == "Application":
                    code.funcs[i] = self.substitute(x, name, value)

                i += 1 #Move to the next value

            return copyApplication(code) #Return modified values

    #Will evaluate a function application (and return the result
    def evaluate(self, funcs):
        if self.debug == True: #Show what the expression is
            print("0:", repr(Application(funcs)))

        #Checks for any sub expressions
        funcs = self.checkForSub(funcs)

        finish = False #Stop evaluation
        step = 1 #Number of reduction steps taken

        #While the first value is a function- or a name that has a defined value
        while nodeType(funcs[0]) == "Function" or nodeType(funcs[0]) == "Name" and self.varExists(self.visit(funcs[0])):
            if self.debug == True: #If we are in debugging mode, show the steps
                print("{}:".format(step), repr(Application(funcs))) #For debugging

            if finish == True or nodeType(funcs[0]) == "Name" and len(funcs) == 1: #If prematurely done
                break

            if nodeType(funcs[0]) == "Name": #Load in this value of this name
                #Loads in the value only
                funcs[0] = self.read(funcs[0].name)

            elif nodeType(funcs[0]) == "Function": #Evaluate the function
                argc = 0 #Index of the argument we stopped at
                #Go through each function and preform substitution
                for arg in funcs[0].args:
                    #If we run out of function arguments
                    if len(funcs) - 1 == 0:
                        finish = True #State that we are done
                        break

                    #If the function isn't flat (has nested elements), check
                    #For repeated function arguments (this is to save processing time)
                    if self.isFlatFunction(funcs[0]) == False:
                        #Makes sure there aren't any repeated variable names
                        funcs[0].code = self.afterFirstAfter(funcs[0].code, arg)

                    val = funcs.pop(1) #Get value to use

                    #Preforms the substitution
                    funcs[0].code = self.substitute(funcs[0].code, arg, val)

                    argc += 1 #Incriment the number of arguments used

                if finish == True: #Not enough arguments
                    arg_list = funcs[0].args #Get the list of arguments
                    while argc: #Change function to get remaining args
                        arg_list.pop(0) #Remove used argument
                        argc -= 1 #Decrease number of arguments we've gone through
                    new_func = copyFunction(funcs[0]) #Copy the funcstion
                    new_func.args = arg_list #Update arglist
                    funcs[0] = new_func #Give the new function
                    continue #Check again

                else: #Function finished fine, strip off the head
                    funcs[0] = funcs[0].code #Put the code in it's place


                #Throw out body head and add on function body
                if nodeType(funcs[0]) == "Application":
                    #Gets the result from evaluating any sub expressions
                    unpacked_func = self.checkForSub(funcs[0].funcs)
                    #add the results of this functions body to memory set
                    funcs = unpacked_func + funcs[1:]

            #Note what step we are now on
            step += 1

        #if self.debug == True: #Show the final step
        #    print("{}:".format(step), repr(Application(funcs)), "\n")

        #print("DEFINED VAL?: ", self.isDefinedValue(funcs[0]))
        if self.isDefinedValue(funcs[0]) == True: #Value does exist as a name, get the name
            funcs[0] = self.getDefinedValue(funcs[0]) #Get that value

        #If we have a function aplication- return application node
        if len(funcs) > 1:
            #Returns the application node
            ret = Application(funcs)
            return ret #Return this application node

        elif len(funcs) == 1: #Return the last value if done
            return funcs[0]

    def visit_Assign(self, node): #Assigns some variable to a function or application
        name = self.visit(node.name) #Get name of this variable

        #If the value is just a single function
        if nodeType(node.value) == "Function":
            result = node.value #Just use the value

        elif nodeType(node.value) == "Application":
            #Use the functions being used to evaluate the values
            result = self.evaluate(node.value.funcs)

        #If this is a variable- load the value from this variable
        elif nodeType(node.value) == "Name":
            #Loads the value from the local environment
            result = self.read(self.visit(node.value))

        #Saves the value given into the namepsace given
        self.write(name, result)

    def visit_Application(self, node): #Evaluates function application
        #Evaluates the function application and returns result
        return self.evaluate(node.funcs)

    def visit_Name(self, node): #Returns name of this node
        return node.name #Return the name

    def run(self, env={}): #Executes a program
        self.globals = env #Sets up the environment
        results = [] #The list of results
        #Execute each statement
        for statement in self.ast:
            if nodeType(statement) == "Function": #Done evaluate, return the function itself
                results.append(statement) #Just add the function

            else: #Otherwise, evaluate it
                #Add this to the list of results
                results.append(self.visit(statement))

        #Return the list of actual results
        return list(filter(lambda i: i != None, results))
