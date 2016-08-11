"""
# Copyright Nick Cheng, Brian Harrington, Danny Heap, Ke Deng 2013, 2014, 2015
# Distributed under the terms of the GNU General Public License.
#
# This file is part of Assignment 2, CSCA48, Winter 2015
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.
"""

# Do not change this import statement, or add any of your own!
from regextree import RegexTree, StarTree, DotTree, BarTree, Leaf

# Do not change anything above this comment except for the copyright
# statement

# Student code below this comment.

single_char = "012e"
other_char = "()|.*"


def is_in(string):
    '''(str) -> bool
    checks if the given string contains characters only from valid regexes.
    >>> is_in("wafafaf")
    False
    >>> is_not_in("(100101010g)")
    False
    >>> is_not_in("||||112200)
    True
    '''
    ret = True
    valid = (single_char + other_char)
    for i in string:
        if i not in valid:
            ret = False
    return ret


def is_regex(string):
    '''
    (str) -> bool
    checks if given string is a valid regex string.
    >>> is_regex("12345")
    False
    >>> is_regex("1")
    True
    >>> is_regex("((1*.2)**|(1.e))")
    True
    '''
    # I swear this was easier to write than recursion
    ret = False
    if string == '':
        return False
    if is_in(string):
        # assume it to be true
        ret = True

        if len(string) == 1:
            return True
        # if first char in "012e", only '*' can follow
        if string[0] in single_char:
            for i in range(1, len(string)):
                if string[i] != '*':
                    ret = False

        # else if first character is '(', string length has to be > 5
        elif (string[0] == "(" and len(string) < 5) or string.find(')') < 4:
            return False
        # else if it's a '('
        elif string[0] == "(" and string[1] in "012e(":
            # These two need to be 0, think of them as balances
            separater_count = 0
            brackets = 1
            # needs to be False
            separater_needed = True
            # go through character by character
            for i in range(1, len(string) - 1):
                # '*)|.' can't come after ".|("
                if string[i] in ".|(" and string[i + 1] in '*).|':
                    return False
                # "012e(" cannot follow ')'
                elif string[i] == ')' and string[i + 1] in "012e(":
                    return False
                # '(012e' cannot follow "012e"
                elif string[i] in single_char and string[i + 1] in '(012e':
                    return False
                # only ")*|." can follow '*'
                elif string[i] == '*' and string[i + 1] in "012e(":
                    return False
                # ')' found would decrease brackets by one
                elif string[i] == ')':
                    brackets -= 1
                    separater_count -= 1
                # '(' found would increase brackets by one
                elif string[i] == '(':
                    brackets += 1
                    separater_needed = True

                elif string[i] in "|.":
                    separater_count += 1
                    separater_needed = False
            # check last char in string
            if string[-1] == ")":
                brackets -= 1
                separater_count -= 1
            elif string[-1] != "*":
                return False

            # final check for brackets and separaters
            if brackets == 0 and separater_count == 0 and not separater_needed:
                ret = True
            else:
                ret = False
        else:
            ret = False
    return ret


def permutation(string):
    '''
    (str) -> list ot str
    finds all the permutations of a string and sticks them into a list.
    >>> permutation("abc")
    ['abc', 'bac', 'bca', 'acb', 'cab', 'cba']
    '''
    # base case
    if len(string) == 1:
        return [string]
    # if length is 2, swap the chars and add both to the list
    elif len(string) == 2:
        return [string[0] + string[1], string[1] + string[0]]

    # get all permutations of length of string minus one character
    perms = permutation(string[1:])
    char = string[0]
    ret = []
    # iterate through every single element in permutation list
    for p in perms:
        # stick the character into every possible location between characters
        # including before and after
        for i in range(len(p) + 1):
            ret.append(p[:i] + char + p[i:])
    return ret


def all_regex_permutations(string):
    '''
    (str) -> set
    returns all possible valid regexes that can be permuted from the given
    string, stored in a set
    >>> all_regex_permutations("(1|2)") == {(1|2), (2|1)}
    True
    >>> all_regex_permutations("1*****") == {1*****}
    True
    >>> all_regex_permutations("what's up") == set()
    True
    '''
    ret = set()
    # checks if string contains only valid regex chars first
    if is_in(string):
        # if string happens to be a regex and starts with "120e", don't permute
        if string[0] in single_char and is_regex(string):
            ret.add(string)
            return ret
        else:
            # otherwise permute and add valid ones
            for i in permutation(string):
                if is_regex(i):
                    ret.add(i)
    return ret


def build_regex_tree(regex):
    '''
    (str) -> RegexTree
    takes a valid regex and builds a regextree from it, returning its root.
    REQ: must be a valid regex
    >>> build_regex_tree("1*").__eq__(StarTree(Leaf('1')))
    True
    >>> build_regex_tree("(1|0)*").__eq__(StarTree\
    (BarTree(Leaf('1'), Leaf(0))))
    True
    '''
    # base case single character given
    if len(regex) == 1 and regex in single_char:
        return Leaf(regex)
    # length of 2
    elif len(regex) == 2 and regex[0] in single_char and regex[1] == '*':
        return StarTree(regex[0])
    # last character is '*'
    elif len(regex) > 2 and regex[-1] == '*':
        return StarTree(build_regex_tree(regex[:-1]))
    # if brackets, just keep recursing to remove all leading '('
    elif regex[0] == '(':
        return build_regex_tree(regex[1:])

    # first char isn't a bracket, meaning that there's a separater
    elif regex[0] in single_char:
        left_bracket = regex.find("(")

        bar = regex.rfind('|')
        dot = regex.rfind('.')
        # remove all trailing ')'
        for i in range(len(regex)):
            if regex[-1] == ')':
                regex = regex[:-1]
        # if left bracket not found
        if left_bracket == -1:
            # if bar tree has to be made
            if bar > dot:
                return BarTree(build_regex_tree(regex[:bar]),
                               build_regex_tree(regex[bar + 1:]))
            # otherwise DotTree
            else:
                return DotTree(build_regex_tree(regex[:dot]),
                               build_regex_tree(regex[dot + 1:]))
        else:
            # if bar tree has to be made
            if regex[left_bracket - 1] == '|':
                return BarTree(build_regex_tree(regex[:left_bracket - 1]),
                               build_regex_tree(regex[left_bracket + 1:]))
            # otherwise dot tree
            else:
                return DotTree(build_regex_tree(regex[:left_bracket - 1]),
                               build_regex_tree(regex[left_bracket + 1:]))


def check_partitions(tree, string):
    '''
    (regextree, str) -> bool
    checks whether each possible partition of the string matches up with the
    tree.
    REQ: tree has to be a BarTree or a DotTree for it to make sense
    >>> check_partitions(BarTree(Leaf('1'), Leaf('2')), "11212212")
    True
    >>> check_partitions(DotTree(Leaf('1'), Leaf('2')), "11212212")
    False
    >>> check_partitions(BarTree(Leaf('1'), Leaf('2')), "11210212")
    False
    >>> check_partitions(DotTree(Leaf('1'), Leaf('2')), "12")
    True
    '''
    ret = True
    start = 0
    # go through every single substring/partition of given string
    while start < len(string) and ret:
        end = start + 1
        # go through first however many characters of the string
        while end <= len(string):
            # if they match check the next however many characters
            if match_helper(tree, string[start:end]):
                ret = True
                start = end
            else:
                ret = False
            end += 1
        start += 1
    return ret


def match_helper(tree, string):
    '''
    (regextree, str) -> bool
    returns True iff given string matches given regextree.
    REQ: given string contains only characters from "012", or nothing at all.
    >>> a = build_regex_tree("e*")
    >>> match_helper(a, "1")
    False
    >>> a = build_regex_tree("(1.e*)")
    >>> match_helper(a, "1")
    True
    >>> a = build_regex_tree("((1.2*)|(0|1))")
    >>> match_helper(a, "0")
    True
    >>> match_helper(a, "1222220")
    False
    '''
    # base case, just a leaf
    if isinstance(tree, Leaf):
        if tree.get_symbol() != 'e':
            return string == tree.get_symbol()
        else:
            return string == ''
    # BarTree below StarTree
    elif isinstance(tree, StarTree) and isinstance(tree.get_child(), BarTree):
        return check_partitions(tree.get_child(), string)

    # DotTree below StarTree
    elif isinstance(tree, StarTree) and isinstance(tree.get_child(), DotTree):
        return check_partitions(tree.get_child(), string)

    # StarTree below StarTree
    elif isinstance(tree, StarTree) and isinstance(tree.get_child(), StarTree):
        return match_helper(tree.get_child(), string)

    # if Star tree with child being a symbol
    elif tree.get_symbol() == '*' and (tree.get_child().get_symbol()) in "012e":
        if tree.get_child() != 'e':
            return string.replace(tree.get_child().get_symbol(), '') == ''
        else:
            return string == ''

    # if BarTree
    elif isinstance(tree, BarTree):
        # as long as at least one side of the tree is true then BarTree matches
        return (match_helper(tree.get_left_child(), string) or
                match_helper(tree.get_right_child(), string))
    # if DotTree
    elif isinstance(tree, DotTree):
        temp = False
        # keep splitting the string up into 2 until both are true
        # otherwise it's false
        for i in range(len(string) + 1):
            if (match_helper(tree.get_left_child(), string[:i]) and
                    match_helper(tree.get_right_child(), string[i:])):
                temp = True
        return temp


def regex_match(tree, string):
    '''
    (regextree, str) -> bool
    returns True iff given string matches given regextree.
    REQ: valid regex tree has to be given
    >>> a = build_regex_tree("e*")
    >>> regex_match(a, "1")
    False
    >>> a = build_regex_tree("(1.e*)")
    >>> regex_match(a, "1")
    True
    >>> a = build_regex_tree("((1.2*)|(0|1))")
    >>> regex_match(a, "0")
    True
    >>> regex_match(a, "1222220")
    False
    >>> regex_match(a, "N0t even a valid ternary string here")
    False
    '''
    ret = False
    # checks if given string is valid ternary string with only "012" or empty
    for i in string:
        if i not in "012":
            return False
    # run through the bulk of the function
    ret = match_helper(tree, string)
    return ret
