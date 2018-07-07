import re

# function for parsing BASIC command
def parse_basic(line):
    return re.match("^(\\d+)\\s+(\\S+)\\s*(.*)", line)


#function for loading an existing project
def load(file):
    global program
    global repeat_stack
    global while_stack
    global for_stack
    global for_iterators
    program = {}
    repeat_stack = []
    while_stack = []
    for_stack = []
    for_iterators = {}

    fd = open(file, "r")
    for line in fd:
        res = parse_basic(line)
        program[int(res.group(1))] = (res.group(2), res.group(3))
    fd.close()



def basic_input(args):
    res = re.match("^\s*\"(.+)\"\s*;\s*(\S+)", args)
    if res != None:
        globals()[res.group(2)] = input(res.group(1))
    else:
        res = re.match("^\s*(\S+)", args)
        globals()[res.group(1)] = input()


def basic_print(args):
    global for_iterators
    res = re.match("^\s*(\".+\")\s*;\s*(.+)\s*", args)
    if res != None:
        print(res.group(1) + (lambda x: for_iterators[x] if x in for_iterators.keys() else globals()[x])(res.group(2)))
    else:
        res = re.match("^\s*\"(.+)\"\s*", args)
        if res != None:
            print(res.group(1))
        else:
            res = re.match("^\s*(.+)\s*", args)
            print(vars_to_vals_for(res.group(1)))



def basic_goto(args):
    res = re.match("^\s*(\d+)\s*", args)
    return int(res.group(1))



def basic_let(args):
    res = re.match("^(\S+)\s*=\s*(.+)", args)
    buf = res.group(2)
    buf = vars_to_vals_for(buf)
    buf = vars_to_vals(buf)
    globals()[res.group(1)] = str(eval(buf))



def basic_if(args, line):
    args = vars_to_vals_for(args)

    res = re.match("^\s*(.+)\s+then\s+(.+)\s+else\s+(.+)\s*", args)
    if res != None:
        if eval(vars_to_vals_for(res.group(1))): return execute((res.group(2)[:res.group(2).find(' ')], res.group(2)[res.group(2).find(' ') + 1:]), line)
        else: return execute((res.group(3)[:res.group(3).find(' ')], res.group(3)[res.group(3).find(' ') + 1:]), line)
    else:
        res = re.match("^\s*(.+)\s+then\s+(.+)\s*", args)
        if eval(vars_to_vals_for(res.group(1))):
            return execute((res.group(2)[:res.group(2).find(' ')], res.group(2)[res.group(2).find(' ') + 1:]), line)
        else: return 0



def basic_repeat(line):
    global repeat_stack
    repeat_stack.append(line)


#function for changing variables in expression to corresponding values
def vars_to_vals(args):
    global program
    r = re.search("([^\d\s/+\-*%()=!]+)", args)
    args_copy = ""
    while args_copy != args:
        if r == None: break
        args_copy = args[:]
        if r.group(1) in globals().keys():
            args = re.sub("([^\d\s/+\-*%()=!]+)", globals()[r.group(1)], args, 1)
        r = re.search("([^\d\s/+\-*%()=!]+)", args)
    return args


#function for changing variables in expression to corresponding values from 'for' iterators
def vars_to_vals_for(args):
    global program
    global for_iterators
    r = re.search("([^\d\s/+\-*%()=!]+)", args)
    args_copy = ""
    while args_copy != args:
        if r == None: break
        args_copy = args[:]
        if r.group(1) in for_iterators.keys():
            args = re.sub("([^\d\s/+\-*%()=!]+)", for_iterators[r.group(1)], args, 1)
        r = re.search("([^\d\s/+\-*%()=!]+)", args)
    return vars_to_vals(args)


#function for finding next line with command given in an argument ignoring nested encounters
def find_statement(line, statement, ignore):
    global program
    prog_list = [*program]
    prog_list.sort()
    start_pos = prog_list.index(line)
    nest = 0
    for pos in prog_list[start_pos + 1:]:
        if program[pos][0] == ignore: nest += 1
        elif program[pos][0] == statement:
            if nest == 0:
                return pos
            else: nest -= 1
    return -1



def basic_until(args):
    global repeat_stack
    args = vars_to_vals_for(args)
    if eval(args):
        repeat_stack.pop()
        return 0
    else: return repeat_stack.pop()



def basic_while(args, line):
    global while_stack
    args = vars_to_vals_for(args)
    if eval(args):
        while_stack.append(line)
        return 0
    else:
        while_stack.append(-1)
        return find_statement(line, "wend", "while")



def basic_wend():
    global while_stack
    pos = while_stack.pop()
    return pos if pos != -1 else 0




def basic_for(args, line):
    global for_stack
    global for_iterators
    res = re.match("\s*(\S+)\s*=\s*(.+)\s+to\s+(.+)\s*", args)
    start_val = str(eval(vars_to_vals_for(res.group(2))))
    end_val = str(eval(vars_to_vals_for(res.group(3))))

    if res.group(1) in for_iterators.keys():
        start_val = str(eval(for_iterators[res.group(1)] + " + 1"))

    for_iterators[res.group(1)] = start_val

    if (eval(start_val + " == " + end_val)):
        for_iterators.pop(res.group(1))
        for_stack.append(-1)
        return find_statement(line, "next", "for")
    else:
        for_stack.append(line)
        return 0



def basic_next():
    global for_stack
    jmp = for_stack.pop()
    if jmp == -1:
        return 0
    else:
        return jmp



#function for executing BASIC command
def execute(cmd, line):
    global program
    command, args = cmd

    if (command == ""): return -1
    elif (command == "input"):  basic_input(args);  return 0
    elif (command == "print"):  basic_print(args);  return 0
    elif (command == "goto"):   return basic_goto(str(args))
    elif (command == "end"):   return -1
    elif (command == "let"):    basic_let(args);    return 0
    elif (command == "if"):     return basic_if(args, line)
    elif (command == "repeat"): basic_repeat(line); return 0
    elif (command == "until"):  return basic_until(args)
    elif (command == "while"):  return basic_while(args, line)
    elif (command == "wend"):   return basic_wend()
    elif (command == "for"):    return basic_for(args, line)
    elif (command == "next"):   return basic_next()
    else: print("Unknown command"); return -1



#function for running the program
def run():
    global program
    if 'program' not in globals():
        print("No project found - create a new project or load an existing one")
        return
    prog_list = [*program]
    next = prog_list[0]

    next_copy = execute(program[next], next)
    if next_copy != 0: next = next_copy
    else: next = prog_list[prog_list.index(next) + 1] if prog_list.index(next) + 1 < len(prog_list) else -1

    while(next != -1):
        next_copy = execute(program[next], next)
        if next_copy != 0: next = next_copy
        else: next = prog_list[prog_list.index(next)+1] if prog_list.index(next) + 1 < len(prog_list) else -1



#function for changing the numeration of the program (10, 20...)
def renum():
    global program
    if 'program' not in globals():
        print("No project found - create a new project or load an existing one")
        return
    new_order = {}
    new_prog = {}
    prog_list = [*program]
    prog_list.sort()
    for line, i in zip(prog_list, range(1, len(prog_list)+1)):
        new_order[line] = 10*i

    for line in prog_list:
        cmd, arg = program[line]
        if cmd == "goto":
            arg = new_order[int(program[line][1])]
        res = re.search("goto\s+(\d+)", str(arg))
        if res != None:
            new_line = res.group(1)
            arg = re.sub("goto\s+(\d+)", "goto " + str(new_order[new_line]), arg)

        new_prog[new_order[line]] = (cmd, arg)

    program = new_prog



#function for creating the new project
def new():
    global program
    global repeat_stack
    global while_stack
    global for_stack
    global for_iterators
    repeat_stack = []
    while_stack = []
    for_stack = []
    for_iterators = {}
    program = {}



#function for printing the list of commands currently in the program
def list_prog():
    global program
    if 'program' not in globals():
        print("No project found - create a new project or load an existing one")
        return
    prog_list = [*program]
    prog_list.sort()
    for num in prog_list:
        (cmd, arg) = program[num]
        print(num, cmd, arg)



#function for parsing command that was not from interpreter
def repl_cmd(cmd):
    global program
    if 'program' not in globals():
        print("No project found - create a new project or load an existing one")
        return
    res = parse_basic(cmd)
    if res == None:
        print("Unknown command")
    else:
        program[res.group(1)] = (res.group(2), res.group(3))



#function for saving current project in the file
def save(fileName = "main.bas"):
    global program
    if 'program' not in globals():
        print("No project found - create a new project or load an existing one")
        return
    file = open(fileName, "w")
    prog_list = [*program]
    prog_list.sort()
    for line in prog_list:
        file.write(str(line) + " " + str(program[line][0]) + " " + str(program[line][1]) + "\n")
    file.close()



#main function
def console():
    while(True):
        cmd = input(">> ")
        res = re.match("^(\\S+)\\s*(.*)", cmd)
        {
            "load": lambda x: load(x),
            "run": lambda x: run(),
            "renum": lambda x: renum(),
            "new": lambda x: new(),
            "list": lambda x: list_prog(),
            "stop": lambda x: exit(),
            "save": lambda x: save(x)
        }.get(res.group(1), lambda x: repl_cmd(res.group(1) + " " + x))(res.group(2))


if __name__ == "__main__":
    console()