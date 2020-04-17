import pulp
import pandas as pd

# column names for accessing the data
NAME = "Name"
G = "Pollution"
W = "Wildlife"
S = "Safety"
P = "Population"


# class for each individual beach
class Beach:
    def __init__(self, name, g, w, s, p):
        self.name = name
        self.g = g  # grams of plastic pollution
        self.w = w  # vulnerable marine wildlife population
        self.s = s  # safety score and terrain
        self.p = p  # population around area

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


# Global variables
# rate of cleanup (average grams of plastic picked up per hour, by one volunteer)
r = 12305.56
# minimum number of volunteers at a beach
min_x = 2
total_volunteers = 10  # total number of volunteers who have signed up

# structures to store the input
beach_dict = {}
beach_volunteers = []
# Instantiate the problem class
lp_problem = pulp.LpProblem(
    "Pollution_Cleanup_Maximizing_Problem", pulp.LpMaximize)

# load data into dataframe
df = pd.read_csv('data/test.csv', sep=",")

normalized_df = df.copy()
for feature_name in df.columns:
    if feature_name != NAME:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        normalized_df[feature_name] = (
            df[feature_name]-min_value)/(max_value-min_value)

normalized_r = r/(df[G].max())

# each entry in dataframe
for index, b in normalized_df.iterrows():
    # create a beach object
    beach_obj = Beach(b[NAME], b[G], b[W], b[S], b[P])
    # add it to the dictionary
    beach_dict[index] = beach_obj
    # create an lp variable
    var_id = 'volunteers_' + str(index)
    x = pulp.LpVariable(var_id, lowBound=0, cat='Integer')
    # add it to the list of variables
    beach_volunteers.append(x)

num_beaches = len(beach_dict)

# Objective function
# weights
cv = 0.10  # pollution cleaned
cw = 0.10  # wildlife
cs = 0.10  # safety
cp = 0.70  # population

lp_problem += pulp.lpSum(
    (beach_volunteers[i] *
     (cv*normalized_r             # cv*normalized_r
      + cw*beach_dict[i].get_w()  # cw*w_i
      + cs*beach_dict[i].get_s()  # cs*s_i
      + cp*beach_dict[i].get_p())  # cp*p_i
     )
    for i in range(num_beaches)), "Pollution Cleanup"

# Constraints
for i in range(num_beaches):
    # r*v_i <= g_i (unnormalized)
    lp_problem += r*beach_volunteers[i] <= df.at[i, G]

lp_problem += pulp.lpSum(beach_volunteers[i]
                         for i in range(num_beaches)) <= total_volunteers

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
