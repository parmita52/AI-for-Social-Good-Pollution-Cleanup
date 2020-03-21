# this is for testing PuLP for Linear Programming
import pulp

# example LP jus tto see it in action
'''
x ≥ 0
y ≥ 2
2y ≤ 25 - x
4y ≥ 2x - 8
y ≤ 2x - 5

Maximize Z = 4x + 3y
'''

my_lp_problem = pulp.LpProblem("MyLPProblem", pulp.LpMaximize)

# x ≥ 0
x = pulp.LpVariable('x', lowBound=0, cat='Continuous')
# y ≥ 2
y = pulp.LpVariable('y', lowBound=2, cat='Continuous')

# Objective function
my_lp_problem += 4 * x + 3 * y, "Z"

# Constraints
my_lp_problem += 2 * y <= 25 - x
my_lp_problem += 4 * y >= 2 * x - 8
my_lp_problem += y <= 2 * x - 5

print(my_lp_problem)
# this will print:
'''
MyLPProblem:
MAXIMIZE
4*x + 3*y + 0
SUBJECT TO
_C1: x + 2 y <= 25

_C2: - 2 x + 4 y >= -8

_C3: - 2 x + y <= -5

VARIABLES
x Continuous
2 <= y Continuous
'''

# Solve it!
my_lp_problem.solve()
print(pulp.LpStatus[my_lp_problem.status])
# this will print: Optimal out of the choices:
'''
Not Solved: Status prior to solving the problem.
Optimal: An optimal solution has been found.
Infeasible: There are no feasible solutions (e.g. if you set the constraints x <= 1 and x >=2).
Unbounded: The constraints are not bounded, maximising the solution will tend towards infinity (e.g. if the only constraint was x >= 3).
Undefined: The optimal solution may exist but may not have been found.
'''

# print the variable assignemnts
for variable in my_lp_problem.variables():
    print("{} = {}".format(variable.name, variable.varValue))

# print the objective
print(pulp.value(my_lp_problem.objective))
