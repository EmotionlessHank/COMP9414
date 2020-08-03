import sys
from cspProblem import CSP
from cspProblem import Constraint
from cspConsistency import Search_with_AC_from_CSP
from searchGeneric import GreedySearcher
from operator import lt, ne, eq, gt
import linecache


# init a csp, and later we will send the all the constraints in it
class task_CSP(CSP) :
    def __init__(self, domain, hard_constraint, soft_constraint, soft_cost) :
        super().__init__(domain, hard_constraint)
        self.soft_constraint = soft_constraint
        self.soft_cost = soft_cost


# init a  ArcConsistency Searcher,and in it ,I add a heuristic part in Search_with_AC_from_CSP in order to solve the
# cost calculating problem
class ArcConsistencySearch(Search_with_AC_from_CSP) :
    def __init__(self, csp) :
        super().__init__(csp)
        self.cost = []
        self.soft_constraint = csp.soft_constraint
        self.soft_cost = csp.soft_cost

    def heuristic(self, node) :
        # cost = 0
        cost_list = []
        for t in node :
            if t in self.soft_constraint :
                cur_cost = []
                expecting_time = self.soft_constraint[t]
                for val in node[t] :
                    real_time = val[1]
                    # if the real time is bigger than expecting time, this will cause extra cost
                    if real_time > expecting_time :
                        real_time_day = int(str(real_time)[0])
                        expecting_time_day = int(str(expecting_time)[0])
                        # if the real time is in the same day with expecting time
                        # we just need to compare the rest of the string
                        if real_time_day == expecting_time_day :
                            delay = int(real_time - expecting_time)
                            cur_cost.append(self.soft_cost[t] * delay)
                        else :
                            delta = int(real_time_day - expecting_time_day)
                            real_moment = int(str(real_time)[1 :])
                            expecting_moment = int(str(expecting_time)[1 :])
                            delay = delta * 24 + int(real_moment - expecting_moment)
                            cur_cost.append(self.soft_cost[t] * delay)
                    else :
                        # else append a 0 cost to the list
                        cur_cost.append(0)
                # append the min cost, we need to find the optimal path
                if len(cur_cost) > 0 :
                    cost_list.append(min(cur_cost))
        cost = sum(cost_list)

        return cost

# define a func to process the line simply
def line_process(line) :
    line = line.strip()
    line = line.replace(',', '')
    line = line.split(' ')
    return line


# using a dict to store all the time strings. Later can call it easily
# I want to use enum, but it seems hard to implement
valid_time = {'9am' : 9, '10am' : 10, '11am' : 11, '12pm' : 12, '1pm' : 13, '2pm' : 14, '3pm' : 15, '4pm' : 16,
              '5pm' : 17}
# same, init a workday dict.
workday = {'mon' : 1, 'tue' : 2, 'wed' : 3, 'thu' : 4, 'fri' : 5}

# read from command lines
filename = sys.argv[1]
# filename = 'input8.txt'
file = open(filename, 'r', encoding='utf-8')

# using double 'for' loop to generate all the possible 3-digits value.
# like 110, the first digit '1' is represent the day in a week, 1 is mon, 2 is tue, etc.
# the second digit and the third digit is the time in a day, like 10 is 10am, 11 is 11am, 12 is 12pm, 13 is 1pm, etc.
domain_raw_list = list()
for day in range(1, 6) :
    for t in range(9, 18) :
        domain_raw_list.append(100 * day + t)
tasks_duration = {}
for line in file :
    var = []
    # get the duration first
    if 'task' in line and '#' not in line :
        line = line_process(line)
        tasks = line[1]
        tasks_duration[tasks] = int(line[2])

# next step, by using the task duration and the domain value list to generate all the valid ranges and append them
# into different list, like all the valid ranges in 't1', and 't1' is the key in domain_dict. example domain_dict:
# {'t1': [(109, 112), (110, 113), (111, 114), (112, 115), (113, 116), (114, 117), (209, 212), (210, 213), (211, 214),
# (212, 215), (213, 216), (214, 217), (309, 312), (310, 313), (311, 314), (312, 315), (313, 316), (314, 317), (409,
# 412), (410, 413), (411, 414), (412, 415), (413, 416), (414, 417), (509, 512), (510, 513), (511, 514), (512, 515),
# (513, 516), (514, 517)], 't2': [(109, 113), (110, 114), (111, 115), (112, 116), (113, 117), (209, 213), (210, 214),
# (211, 215), (212, 216), (213, 217), (309, 313), (310, 314), (311, 315), (312, 316), (313, 317), (409, 413), (410,
# 414), (411, 415), (412, 416), (413, 417), (509, 513), (510, 514), (511, 515), (512, 516), (513, 517)]}

# the range in list have two part, the first part is start time and the second part is end time.
# like, 't1': [(109, 112), the value of 't1' is a list, and first element of list is (109, 112).
# 109 is the start time, and 112 is the end time
domain_list = []
domain_dict = {}
for key in tasks_duration :
    cur_duration = tasks_duration[key]
    templist = []
    for i in set(domain_raw_list) :
        t = int(str(i)[1 :])
        if t + cur_duration > 17 :
            continue
        else :
            t = int(str(i)[0]) * 100 + int(t)
            templist.append((t, t + cur_duration))
    domain_dict[key] = templist
file.close()
# sort the key in the domain dict
sorted_dict_list = sorted(domain_dict.items(), key=lambda x : x[0], reverse=False)
sorted_dict = {}
for item in sorted_dict_list :
    sorted_dict[item[0]] = item[1]


# I use function to pack the condition if each constraint
def before_compare(x, y) :
    return x[1] <= y[0]


def same_day_compare(x, y) :
    return int(str(x[0])[0]) == int(str(y[0])[0])


def after_compare(x, y) :
    return x[0] >= y[1]


def starts_at_compare(x, y) :
    return x[0] == y[1]


def day_const(day) :
    condition = lambda x : int(str(x[0])[0]) == day
    return condition


def time_const(time) :
    condition = lambda x : int(str(x[0])[1 :]) == time
    return condition


def starts_before_const(date) :
    relation = lambda x : x[0] <= date
    return relation


def starts_after_const(date) :
    relation = lambda x : x[0] >= date
    return relation


def ends_before_const(date) :
    relation = lambda x : x[1] <= date
    return relation


def ends_after_const(date) :
    relation = lambda x : x[1] >= date
    return relation


def starts_in_const(f_date, b_date) :
    relation = lambda x : b_date >= x[0] >= f_date
    return relation


def ends_in_const(f_date, b_date) :
    relation = lambda x : b_date >= x[1] >= f_date
    return relation


def starts_before_only_time(time) :
    relation = lambda x : int(str(x[0])[1 :]) <= time
    return relation


def ends_before_only_time(time) :
    relation = lambda x : int(str(x[1])[1 :]) <= time
    return relation


def starts_after_only_time(time) :
    relation = lambda x : int(str(x[0])[1 :]) >= time
    return relation


def ends_after_only_time(time) :
    relation = lambda x : int(str(x[1])[1 :]) >= time
    return relation


# get the binary constraints
# hard_constraints_list is to store the hard constraints, seem to soft_constraints_dict and soft_cost_dict
hard_constraints_list = []
soft_constraints_dict = {}
soft_cost_dict = {}

# new method to find the binary constraints and domain constraint and soft const.
# the old method is in the last of the code, this one is much more simple.
# I check the csp examples code, in class constraints, there is a range list and a relation in it.
# so I init a scope contain two task name, and relation contain the Size relationship of two tasks.
file = open(filename, 'r', encoding='utf-8')
for line in file :
    line = line_process(line)

    # get the task name and fill in scope
    # this step is to get binary const
    if line[0] == 'constraint' :
        scope = (line[1], line[3])
        if line[2] == 'before' :
            # if t1 before t2, in here, I use lambda function to let t1.end_time <= t2.start_time
            hard_constraints_list.append(Constraint(scope, before_compare))
        elif line[2] == 'same-day' :
            hard_constraints_list.append(Constraint(scope, same_day_compare))
        elif line[2] == 'after' :
            hard_constraints_list.append(Constraint(scope, after_compare))
        elif line[2] == 'starts-at' :
            temp = starts_at_compare(scope[0], scope[1])
            hard_constraints_list.append(Constraint(scope, starts_at_compare))

    # get the domain constraints
    if line[0] == 'domain' and line[2] != 'ends-by' :
        check = line[2]
        if line[2] in workday :
            scope = (line[1],)
            hard_const_day = workday[line[2]]
            hard_constraints_list.append(Constraint(scope, day_const(hard_const_day)))
        elif line[2] in valid_time :
            scope = (line[1],)
            hard_const_time = valid_time[line[2]]
            hard_constraints_list.append(Constraint(scope, time_const(hard_const_time)))
        elif line[2] == 'starts-before' and len(line) == 5 :
            scope = (line[1],)
            target_date = int(workday[line[3]] * 100 + valid_time[line[4]])
            hard_constraints_list.append(Constraint(scope, starts_before_const(target_date)))
        elif line[2] == 'starts-after' and len(line) == 5 :
            scope = (line[1],)
            target_date = int(workday[line[3]] * 100 + valid_time[line[4]])
            hard_constraints_list.append(Constraint(scope, starts_after_const(target_date)))
        elif line[2] == 'ends-before' and len(line) == 5 :
            scope = (line[1],)
            target_date = int(workday[line[3]] * 100 + valid_time[line[4]])
            hard_constraints_list.append(Constraint(scope, ends_before_const(target_date)))
        elif line[2] == 'ends-after' and len(line) == 5 :
            scope = (line[1],)
            target_date = int(workday[line[3]] * 100 + valid_time[line[4]])
            hard_constraints_list.append(Constraint(scope, ends_after_const(target_date)))
        elif line[2] == 'starts-in' and len(line) == 6 :
            scope = (line[1],)
            # '<time>-<day> is in a same string, need to split them first'
            time_and_day = line[4].split('-', 1)
            front_time = time_and_day[0]
            back_day = time_and_day[1]
            front_date = int(workday[line[3]] * 100 + valid_time[front_time])
            back_date = int(workday[back_day] * 100 + valid_time[line[5]])
            hard_constraints_list.append(Constraint(scope, starts_in_const(front_date, back_date)))
        elif line[2] == 'ends-in' and len(line) == 6 :
            scope = (line[1],)
            time_and_day = line[4].split('-', 1)
            front_time = time_and_day[0]
            back_day = time_and_day[1]
            front_date = int(workday[line[3]] * 100 + valid_time[front_time])
            back_date = int(workday[back_day] * 100 + valid_time[line[5]])
            hard_constraints_list.append(Constraint(scope, ends_in_const(front_date, back_date)))
        elif line[2] == 'starts-before' and len(line) == 4 :
            scope = (line[1],)
            target_time = int(valid_time[line[3]])
            hard_constraints_list.append(Constraint(scope, starts_before_only_time(target_time)))
        elif line[2] == 'ends-before' and len(line) == 4 :
            scope = (line[1],)
            target_time = int(valid_time[line[3]])
            hard_constraints_list.append(Constraint(scope, ends_before_only_time(target_time)))
        elif line[2] == 'starts-after' and len(line) == 4 :
            scope = (line[1],)
            target_time = int(valid_time[line[3]])
            hard_constraints_list.append(Constraint(scope, starts_after_only_time(target_time)))
        elif line[2] == 'ends-after' and len(line) == 4 :
            scope = (line[1],)
            target_time = int(valid_time[line[3]])
            hard_constraints_list.append(Constraint(scope, ends_after_only_time(target_time)))

    # get the soft constraints
    if line[0] == 'domain' and line[2] == 'ends-by' :
        taskname = line[1]
        time_n_day = workday[line[3]] * 100 + valid_time[line[4]]
        soft_cost_dict[taskname] = int(line[5])
        soft_constraints_dict[taskname] = int(time_n_day)
file.close()

# call the GreedySearcher and using the ArcConsistency to solve the problem
CSP = task_CSP(sorted_dict, hard_constraints_list, soft_constraints_dict, soft_cost_dict)
# then input the task csp to ArcConsistencySearch that we have init before
problem_case = ArcConsistencySearch(CSP)
# init the greedy seacrcher with the CSP in it
GS = GreedySearcher(problem_case)
# call the search func and store the result
solution = GS.search()


# print the result in solution
day_in_week = 0
time_in_a_day = 0
# if we find the solution
if solution is not None:
    solution = solution.end()
    for taskname in solution :
        for i in workday :
            test1 = list(solution[taskname])
            test2 = list(solution[taskname])[0]
            test3 = list(solution[taskname])[0][0]
            test4 = list(solution[taskname])[0][0] // 100
            if workday[i] == list(solution[taskname])[0][0] // 100 :
                day_in_week = i
        for i in valid_time :
            test5 = list(solution[taskname])[0][0]
            test6 = list(solution[taskname])[0][0] % 100
            if valid_time[i] == list(solution[taskname])[0][0] % 100 :
                time_in_a_day = i
        print(f'{taskname}:{day_in_week} {time_in_a_day}')
    print(f'cost:{problem_case.heuristic(solution)}')

# else print no solution
else :
    print('No solution')
