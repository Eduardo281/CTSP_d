import gurobipy as gp

class CTSP_d_BaseModel(object):
    """Class to instantiate the common \"Base CTSP_d\" model, that is, a binary assignment model,
    with functions to solve the model, print variables, and more."""
    def __init__(self, data, relax=False, memLimit=None):
        self.data = data
        self.D = self.data["distances"]
        self.n = len(self.D)
        self.V = set(range(self.n))
        self.V_P = self.data["V_P"]
        self.P = len(self.V_P)
        self.d = self.data["d"]
        self.A = [(i, j) for i in self.V for j in self.V if(i != j)]

        self.route = []
        self.routeList = []

        self.x = set()
        self.u = set()
        self.y = set()

        if(memLimit):
            self.memLimit = memLimit
            self.env = gp.Env(empty=True)
            self.env.setParam("MemLimit", self.memLimit)
            self.env.start()
            self.model = gp.Model(env=self.env)
        else:
            self.model = gp.Model()
        self.relax = relax

        if(relax):
            self.x = self.model.addVars(self.A)
        else:
            self.x = self.model.addVars(self.A, vtype = gp.GRB.BINARY)

        # Objective Function
        self.model.setObjective(
            gp.quicksum(self.D[i][j] * self.x[i, j] for (i, j) in self.A), 
            sense = gp.GRB.MINIMIZE
        )

        # All nodes must be visited exactly one time
        self.c_1 = self.model.addConstrs(
            gp.quicksum(self.x[i, j] for i in self.V if (i, j) in self.A) == 1
            for j in self.V
        )

        # All nodes must be left exactly one time
        self.c_2 = self.model.addConstrs(
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A) == 1
            for i in self.V
        )

    def updateRoute(self):
        self.route = [(i, j) for (i, j) in self.A if self.x[i, j].X > 0.5]

    def updateRouteList(self):
        self.routeList = [0]
        self.v0 = 0
        self.v1 = -1
        while(self.v1 != 0):
            for item in self.route:
                if item[0] == self.v0:
                    self.v1 = item[1]
                    self.routeList.append(self.v1)
                    break
            self.v0 = self.v1

    def solve(self, time=None, heur=None, log=0):
        if(time != None):
            self.model.setParam("TimeLimit", time)
        if(heur != None):
            self.model.setParam("Heuristics", heur)
        if(log >= 0):
            try:
                self.model.Params.LogToConsole = log
            except:
                self.model.Params.LogToConsole = 1
        else:
            self.model.Params.LogToConsole = 1

        self.model.optimize()

        if(self.relax):
            return

        try:
            (self.x[self.A[0]].X <= 2) == True
        except:
            return
        self.updateRoute()
        self.updateRouteList()
        

    def printX(self, limX = 0.5):
        try:
            (self.x[self.A[0]].X <= 2) == True
        except:
            return
        for (i, j) in self.A:
            if(self.x[i, j].X > limX):
                print(f"x[{i}, {j}] = {self.x[i, j].X}")
        
    def routeToVars(self, route):
        self.model.reset()
        for (i, j) in route:
            self.x[i, j].start = 1
        self.model.update()
        self.route = route.copy()
        self.updateRouteList()

    def printRoute(self):
        if (self.route == []):
            print("No route available up to this moment!")
            return
        print("\nROUTE BUILT:\n")
        for item in self.routeList[:-1]:
            print(f"{item} -> ", end="")
        print("0", end="")
        print('\n')
        return

    def pass_initial_solution(self, init_sol):
        init_route = [(init_sol[i], init_sol[(i+1)]) for i in (range(len(init_sol)-1))]
        self.routeToVars(init_route)
        for pos, i in enumerate(init_sol):
            self.u[i].start = pos

    def printU(self):
        try:
            (self.u[0].X <= self.n) == True
        except:
            return
        for j in self.V:
            print(f"u[{j}] = {self.u[j].X}")

    def printY(self, limX = 0.5):
        try:
            (self.y[self.A[0]].X <= 2) == True
        except:
            return
        for (i, j) in self.A:
            if(self.y[i, j].X > limX):
                print(f"y[{i}, {j}] = {self.y[i, j].X}")

class MTZ_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the CTSP_d model based on the classic MTZ formulation for the TSP."""
    
    alias = "MTZ1"
    
    def __init__(self, data, relax=False, memLimit=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        if(relax):
            self.u = self.model.addVars(self.V, ub = self.n - 1)
        else:
            #self.u = self.model.addVars(self.V, vtype = gp.GRB.INTEGER, ub = self.n - 1)
            self.u = self.model.addVars(self.V, ub = self.n - 1)
        
        self.c_MTZ = self.model.addConstrs(
           self.u[i] - self.u[j] + self.n * self.x[i, j] <= self.n - 1
           for (i, j) in self.A if j != 0
        )

        self.c_MTZ_d_relax = self.model.addConstrs(
            self.u[i] + 1 <= self.u[j] for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if q > p + self.d
        )

class GP_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the CTSP_d model based on the Gouveia and Pires formulation for the TSP."""
    
    alias = "GP1"
    
    def __init__(self, data, relax=False, memLimit=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i > 0 and j > 0)
        ]

        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
        
        self.c_prec_1 = self.model.addConstrs(
            self.x[i, j] - self.y[i, j] <= 0 for (i, j) in self.non_zero_i_j
        )

        self.c_prec_2 = self.model.addConstrs(
            self.x[i, j] + self.y[j, i] <= 1 for (i, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) 
            if (i > 0 and j > 0 and k > 0)
        ]

        self.c_prec_3 = self.model.addConstrs(
            self.x[j, i] + self.x[i, j] + self.y[k, i] - self.y[k, j] <= 1
            for (i, j, k) in self.non_zero_i_j_k
        )

        self.c_prec_4 = self.model.addConstrs(
            self.x[k, j] + self.x[i, k] + self.x[i, j] + self.y[k, i] - self.y[k, j] <= 1
            for (i, j, k) in self.non_zero_i_j_k
        )

        del self.non_zero_i_j_k

        self.c_precedence_d_relax = self.model.addConstrs(
            self.y[i, j] == 1 for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A if q > p + self.d
        )

class SSB_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the CTSP_d model based on the SSB3 formulation for the TSP
    presented in Oncan et. al. (2009), originally proposed by Sarin et. al."""
    
    alias = "SSB1"
    
    def __init__(self, data, relax=False, memLimit=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
        
        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i > 0 and j > 0)
        ]

        self.c_prec_1 = self.model.addConstrs(
            self.y[i, j] >= self.x[i, j] for (i, j) in self.non_zero_i_j
        )

        self.c_prec_2 = self.model.addConstrs(
            self.y[i, j] + self.y[j, i] == 1 for (i, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) 
            if (i > 0 and j > 0 and k > 0)
        ]

        self.c_prec_3 = self.model.addConstrs(
            self.y[i, j] + self.x[j, i] + self.y[j, k] + self.y[k, i] <= 2
            for (i, j, k) in self.non_zero_i_j_k
        )

        del self.non_zero_i_j_k

        self.VI_SSB = self.model.addConstrs(
            self.x[0, j] + self.x[j, 0] <= 1 for j in self.V if j > 0
        )

        self.c_precedence_d_relax = self.model.addConstrs(
            self.y[i, j] == 1 for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A if q > p + self.d
        )

class SST_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the CTSP_d model based on the SST2 formulation for the TSP
    presented in Oncan et. al. (2009), originally proposed by Sherali et. al. (2006)."""
    
    alias = "SST1"
    
    def __init__(self, data, relax=False, memLimit=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) 
            if (i > 0 and j > 0 and k > 0)
        ]

        if(relax):
            self.y = self.model.addVars(self.A)
            self.t = self.model.addVars(self.non_zero_i_j_k)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
            self.t = self.model.addVars(self.non_zero_i_j_k, vtype = gp.GRB.BINARY)
        
        self.SST_51 = self.model.addConstrs(
           self.y[i, j] + self.x[j, i] + self.y[j, k] + self.y[k, i] <= 2
           for (i, j, k) in self.non_zero_i_j_k
        )

        self.SST_57 = self.model.addConstrs(
            self.t[i, j, k] <= self.x[i, k] for (i, j, k) in self.non_zero_i_j_k
        )

        del self.non_zero_i_j_k

        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i > 0 and j > 0)
        ]

        self.SST_49 = self.model.addConstrs(
           self.y[i, j] + self.y[j, i] == 1 for (i, j) in self.non_zero_i_j
        )
        
        self.SST_54 = self.model.addConstrs(
           self.y[i, j] >= self.x[0, i] for (i, j) in self.non_zero_i_j
        )

        self.SST_55 = self.model.addConstrs(
           self.y[j, i] >= self.x[i, 0] for (i, j) in self.non_zero_i_j
        )

        self.SST_58 = self.model.addConstrs(
            gp.quicksum(self.t[i, j, k] for k in self.V if k > 0 if k != i if k != j) + self.x[i, j] == self.y[i, j] 
            for (i, j) in self.non_zero_i_j
        )

        self.SST_59 = self.model.addConstrs(
            self.x[0, k] + gp.quicksum(self.t[i, j, k] for i in self.V if i > 0 if i != j if i != k) == self.y[k, j]
            for (k, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        self.c_precedence_d_relax = self.model.addConstrs(
            self.y[i, j] == 1 for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A if q > p + self.d
        )
