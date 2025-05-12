import gurobipy as gp

class CTSP_d_BaseModel(object):
    """Class to instantiate the common \"Base CTSP_d\" model, that is, a binary assignment model,
    with functions to solve the model, print variables, and more. Not intented to represent any
    TSP model by itself, but it is used as the initial class for all the models.

    Attributes
    ----------
    data : dict
        Stores the data parameter passed in input.
    relax : bool
        Stores the relax parameter passed in input.
    memLimit : int
        Stores the memLimit parameter passed in input.
    D : list[list[int]]
        Distance matrix of the instance.
    n : int
        Quantity of vertices in the instance.
    V : set[int]
        Set of vertices of the instance.
    V_P: list[list[int]]
        Priorities sets of the instance.
    P : int
        Quantity of priorities sets in the instance.
    d : int
        Parameter d used to define the CTSP-d.
    A : list[tuple[int, int]]
        List of arcs (i, j) of the instance.
    route : list[tuple[int, int]]
        List of arcs (i, j) included in the solution (unordered).
    routeList : list[int]
        Sequence of vertices visited in the solution (ordered)
    x : gp.tupledict
        Variables x of the model.
        A set of binary variables x[i, j], defined for all (i, j) in A.
        Represent if an arc (i, j) is included in the solution.
    u : gp.tupledict
        Variables u of the model.
        A set of linear variables u[j], defined for all j in V.
        Represent the position of the vertex j in the solution.
        Used in the models MTZ1, MTZ2 and H2020.
    y : gp.tupledict
        Variables y of the model.
        A set of binary variables y[i, j], defined for all (i, j) in A.
        Represent if i precedes j (not necessarily immediately) in the solution.
        Used in the models GP1, GP2, SSB1, SSB2, SST1 and SST2.
    env : gp.Env
        A Gurobi environment to build the model.
    model : gp.Model
        The Gurobi model variable.
    cstrTSP1 : gp.tupledict
        Constraints set imposing that every city must be visited exactly once.
    cstrTSP2 : gp.tupledict
        Constraints set imposing that every city must be left exactly once.
    """
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        """Member initializer for CTSP_d_BaseModel class
        
        Parameters
        ----------
        data : dict
            All the data needed to represent an instance of the CTSP-d.
            Must have the following fields:
            * "distances": Distance matrix (list[list[int or float]]);
            * "V_P": Priorities sets (list[list[int]]);
            * "d": The d parameter (int);
            * "instance_name": Instance name (str). Used only if export function is called.
        relax : bool, default=False
            Allow to build a model with no integer variables.
        memLimit : int, default=None
            Allow to limit the total RAM memory used by Gurobi in Gb.
        """
        self.data = data
        self.relax = relax
        self.memLimit = memLimit
        
        self.D = self.data["distances"]
        self.n = len(self.D)
        self.V = set(range(self.n))
        self.V_P = self.data["V_P"]
        self.P = len(self.V_P)
        self.d = self.data["d"]
        self.A = [(i, j) for i in self.V for j in self.V if(i != j)]

        self.route = [] 
        self.routeList = []

        self.x = gp.tupledict()
        self.u = gp.tupledict()
        self.y = gp.tupledict()

        self.env = gp.Env(empty=True)
        
        if(memLimit):
            self.env.setParam("MemLimit", self.memLimit)

        self.env.start()
        self.model = gp.Model(env=self.env)            

        # Variables set:
        # Creating the x variables - used in all the models
        if(relax):
            self.x = self.model.addVars(self.A)
        else:
            self.x = self.model.addVars(self.A, vtype = gp.GRB.BINARY)

        # Objective Function (1): 
        # To minimize the total route distance
        self.model.setObjective(
            gp.quicksum(self.D[i][j] * self.x[i, j] for (i, j) in self.A), 
            sense = gp.GRB.MINIMIZE
        )

        # Constraints set (2): 
        # All nodes must be visited exactly once
        self.cstrTSP1 = self.model.addConstrs(
            gp.quicksum(self.x[i, j] for i in self.V if (i, j) in self.A) == 1
            for j in self.V
        )

        # Constraints set (3): 
        # All nodes must be left exactly once
        self.cstrTSP2 = self.model.addConstrs(
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A) == 1
            for i in self.V
        )

    def updateRoute(self) -> None:
        """Updates self.route using the model variables."""
        self.route = [(i, j) for (i, j) in self.A if self.x[i, j].X > 0.5]

    def updateRouteList(self) -> None:
        """Updates self.routeList using the arcs in self.route."""
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

    def solve(
            self, 
            time: float=None, 
            heur: float=None, 
            log: bool=False
        ) -> None:
        """Calls Gurobi to solve the problem. If relax was set to false and a 
        feasible solution is found, it automatically updates the route and 
        routeList variables too.
        
        Parameters
        ----------
        time : float
            Total runtime passed to Gurobi.
            If the solving process do not end after "time" seconds,
            Gurobi will stop as soon as possible.
        heur : float, default=None
            Amount of time Gurobi will spent in MIP heuristics. According to the
            documentation, it can be seen as the desired fraction of total MIP
            runtime devoted to heuristics. Do not specifying a value meaning
            it will be used the Gurobi default value.
        log : bool, default=False
            Allow to enable or disable Gurobi console logging.
        """
        if(time != None):
            self.model.setParam("TimeLimit", time)
        if(heur != None):
            self.model.setParam("Heuristics", heur)
        if(log != None):
            self.model.setParam("LogToConsole", log)

        self.model.optimize()

        if(self.relax):
            return

        try:
            (self.x[self.A[0]].X <= 2) == True
        except:
            return
        
        self.updateRoute()
        self.updateRouteList()
        
    def printX(self, limX: float = 0.5) -> None:
        """Prints the x variables on the terminal.
        
        Parameters
        ----------
        limX : float, default=0.5
            Only variables satisfying x >= limX will be printed.
        """
        try:
            (self.x[self.A[0]].X <= 2) == True
        except:
            return
        for (i, j) in self.A:
            if(self.x[i, j].X > limX):
                print(f"x[{i}, {j}] = {self.x[i, j].X}")
        
    def printRoute(self) -> None:
        """Prints the solution route using the self.routeList values."""
        if (self.routeList == []):
            print("No route available up to this moment!")
            return
        print("\nROUTE BUILT:\n")
        for item in self.routeList[:-1]:
            print(f"{item} -> ", end="")
        print(self.routeList[-1], end="")
        print('\n')
        return

    def printU(self) -> None:
        """Prints the u variables on the terminal."""
        try:
            (self.u[0].X <= self.n) == True
        except:
            return
        for j in self.V:
            print(f"u[{j}] = {self.u[j].X}")

    def printY(self, limY = 0.5):
        """Prints the y variables on the terminal.
        
        Parameters
        ----------
        limy : float, default=0.5
            Only variables satisfying y >= limY will be printed.
        """
        try:
            (self.y[self.A[0]].X <= 2) == True
        except:
            return
        for (i, j) in self.A:
            if(self.y[i, j].X > limY):
                print(f"y[{i}, {j}] = {self.y[i, j].X}")

class MTZ_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the MTZ1 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (MTZ1).
    """
    
    alias = "MTZ1"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        # Variables set:
        # Creating the u variables.
        self.u = self.model.addVars(self.V, ub = self.n - 1)

        # Constraints set (7):
        # The classical MTZ subtour removal constraint.
        # Impose the u variables meaning - the position of the vertices in a feasible solution
        self.cstrMTZ = self.model.addConstrs(
           self.u[i] - self.u[j] + self.n * self.x[i, j] <= self.n - 1
           for (i, j) in self.A if j != 0
        )

        # Constraints set (8):
        # The d-relaxed priority rule constraint, as proposed by Hà et. al. (2020)
        self.cstrMTZdRelax = self.model.addConstrs(
            self.u[i] + 1 <= self.u[j] for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if q > p + self.d
        )

class GP_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the GP1 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (GP1).
    """
    
    alias = "GP1"
    
    def __init__(self, data : dict, relax: bool=False, memLimit: int=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        # Variables set:
        # Creating the y variables.
        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)

        # Auxiliary set
        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i > 0 and j > 0)
        ]

        # Constraints set (31):
        # If j is the successor of i in the tour, then i precedes j in the tour.
        # If i does not precede j in the tour, then j cannot be the successor of i.
        self.cstrPrecedence1 = self.model.addConstrs(
            self.x[i, j] - self.y[i, j] <= 0 for (i, j) in self.non_zero_i_j
        )

        # Constraints set (32):
        # If j is the successor of i, then j does not precede i.
        # If j precedes i, then j is not the successor of i in the tour.
        self.cstrPrecedence2 = self.model.addConstrs(
            self.x[i, j] + self.y[j, i] <= 1 for (i, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        # Auxiliary set
        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) 
            if (i > 0 and j > 0 and k > 0)
        ]

        # Constraints set (33):
        # When arc (i, j) is included in the tour, then y_ki <= y_kj, for all non zero k, that is, 
        # every vertex k that precedes i in the tour must necessarily precede j.
        self.cstrPrecedence3 = self.model.addConstrs(
            self.x[j, i] + self.x[i, j] + self.y[k, i] - self.y[k, j] <= 1
            for (i, j, k) in self.non_zero_i_j_k
        )

        # Constraints set (34):
        # Represent the same condition that cstrPrecedence3. Included to make the formulation stronger.
        self.cstrPrecedence4 = self.model.addConstrs(
            self.x[k, j] + self.x[i, k] + self.x[i, j] + self.y[k, i] - self.y[k, j] <= 1
            for (i, j, k) in self.non_zero_i_j_k
        )

        del self.non_zero_i_j_k

        # Constraints set (30):
        # The d-relaxed priority rule constraint formulated using the precedence variables.
        self.cstrPrecedenceDRelax = self.model.addConstrs(
            self.y[i, j] == 1 for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A if q > p + self.d
        )

class SSB_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the SSB1 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (SSB1).
    """
    
    alias = "SSB1"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        # Variables set:
        # Creating the y variables.
        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
        
        # Auxiliary set
        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i > 0 and j > 0)
        ]

        # Constraints set (36):
        # If j is the successor of i in the tour, then i precedes j in the tour.
        # If i does not precede j in the tour, then j cannot be the successor of i.
        self.cstrPrecedence1 = self.model.addConstrs(
            self.y[i, j] >= self.x[i, j] for (i, j) in self.non_zero_i_j
        )

        # Constraints set (37):
        # Given two distinct vertices i and j, then j must be before or after i.
        self.cstrPrecedence2 = self.model.addConstrs(
            self.y[i, j] + self.y[j, i] == 1 for (i, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        # Auxiliary set
        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) 
            if (i > 0 and j > 0 and k > 0)
        ]

        # Constraints set (38):
        # Ensure that y_ij = 1 if, and only if, j is the successor of i in the tour.
        self.cstrPrecedence3 = self.model.addConstrs(
            self.y[i, j] + self.x[j, i] + self.y[j, k] + self.y[k, i] <= 2
            for (i, j, k) in self.non_zero_i_j_k
        )

        del self.non_zero_i_j_k

        # Constraints set (39):
        # No vertex j can be successor and predecessor of the origin at the same time.
        self.cstrPrecedence4 = self.model.addConstrs(
            self.x[0, j] + self.x[j, 0] <= 1 for j in self.V if j > 0
        )

        # Constraints set (30):
        # The d-relaxed priority rule constraint formulated using the precedence variables.
        self.cstrPrecedenceDRelax = self.model.addConstrs(
            self.y[i, j] == 1 for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A if q > p + self.d
        )

class SST_CTSP_d_Model(CTSP_d_BaseModel):
    """Class to instantiate the SST1 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (SST1).
    """
    
    alias = "SST1"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        # Auxiliary set
        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) 
            if (i > 0 and j > 0 and k > 0)
        ]

        # Variables set:
        # Creating the y and t variables.
        if(relax):
            self.y = self.model.addVars(self.A)
            self.t = self.model.addVars(self.non_zero_i_j_k)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
            self.t = self.model.addVars(self.non_zero_i_j_k, vtype = gp.GRB.BINARY)

        # Constraints set (38):
        # y_ij = 1 if, and only if, vertex j is successor of i in the tour
        self.cstrPrecedence1 = self.model.addConstrs(
           self.y[i, j] + self.x[j, i] + self.y[j, k] + self.y[k, i] <= 2
           for (i, j, k) in self.non_zero_i_j_k
        )

        # Constraints set (45):
        # RLT constraints set 1
        self.cstrRLT1 = self.model.addConstrs(
            self.t[i, j, k] <= self.x[i, k] for (i, j, k) in self.non_zero_i_j_k
        )

        del self.non_zero_i_j_k

        # Auxiliary set
        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i > 0 and j > 0)
        ]

        # Constraints set (37):
        # Given two distinct vertices i and j, then j must be before or after i.
        self.cstrPrecedence2 = self.model.addConstrs(
           self.y[i, j] + self.y[j, i] == 1 for (i, j) in self.non_zero_i_j
        )
        
        # Constraints set (41):
        # If i is the first vertex on the tour after the origin, then i precedes all vertices j different of 0 and i
        self.cstrYAtRouteStart = self.model.addConstrs(
           self.y[i, j] >= self.x[0, i] for (i, j) in self.non_zero_i_j
        )

        # Constraints set (42):
        # If i is the last vertex on the tour after the origin, then i succeeds all vertices j different of 0 and i
        self.cstrYAtRouteEnd = self.model.addConstrs(
           self.y[j, i] >= self.x[i, 0] for (i, j) in self.non_zero_i_j
        )

        # Constraints set (46):
        # RLT constraints set 2
        self.cstrRLT2 = self.model.addConstrs(
            gp.quicksum(self.t[i, j, k] for k in self.V if k > 0 if k != i if k != j) + self.x[i, j] == self.y[i, j] 
            for (i, j) in self.non_zero_i_j
        )

        # Constraints set (47):
        # RLT constraints set 3
        self.cstrRLT3 = self.model.addConstrs(
            self.x[0, k] + gp.quicksum(self.t[i, j, k] for i in self.V if i > 0 if i != j if i != k) == self.y[k, j]
            for (k, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        # Constraints set (30):
        # The d-relaxed priority rule constraint formulated using the precedence variables.
        self.cstrPrecedenceDRelax = self.model.addConstrs(
            self.y[i, j] == 1 for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A if q > p + self.d
        )
