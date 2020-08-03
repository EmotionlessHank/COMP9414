import sys
from cspProblem import CSP, Constraint
from cspConsistency import Search_with_AC_from_CSP
from searchGeneric import AStarSearcher


###############################################################################3
# Change class display in display.py:
# change 'max_display_level = 1 to 'max_display_level = 0'
# this is to disable the display function to print the expanded path
#################################################################################
# Change class Arc in searchProblem.py:
# change def __init__(self, from_node, to_node, cost=1, action=None):
# to  def __init__(self, from_node, to_node, cost=0, action=None):
# as in this meeting arrangement problem, no arc cost from one node to next node
#################################################################################


#######################################################
############ extend CSP class #########################
# add self.soft_constraints to store soft constraints which is a dict with format {'t1': ['end-by    ']}
# add soft_cost {t1:}
class New_CSP(CSP):
    def __init__(self,domains,constraints,soft_constraints,soft_cost):
        super().__init__(domains,constraints)
        self.soft_constraints = soft_constraints
        self.soft_cost = soft_cost

class Search_with_AC_from_Cost_CSP(Search_with_AC_from_CSP):
    def __init__(self,csp):
        super().__init__(csp)
        self.cost = []
        self.soft_cons = csp.soft_constraints
        self.soft_cost = soft_cost

    def heuristic(self,node):
        cost = 0
        cost_list = []
        for task in node:
            if task in self.soft_cons:
                temp = []
                expect_time = self.soft_cons[task]
                for value in node[task]:
                    actual_time = value[1]
                    if actual_time > expect_time:
                        delay = (actual_time//10- expect_time//10)*24 + ((actual_time%10) - (expect_time%10))
                        temp.append(self.soft_cost[task] * delay)
                    else:
                        temp.append(0)

                if len(temp)!=0:
                    cost_list.append(min(temp))

        cost = sum(cost_list)

        return cost


####################################################
######### binary constraint ########################
####################################################
def binary_before(t1,t2):
    return t1[1]<=t2[0]

def binary_same_day(t1,t2):
    return t1[0]//10 == t2[0]//10




####################################################
######### hard constraint ##########################
####################################################

def hard_day(day):
    hardday = lambda x: x[0]//10 ==day
    '''
    def hardday(val):
        return val[0]//10 ==day
    '''
    return hardday

def hard_time(time):
    def hardtime(val):
        return val[0] % 10 == time
    return hardtime




#filename = sys.argv[1]
filename = 'input1.txt'
file =  open(filename,'r', encoding = 'utf-8')
for line in file:
    #Remove '\n'
    task_duration = {}
    week_to_num = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5}
    time_to_num = {'9am': 1, '10am': 2, '11am':3, '12pm': 4, '1pm': 5, '2pm': 6, '3pm': 7, '4pm': 8, '5pm':9}
    domain =set()
    for i in range(1,6):
        for j in range(1,10):
            domain.add(i*10+j)
    #print(sorted(domain))
    task_domain = {}
    hard_constraint = []
    soft_constraint = {}
    soft_cost = {}
    task_list = []
    #get varible and domain
    if 'tasks' in line:
        for line in file:
            if '#' in line:
                break
            line = line.strip()
            line = line.replace(',', '')
            line = line.split(' ')
            task_duration[line[1]] = int(line[2])

    for task in task_duration:
        di = set()
        duration = task_duration[task]
        for item in domain:
            if item % 10 + int(duration) <=9:
                di.add(item)
        task_domain[task] = sorted(set((x,x+duration) for x in di))


    #get binary constraints
    if 'binary' in line:
        for line in file:
            if '#' in line:
                break
            line = line.strip()
            line = line.replace(',','')
            line = line.split(' ')
            #print(line)
            t1 = line[1]
            t2 = line[3]
            if line[2] == 'before':
                #print('hhhhhhhh')
                hard_constraint.append(Constraint((t1,t2),binary_before))

            if line[2] == 'after':
                pass

            if line[2] == 'same-day':
                hard_constraint.append(Constraint((t1,t2),binary_same_day))

            if line[2] =='starts-at':
                pass


    #get hard fomain
    if 'domain' in line:
        for line in file:
            if '#' in line:
                break
            line = line.strip()
            line = line.replace(',', '')
            line = line.split(' ')
            t = line[1]

            # domain, t day
            if line[2] in week_to_num:
                day = week_to_num[line[2]]
                hard_constraint.append(Constraint((t,),hard_day(day)))

            # domain, t time
            if line[2] in time_to_num:
                time = time_to_num[line[2]]
                hard_constraint.append(Constraint((t,),hard_time(time)))
            #
            #
            #
            # add other hard domain constraints by yourself
            #
            #
            #


    # get soft_domain
    if 'soft' in line:
        for line in file:
            if '#' in line:
                break
            line = line.strip()
            line = line.replace(',', '')
            line = line.split(' ')
            tasks = line[1]
            day = week_to_num[line[3]]
            time = time_to_num[line[4]]
            soft_cost[tasks] = int(line[-1])
            soft_constraint[tasks] = day*10 + time

#print(soft_constraint)
#print(hard_constraint)
#print(task_domain)

csp = New_CSP(task_domain,hard_constraint,soft_constraint,soft_cost)
problem = Search_with_AC_from_Cost_CSP(csp)
solution = AStarSearcher(problem).search()

#print(solution)

if solution:
    solution = solution.end()
    for task in solution:
        for item in week_to_num:
            if week_to_num[item] ==list(solution[task])[0][0]//10:
                day = item
        for item in time_to_num:
            if time_to_num[item] == list(solution[task])[0][0]%10:
                time = item
        print(f'{task}:{day} {time}')
    print(f'cost:{problem.heuristic(solution)}')
else:
    print('No solution')
