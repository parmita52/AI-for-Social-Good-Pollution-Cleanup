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

# load data into dataframe
df = pd.read_csv('data/synthetic.csv', sep=",")
df[P] = df[P]*18.9*500000
grouped = df.groupby(df.Zone)
counties = grouped.groups.keys()
for county in counties:
    county_df = grouped.get_group(county)
    # total number of volunteers for this county
    total_volunteers = county_df['Volunteers'].sum()
    # normalize other factors
    normalized_county_df = county_df[[G, W, S, P]].copy()
    for feature_name in normalized_county_df.columns:
        max_value = county_df[feature_name].max()
        min_value = county_df[feature_name].min()
        normalized_county_df[feature_name] = (
            county_df[feature_name]-min_value)/(max_value-min_value + 1)
    normalized_r = r/(county_df[G].max())

    # structures to store the input
    beach_dict = {}
    beach_volunteers = []
    beach_indicators = []
    # Instantiate the problem class
    lp_name = (str(county)).replace(" ", "_") + "_LP"
    lp_problem = pulp.LpProblem(lp_name, pulp.LpMaximize)

    # each entry in dataframe
    i = 0
    for index, b in normalized_county_df.iterrows():
        # create a beach object
        beach_obj = Beach("", b[G], b[W], b[S], b[P])
        # add it to the dictionary
        beach_dict[i] = beach_obj
        i += 1
        # create lp variables
        var_id = 'volunteers_' + str(index)
        v = pulp.LpVariable(var_id, lowBound=0, cat='Integer')
        var_id = 'indicator_' + str(index)
        I = pulp.LpVariable(var_id, lowBound=0, upBound=1, cat='Integer')
        # add it to the list of variables
        beach_volunteers.append(v)
        beach_indicators.append(I)

    num_beaches = len(beach_dict)

    # Objective function
    # weights
    cv = 0.3  # pollution cleaned
    cw = 0.1  # wildlife
    cs = 0.5  # safety
    cp = 0.1  # population

    # SUMi : vi(cv * r  +  cw * wi)  + Ii(cs * si  + cp * pi) + (0 - Ii)

    lp_problem += pulp.lpSum(
        (
            beach_volunteers[i] *
            (
                cv*normalized_r +
                cw*beach_dict[i].get_w()
            )

            +

            beach_indicators[i] *
            (
                cs*beach_dict[i].get_s() +
                cp*beach_dict[i].get_p()
            )

            +

            (0 - 1*beach_indicators[i])
        )
        for i in range(num_beaches)
    ), "Pollution Cleanup"

    # Constraints
    for i in range(num_beaches):
        # r*v_i <= g_i (unnormalized)
        # lp_problem += r*beach_volunteers[i] <= df.at[i, G]

        # vi <= (total_volunteers) * Ii
        lp_problem += beach_volunteers[i] <= (total_volunteers) * \
            (beach_indicators[i])

    # SUMi vi <= total_volunteers
    lp_problem += pulp.lpSum(beach_volunteers[i]
                             for i in range(num_beaches)) <= total_volunteers

    lp_problem += pulp.lpSum(beach_volunteers[i]
                             for i in range(num_beaches)) >= total_volunteers

    # print(lp_problem)
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
    # print(pulp.LpStatus[lp_problem.status])
    # this will print: Optimal out of the choices:
    '''
    Not Solved: Status prior to solving the problem.
    Optimal: An optimal solution has been found.
    Infeasible: There are no feasible solutions (e.g. if you set the constraints x <= 1 and x >=2).
    Unbounded: The constraints are not bounded, maximising the solution will tend towards infinity (e.g. if the only constraint was x >= 3).
    Undefined: The optimal solution may exist but may not have been found.
    '''

    # print the variable assignemnts
    sum = 0
    sumi = 0
    for variable in lp_problem.variables():
        # print("{} = {}".format(variable.name, variable.varValue))
        if "volunteer" in (variable.name):
            sum += variable.varValue
        if "indicator" in (variable.name):
            sumi += variable.varValue

    if sumi >= 2:
        print("************")
        print(sumi)
        print(lp_problem)

    # print the objective
    # print(pulp.value(lp_problem.objective))
