from collections import deque
import copy

class TreeNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

def tree_form(tabbed_strings):
    lines = tabbed_strings.split("\n")
    root = TreeNode("Root") 
    current_level_nodes = {0: root}
    stack = [root]
    for line in lines:
        level = line.count(' ') 
        node_name = line.strip() 
        node = TreeNode(node_name)
        while len(stack) > level + 1:
            stack.pop()
        parent_node = stack[-1]
        parent_node.children.append(node)
        current_level_nodes[level] = node
        stack.append(node)
    return root.children[0] 

def str_form(node):
    def recursive_str(node, depth=0):
        result = "{}{}".format(' ' * depth, node.name) 
        for child in node.children:
            result += "\n" + recursive_str(child, depth + 1) 
        return result
    return recursive_str(node)

def apply_individual_formula_on_given_equation(equation, formula_lhs, formula_rhs, do_only_arithmetic=False):
    variable_list = {}
    def node_type(s):
        if s[:2] == "f_":
            return s
        else:
            return s[:2]

    def does_given_equation_satisfy_forumla_lhs_structure(equation, formula_lhs):
        nonlocal variable_list

        if node_type(formula_lhs.name) in {"u_", "p_"}: 
            if formula_lhs.name in variable_list.keys(): 
                return str_form(variable_list[formula_lhs.name]) == str_form(equation) 
            else: 
                if node_type(formula_lhs.name) == "p_" and "v_" in str_form(equation): 
                    return False
                variable_list[formula_lhs.name] = copy.deepcopy(equation)
                return True
        if equation.name != formula_lhs.name or len(equation.children) != len(formula_lhs.children): 
            return False
        for i in range(len(equation.children)): 
            if does_given_equation_satisfy_forumla_lhs_structure(equation.children[i], formula_lhs.children[i]) is False:
                return False
        return True

    def formula_apply_root(formula):
        nonlocal variable_list
        if formula.name in variable_list.keys():
            return variable_list[formula.name] 
        data_to_return = TreeNode(formula.name, None) 
        for child in formula.children:
            data_to_return.children.append(formula_apply_root(copy.deepcopy(child))) 
        return data_to_return
    count_target_node = 1

    def formula_apply_various_sub_equation(equation, formula_lhs, formula_rhs, do_only_arithmetic):
        nonlocal variable_list
        nonlocal count_target_node
        data_to_return = TreeNode(equation.name, children=[])
        variable_list = {}
        if do_only_arithmetic == False:
            if does_given_equation_satisfy_forumla_lhs_structure(equation, copy.deepcopy(formula_lhs)) is True: 
                count_target_node -= 1
                if count_target_node == 0: 
                    return formula_apply_root(copy.deepcopy(formula_rhs)) 
        else: 
            if len(equation.children) == 2 and all(node_type(item.name) == "d_" for item in equation.children): 
                x = []
                for item in equation.children:
                    x.append(int(item.name[2:])) 
                if equation.name == "f_add":
                    count_target_node -= 1
                    if count_target_node == 0: 
                        return TreeNode("d_" + str(sum(x))) 
                elif equation.name == "f_mul":
                    count_target_node -= 1
                    if count_target_node == 0:
                        p = 1
                        for item in x:
                            p *= item 
                        return TreeNode("d_" + str(p))
                elif equation.name == "f_pow" and x[1]>=2: 
                    count_target_node -= 1
                    if count_target_node == 0:
                        return TreeNode("d_"+str(int(x[0]**x[1])))
        if node_type(equation.name) in {"d_", "v_"}: 
            return equation
        for child in equation.children: 
            data_to_return.children.append(formula_apply_various_sub_equation(copy.deepcopy(child), formula_lhs, formula_rhs, do_only_arithmetic))
        return data_to_return

    cn = 0

    def count_nodes(equation):
        nonlocal cn
        cn += 1
        for child in equation.children:
            count_nodes(child)
    transformed_equation_list = []
    count_nodes(equation)
    for i in range(1, cn + 1): 
        count_target_node = i
        orig_len = len(transformed_equation_list)
        tmp = formula_apply_various_sub_equation(equation, formula_lhs, formula_rhs, do_only_arithmetic)
        if str_form(tmp) != str_form(equation): 
            transformed_equation_list.append(tmp) 
    return transformed_equation_list 

def return_formula_file(file_name):
    content = None
    with open(file_name, 'r') as file:
        content = file.read()
    x = content.split("\n\n")
    input_f = [x[i] for i in range(0, len(x), 2)] 
    output_f = [x[i] for i in range(1, len(x), 2)]
    input_f = [tree_form(item) for item in input_f] 
    output_f = [tree_form(item) for item in output_f]
    return [input_f, output_f] 

def generate_transformation(equation):
    input_f, output_f = return_formula_file("formula_list.txt") 
    transformed_equation_list = []
    transformed_equation_list += apply_individual_formula_on_given_equation(tree_form(equation), None, None, True) 
    for i in range(len(input_f)): 
        transformed_equation_list += apply_individual_formula_on_given_equation(tree_form(equation), copy.deepcopy(input_f[i]), copy.deepcopy(output_f[i]))
    return list(set(transformed_equation_list)) 

def search(equation, depth):
    if depth == 0: 
        return None
    output = generate_transformation(equation) 
    for i in range(len(output)):
        result = search(str_form(output[i]), depth-1) 
        if result is not None:
            output += result 
    return output

def fx_nest(terminal, fx, depth):
    def neighboring_math_equation(curr_tree, depth=depth): 
        def is_terminal(name):
            return not (name in fx.keys()) 
        element = None 
        def append_at_last(curr_node, depth): 
            if (is_terminal(element) and depth == 0) or (not is_terminal(element) and depth == 1): 
                return None
            if not is_terminal(curr_node.name):
                if len(curr_node.children) < fx[curr_node.name]: 
                    curr_node.children.append(TreeNode(element))
                    return curr_node
                for i in range(len(curr_node.children)):
                    output = append_at_last(copy.deepcopy(curr_node.children[i]), depth - 1)
                    if output is not None: 
                        curr_node.children[i] = copy.deepcopy(output)
                        return curr_node
            return None
        new_math_equation_list = []
        for item in terminal + list(fx.keys()): 
            element = item 
            tmp = copy.deepcopy(curr_tree)
            result = append_at_last(tmp, depth)
            if result is not None:
                new_math_equation_list.append(result)
        return new_math_equation_list

    all_possibility = []

    def bfs(start_node):
        nonlocal all_possibility
        queue = deque()
        visited = set()
        queue.append(start_node)
        while queue:
            current_node = queue.popleft()
            if current_node not in visited:
                visited.add(current_node)
                neighbors = neighboring_math_equation(current_node)
                if neighbors == []:
                    all_possibility.append(str_form(current_node))
                    all_possibility = list(set(all_possibility)) 
                for neighbor in neighbors:
                    if neighbor not in visited:
                        queue.append(neighbor)
    for item in fx.keys(): 
        bfs(TreeNode(item))
    return all_possibility 

def break_equation(equation):
    sub_equation_list = [equation]
    equation = tree_form(equation)
    for child in equation.children: 
        sub_equation_list += break_equation(str_form(child)) 
    return sub_equation_list

def spot_invalid_equation(equation):
    equation = tree_form(equation)
    if equation.name == "f_pow": 
        return equation.children[1].name[:2] == "d_" and int(equation.children[1].name[2:]) >= 2
    return True

def print_equation_helper(equation_tree):
    if equation_tree.children == []:
        return equation_tree.name 
    s = "(" 
    sign = {"f_add": "+", "f_mul": "*", "f_pow": "^"} 
    for child in equation_tree.children:
        s+= print_equation_helper(child) + sign[equation_tree.name]
    s = s[:-1] + ")"
    return s

def print_equation(eq):
    eq = eq.replace("v_0", "x")
    eq = eq.replace("v_1", "y")
    eq = eq.replace("v_2", "z")
    eq = eq.replace("d_", "")
    return print_equation_helper(tree_form(eq))

element_list = ["d_" + str(i) for i in range(1, 3)] + ["v_" + str(i) for i in range(0, 1)] 

formed_math = fx_nest(element_list, {"f_add": 2, "f_mul": 2, "f_pow": 2}, 2) 

formed_math = [equation for equation in formed_math if all(spot_invalid_equation(item) for item in break_equation(equation))] + element_list 

equal_category = [[item] for item in formed_math] 

for equation in formed_math:
    output_list = search(equation, 1) 
    for output in output_list: 
        output = str_form(output)
        output_loc = -1
        equation_loc = -1
        for j in range(len(equal_category)):
            if equation in equal_category[j]:
                equation_loc = j
            if output in equal_category[j]:
                output_loc = j
        if equation_loc != -1 and output_loc != -1 and equation_loc != output_loc: 
            equal_category.append(equal_category[output_loc]+equal_category[equation_loc]) 
            equal_category.pop(max(output_loc, equation_loc))
            equal_category.pop(min(output_loc, equation_loc))

for item in equal_category:
    cat = list(set([print_equation(sub_item) for sub_item in item])) 
    for sub_item in cat:
        print(sub_item)
    print("----------")
