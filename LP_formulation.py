import pulp
import xlrd

class Beach:
    def __init__(self, name, g, w, s, p, d):
        self.name = name
        self.g = g # grams of plastic pollution
        self.w = w # vulnerable marine wildlife population
        self.s = s # safety score and terrain
        self.p = p # population around area
        self.d = d # distance from closest populated hub

    def get_name(self):
        return self.name
    def get_g(self):
        return self.g
    def get_w(self):
        return self.w
    def get_s(self):
        return self.s
    def get_p(self):
        return self.p
    def get_d(self):
        return self.d

# Global variables
r = 50 # rate of cleanup (average grams of plastic picked up per hour, by one volunteer)
min_x = 2 # minimum number of volunteers at a beach
total_volunteers = 10 # total number of volunteers who have signed up

# synthesized data saved in a dictionary
# TODO: import data from excel sheet
beach_dict = {}

beach_0 = Beach("0", 230, 2.3, 5, 5, 1)
beach_1 = Beach("1", 5699, 0.02, 4, 5, 1)
beach_2 = Beach("2", 7800, 0.05, 3, 5, 1)
beach_3 = Beach("3", 9289, 0.7, 4, 5, 1)
beach_4 = Beach("4", 802, 0.6, 5, 5, 1)

beach_dict[0] = beach_0
beach_dict[1] = beach_1
beach_dict[2] = beach_2
beach_dict[3] = beach_3
beach_dict[4] = beach_4

num_beaches = 5

# Instantiate the problem class
lp_problem = pulp.LpProblem("Pollution_Cleanup_Maximizing_Problem", pulp.LpMaximize)

# volunteers_i >= 0 for all i
x0 = pulp.LpVariable('volunteers_0', lowBound=0, cat='Integer')
x1 = pulp.LpVariable('volunteers_1', lowBound=0, cat='Integer')
x2 = pulp.LpVariable('volunteers_2', lowBound=0, cat='Integer')
x3 = pulp.LpVariable('volunteers_3', lowBound=0, cat='Integer')
x4 = pulp.LpVariable('volunteers_4', lowBound=0, cat='Integer')

# array of variables for # volunteers at each beach
beach_volunteers = [x0, x1, x2, x3, x4]

# array of variables for # hours to hold cleanup at each beach
# hours_i >= 1 for all i
'''
cleanup_hours = [y0, y1, y2, y3, y4]
for i in range(num_beaches):
    cleanup_hours[i] = pulp.LpVariable('hours_'+str(i), lowBound=1, cat='Integer')
'''
cleanup_hours = [2,2,2,2,2] # setting constant for now

# Objective function
c1 = 3
c2 = 1
c3 = 0.5
c4 = 0.3

# There's a problem with the indicator variable in this part, so commenting out for now
'''
lp_problem += pulp.lpSum(
    ((int(beach_volunteers[i]) > min_x) * # I_i
        (c1*r*beach_volunteers[i]*cleanup_hours[i]*beach_dict[i].get_w() # c1*A_i*w_i where A_i = r*v_i*h_i
        + c2*beach_dict[i].get_s() # c2*s_i
        + c3*beach_dict[i].get_p() # c3*p_i
        + c4*beach_dict[i].get_d() # c4*d_i
        )) 
    for i in range(num_beaches)), "Pollution Cleanup"
'''

lp_problem += pulp.lpSum(
        (c1*r*beach_volunteers[i]*cleanup_hours[i]*beach_dict[i].get_w() # c1*A_i*w_i where A_i = r*v_i*h_i
        + c2*beach_dict[i].get_s() # c2*s_i
        + c3*beach_dict[i].get_p() # c3*p_i
        + c4*beach_dict[i].get_d() # c4*d_i
        )
    for i in range(num_beaches)), "Pollution Cleanup"

# Constraints
for i in range(num_beaches):
    lp_problem += r*beach_volunteers[i]*cleanup_hours[i] <= beach_dict[i].get_g() # A_i <= g_i
    lp_problem += pulp.lpSum(beach_volunteers[i] for i in range(num_beaches)) <= total_volunteers

print(lp_problem)
# this will print:
'''
LP Problem:
MAXIMIZE
...
SUBJECT TO
...
VARIABLES
...
'''

# Solve it!
lp_problem.solve()
print(pulp.LpStatus[lp_problem.status])
# this will print: Optimal out of the choices:
'''
Not Solved: Status prior to solving the problem.
Optimal: An optimal solution has been found.
Infeasible: There are no feasible solutions (e.g. if you set the constraints x <= 1 and x >=2).
Unbounded: The constraints are not bounded, maximising the solution will tend towards infinity (e.g. if the only constraint was x >= 3).
Undefined: The optimal solution may exist but may not have been found.
'''

# print the variable assignemnts
for variable in lp_problem.variables():
    print("{} = {}".format(variable.name, variable.varValue))

# print the objective
print(pulp.value(lp_problem.objective))