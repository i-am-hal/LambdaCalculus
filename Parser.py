"""
This is a simple (hopefully) lambda calculus interpreter
in python! It will have an interact repl- which will allow the
user to load in programs and the like! IT will also support
assignments so you don't have to type out functions over
and over again!

Author: Alastar Slater
Date: 12/02/18
"""

#Constants / types
DOT       = "DOT" #Period seperating head and body
DEFINE    = "DEFINE" #Start of a function definition
LPAREN    = "LPAREN" #Open parenthesis
RPAREN    = "RPAREN" #Closed parenthesis
NAME      = "NAME" #type of some function name / argument
LET       = "LET" #Start of an assignment statement
ASSIGN    = "ASSIGN" #Some sort of assignment
SEMI      = "SEMI" #Stops an assignment
NONE      = '\00NONE\00' #Character used for none
EOF       = "EOF" #End of file (input)

#Valid characters for variable names
valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
valid_chars += "+-_/*|&0123456789!?"


##############
#   TOKENS   #
##############

class Token(object): #Class for tokens
    def __init__(self, type, value, line=0, column=0):
        self.type = type #Type of this token
        self.value = value #Value of this token
        self.line = line #Line number this token appeared on
        self.column = column #Column number this token appeared on

    def __repr__(self): #Gives 'literal' representation of a token
        if self.line == self.column == 0: #Give just type, value
            return "Token({}, {})".format(self.type, repr(self.value))
        #Otherwise if we have more information
        return "Token({}, {}, Line:{}, Column:{})".format(self.type, repr(self.value), self.line, self.column)

    #Gives string representaion of this value
    def __str__(self):
        out = "Token(" + str(self.type) + ',' + repr(self.value) + ',' + str(self.line) + ',' + str(self.column) + ')'
        return out #Return output


#################
#     LEXER     #
#################

#Takes the program and returns a stream of tokens
class Lexer(object):
    def __init__(self, program):
        self.text = program #The text we are tokenizing
        self.pos = 0 # character position in the string
        #The first character in the text
        self.current_char = program[0] if program != "" else None
        self.line = 1 #Line position in this program
        self.column = 1 #Column number in this program

    #Raises an error because that character was not recognized
    def UnrecognizedChar(self, char):
        print("Unrecognized Char '{}'".format(char))
        print("Refer to LINE: {}, COLUMN: {}".format(self.line, self.column))
        raise SystemExit #Quit program

    def advance(self): #Moves forward by one character
        self.pos += 1 #Move forward by one character
        if self.pos < len(self.text): #Character in this position, update current_char
            self.current_char = self.text[self.pos]
            self.column += 1 #Move by 1 column

            if self.current_char == '\n': #New line, update line number & reset column
                self.column = 1 #Reset column position on new line
                self.line += 1 #Increase line number

        else: #No new character, set current_char to 'NONE'
            self.current_char = '\00NONE\00'

    def peek(self, ahead=1): #Returns next character
        pos = self.pos + ahead #Gets poition to look at

        if pos < len(self.text): #IF there is a character there, return it
            return self.text[pos]

        else: #Otherwise, return the None character
            return NONE

    def skip_line_comment(self): #Skips rest of line
        #Keep skipping until we reach a new line
        while self.current_char != '\n':
            self.advance()
        self.advance() #Skip new line character

    def skip_whitespace(self): #Skips over whitespace
        #Keep advancing while we are over whitespace characters
        while self.current_char != NONE and self.current_char.isspace():
            self.advance() #Move onto the next character

    def get_name(self): #Gets some name to be used in this program
        #all the valid characters a variable name can have

        name = "" #The name of this item
        while self.current_char in valid_chars:
            name += self.current_char #Add on the character
            self.advance() #Move onto the next character

        return name #Return the string itself

    def get_next_token(self): #Returns the next token from input program
        #Keep tokenizing while there are characters left
        while self.current_char != '\00NONE\00':
            if self.current_char.isspace(): #If any whitespace, skip it
                self.skip_whitespace()
                continue #Try again

            elif self.current_char == '#': #Single line comment
                self.skip_line_comment()
                continue #Try getting a token


            elif self.current_char == '(' and self.peek() == '\\': #IF this is an LPAREN, return LPAREN token
                line, column = self.line, self.column #Save line and column numbers
                self.advance()
                self.advance() #Skip both characters
                return Token(DEFINE, DEFINE, line, column)

            elif self.current_char == '(': #If this is an open parenthesis
                #Gets the line and column of this character
                line, column = self.line, self.column
                self.advance()
                return Token(LPAREN, LPAREN, line, column)

            elif self.current_char == ')': #If this is a RPAREN, return the RPAREN token
                line, column = self.line, self.column #Save line and column numbers
                self.advance()
                return Token(RPAREN, RPAREN, line, column)

            elif self.current_char == ';': #End of an assignment
                line, column = self.line, self.column #Save line and column numbers
                self.advance()
                return Token(SEMI, SEMI, line, column)

            #If this is the let keywird for defining a value
            elif self.current_char + self.peek() + self.peek(2) == 'let':
                line, column = self.line, self.column #Save line and column number
                for _ in range(3): self.advance() #Skip the three characters
                return Token(LET, LET, line, column)

            elif self.current_char == '.': #Id this is a dot, return the token
                line, column = self.line, self.column #Save line and column
                self.advance()
                return Token(DOT, DOT, line, column)

            elif self.current_char == '=': #If this is some sort of assignment
                line, column = self.line, self.column #Save line and column
                self.advance()
                return Token(ASSIGN, ASSIGN, line, column)

            elif self.current_char in valid_chars: #A character we can use for a name, get name token
                line, column = self.line, self.column #Save line and column
                return Token(NAME, self.get_name(), line, column)

            else: #Otherwise, raise an error
                self.UnrecognizedChar(self.current_char) #Raise an error

        return Token(EOF, EOF) #Return EOF token

    def get_tokens(self): #Get all tokens
        tokens = []

        while self.current_char != NONE:
            tok = self.get_next_token() #Get the next token
            tokens.append(tok) #Append the token

        tokens.append(Token(EOF, EOF)) #Add on an EOF token

        return tokens #Return the list of tokens


##################
#     PARSER     #
##################

class AST(object): #Does actually nothing
    pass

class NoOp(AST): #Does nothing
    pass

#An entire program structure
class Program(AST):
    def __init__(self):
        self.children = [] #All the statements

class Function(AST): #Has a set of arguments, and a body
    def __init__(self, token, args, code):
        self.token = token #Save the token
        self.args = args #The arguments to do
        self.code = code #Code to do
        self.line = token.line #Line this occured on
        self.column = token.column #Column this came on

    def count(self, val_type): #Count occurances of this type in this function's code
        total = self.code.count(self.code) #get occurances of this type in the code
        return total #Return the total number of occurances

    def __len__(self): #Return how many values are in the body
        return len(self.code)

    def __repr__(self):
        return "(\\" + ' '.join(repr(x) for x in self.args) + '. ' + repr(self.code) + ')'

    def __str__(self):
        args = "[" + ','.join(str(x) for x in self.args) + ']' #THe arguments to this function
        out = "Function(" + str(self.token) + "," + args + "," + str(self.code) + ")"
        return out #Return the string representation

    def __eq__(self, other):
        #This is all of the possible information about how this function is layed out
        info = (len(self.args), self.count("Function"), self.count("Application"), self.count("Name"))

        if info == other: #Compare information to other function
            return True 

        return False #Otherwise return false

    def __req__(self):
        #This is all of the possible information about how this function is layed out
        info = (len(self.args), self.count("Function"), self.count("Application"), self.count("Name"))
        return info #Return the information

class Application(AST):
    def __init__(self, funcs):
        self.funcs = funcs #The list of functions being applied

    def count(self, val_type):
        total = 0 #Sum total of all the times we see that type

        for func in self.funcs: #Count up all of this type
            if type(func).__name__ == val_type: #If they match, add 1
                total += 1

            if type(func).__name__ == "Function": #Go through all of it's code
                total += func.count(val_type) #Add up occurances of this type in this function

            elif type(func).__name__ == "Application": #Go through all it's functions
                total += func.count(val_type) #Add all of the occurances in these functions

        return total

    #Return how many functions are in this function application
    def __len__(self): return len(self.funcs)

    def __repr__(self):
        return  " ".join(repr(func) for func in self.funcs)

    def __str__(self):
        out = "Application([" + ",".join(str(func) for func in self.funcs) + "])"
        return out #Return the output

class Name(AST): #The name of some variable / value
    def __init__(self, token):
        #Get the line and column numbers
        self.line, column = token.line, token.column
        self.token = token #Save a copy of the token
        self.name = token.value #Name of this 'variable'

    def count(self, val_type): #If type == Name, return 1
        #Return 1 if the type was Name, otherwise, returns 0
        return (1 if val_type == "Name"
                else 0)

    #Return 1 for the length of the name
    def __len__(self): return 1

    def __repr__(self): return self.name

    def __str__(self):
        return "Name(" + str(self.token) + ')'

    def __eq__(self, other):
        return self.name == other

    def __req__(self):
        return self.name

class Assign(AST): #A assignment of some sort
    def __init__(self, token, name, value):
        self.token = token #Copy of the token
        self.name = name #The name object
        self.value = value #The value this is equal to

    def __repr__(self):
        return str(self.name) + ' = ' + str(self.value)

    def __str__(self): return self.__repr__()


class Parser: #This will parse a program
    def __init__(self, program):
        self.lexer = Lexer(program) #Gets the lexer for this program
        #Gets the first token to use
        self.current_token = self.lexer.get_next_token()
        self.line = self.current_token.line #Line of this token
        self.column = self.current_token.column #Column of this token

    #Raises an error for the user
    def raise_error(self, error_message):
        print("PARSING ERROR:")
        print(error_message) #Print the message, and placement
        print("Refer to Line: {}, Column: {}".format(self.line, self.column))
        raise SystemExit

    #Gets the next token if it matches this type
    def eat(self, token_type, err_msg='default'):
        if token_type == self.current_token.type:
            #Get the next token
            self.current_token = self.lexer.get_next_token()
            self.line = self.current_token.line #Get the new line
            self.column = self.current_token.column #Get the new column number

        else: #Otherwise
            if err_msg == 'default': #Default error message
                self.raise_error("Expected token of type {}!".format(token_type))

            else: #Custom message
                self.raise_error(err_msg)

    def name(self): #Returns Name node
        token = self.current_token #Save the token
        #Removes the name token
        self.eat(NAME, "Expected a variable name!")

        return Name(token) #Returns name Node

    def arg_list(self): #Gets the list of NAMES (arguments to function)
        args = [] #Arguments to this function

        #While there are names (variables / arguments) for this function
        while self.current_token.type == NAME:
            name = self.name() #Gets the next argument
            args.append(name) #Adds the name to the list of arguments

        return args #Return the list of arguments

    #If this is a function declaration
    def function_definition(self):
        token = self.current_token #Save the current token
        self.eat(DEFINE) #Removes the function definition

        args = self.arg_list() #Get the list of arguments

        #Removes the dot seperating the HEAD and BODY of the function
        self.eat(DOT, "Expected '.' to seperate Head and Body of defined function!")

        code = self.function_application() #Gets the applied functions

        #Remove the closing parenthesis
        self.eat(RPAREN, "Expected ')' to end function defintiion!")

        #Returns the defined function
        return Function(token, args, code)

    #A series of functions applied to each other
    def function_application(self):
        #If this is an actual function defintiion
        if self.current_token.type == DEFINE:
            #Get the function from it's definition
            func = self.function_definition()

        #Gets the function if it is some sort of name
        elif self.current_token.type == NAME:
            #Gets the function from the name alone
            func = self.name()

        elif self.current_token.type == LPAREN:
            self.eat(LPAREN) #OPen parenthesis around the expression
            #Get the series of applications
            func = self.function_application()
            #Remove closing parenthesis around expression
            self.eat(RPAREN, "Expecting ')' to end nested expression!")

        else: func = None #Otherwise, no function

        #The list of functions being applied
        applied = [] if func == None else [func]

        #Go through all the functions to be applied
        while self.current_token.type in [NAME, DEFINE, LPAREN]:
            token = self.current_token #Token we're seeing

            if token.type == NAME: #Get name as the new function
                applied.append(self.name()) #Get name

            elif token.type == DEFINE: #Gets function from definition
                applied.append(self.function_definition())

            elif token.type == LPAREN: #Nested expression
                self.eat(LPAREN) #Remove start of the expression
                #Add the result of this sub-expression
                applied.append(self.function_application())
                #Remove end of the sub expression
                self.eat(RPAREN, "Expected ')' to denote end of nested expression!")

        if len(applied) == 0: #Return NoOp if no functions
            return NoOp() #No function

        #Return the first (only) function if there is only one function
        elif len(applied) == 1:
            return applied[0]

        else: #Return aplication node
            return Application(applied)

    def assignment(self): #Makes an assignment node
        #Saves the token
        token = self.current_token
        self.eat(LET) #Remove the let statement
        name = self.name() #Gets the name of this variable

        #Removes the assignment token
        self.eat(ASSIGN, "Expected '=' to denote assignment")

        #Gets all of the statements being applied to each other
        code = self.function_application()

        #Return the node for assigning stuff
        return Assign(token, name, code)

    def statement(self): #Makes 1 of 3 statements, followed by a semicolon
        #If this is an assignment statement
        if self.current_token.type == LET:
            node = self.assignment() #Return assignment node
            #Removes the semicolon at the end of the assignment
            self.eat(SEMI, "Expected ';' to end the assignment!")

            return node #Reutrn the assignment node

        #If this is some sort of expression / function application
        elif self.current_token.type in [DEFINE, NAME, LPAREN]:
            #Gets all of the values being applied to each other
            node = self.function_application()
            #Removes the semicolon at end of the application
            self.eat(SEMI, "Expected ';' to end function application")

            return node #Return the function application

        else: #Otherwise it is a NoOp
            return NoOp()

    def block(self): #Makes a block of code
        statement_list = [self.statement()] #Gets a statement

        #While we have more statements left
        while self.current_token.type != EOF:
            #Adds on a statement to the list of statements
            statement_list.append(self.statement())

        node = Program() #Makes a program node
        node.children = statement_list #Gives it the list of statements

        return node #Return the node

    def parse(self): #Returns AST of program
        return self.block()
