import gurobipy as gp
from BasicModels import CTSP_d_BaseModel

class VI_BaseModel(CTSP_d_BaseModel):
    """Class to add common valid inequalities to the models H2020, MTZ2, GP2, SSB2 and SST2."""
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        # Constraints set (10):
        # The first vertex after the origin can have at most priority d.
        self.cstrGeneralVI1 = self.model.addConstrs(
            gp.quicksum(self.x[0, i] for i in self.V_P[p] if (0, i) in self.A) == 0
            for p in range(self.P) if p > self.d
        )

        # Constraints set (11):
        # The last vertex before the origin must have at least priority P_max - d - 1
        self.cstrGeneralVI2 = self.model.addConstrs(
            gp.quicksum(self.x[i, 0] for i in self.V_P[p] if (i, 0) in self.A) == 0
            for p in range(self.P) if p < self.P - 1 - self.d
        )

        # Constraints set (12):
        # When a vertex in a priority set V_p is left, the next vertex visited can belong
        # to a V_q set satisfying q > p + d, but it can occur at most once.
        self.cstrGeneralVI3 = self.model.addConstrs(
            gp.quicksum(self.x[i, j] for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A) <= 1
            for p in range(self.P) for q in range(self.P) if q > p + self.d
        )

class VI_MTZ_CTSP_d_Model(VI_BaseModel):
    """Class to instantiate the MTZ2 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (MTZ2).
    """
    
    alias = "MTZ2"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        # Variables set:
        # Creating the u variables.
        self.u = self.model.addVars(self.V, ub = self.n - 1)

        # Constraints set (9):
        # Given two priority levels p and q, if q > p + d, then we must have x_ji = 0
        self.cstrGeneralVI4 = self.model.addConstrs(
            gp.quicksum(self.x[j, i] for i in self.V_P[p] for j in self.V_P[q] if (j, i) in self.A) == 0
            for p in range(self.P) for q in range(self.P) if q > p + self.d
        )

        # Constraints set (25):
        # Lifted d-relaxed priority rule constraint
        self.cstrLiftedMTZdRelax = self.model.addConstrs(
            self.u[i] + 2 - self.x[i, j] <= self.u[j] for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if q > p + self.d
        )

        # Constraints set (14):
        # Minimum value each variable u_j must satisfy
        self.cstrMinUVar = self.model.addConstrs(
            self.u[j] >= sum(len(self.V_P[r]) for r in range(p - self.d)) + 1
            for p in range(self.d + 1, self.P) for j in self.V_P[p]
        )

        # Constraints set (15):
        # Maximum value each variable u_j may assume
        self.cstrMaxUVar = self.model.addConstrs(
            self.u[j] <= sum(len(self.V_P[r]) for r in range(p + self.d + 1))
            for p in range(self.P - self.d - 1) for j in self.V_P[p]
        )

        # M values (17):
        # Used to define the adjusted MTZ constraints
        self.MTZ_M = {
            (i, j): sum(len(self.V_P[r]) for r in range(max(0, p - self.d), min(self.P, q + self.d + 1))) - 1
                for p in range(self.P) for q in range(p, self.P) 
                for i in self.V_P[p]   for j in self.V_P[q]
        }

        self.MTZ_M.update({
            (j, i): self.MTZ_M[i, j] for (i, j) in list(self.MTZ_M.keys())
        })

        # Constraints set (16):
        # Lifted MTZ subtour removal constraint as in Desrochers and Laporte (1991),
        # with M adjusted for the CTSP-d
        self.cstrLiftedMTZ = self.model.addConstrs(
            self.u[i] - self.u[j] + (self.MTZ_M[i,j]+1) * self.x[i, j] + 
            (self.MTZ_M[i,j]-1) * self.x[j, i] <= self.MTZ_M[i,j]
            for (i, j) in self.A if (i*j) != 0
        )

        # Constraints set (21):
        # If i is the first vertex after the origin, then u_i <= 1
        self.cstrFirstVertexDL = self.model.addConstrs(
            self.u[i] <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        # Constraints set (22):
        # If i is the last vertex before the origin, then u_i >= n - 1
        self.cstrLastVertexDL = self.model.addConstrs(
            self.u[i] >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        # Constraints set (23):
        # For all vertices i in V such that i !=0, we will have u_i >= 1
        self.cstrIntermediateVerticesDL = self.model.addConstrs(
            self.u[i] >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )

        # Constraints set (24):
        # Imposing that u[0] == 0
        self.cstrUZero = self.model.addConstr(
            self.u[0] == 0
        )

        # Constraints set (27):
        # Since u_0, ..., n_{n-1} will describe a permutation of 0, ..., n-1, then
        # the sum of the variables will satisfy
        self.cstrSumUVars = self.model.addConstr(
            gp.quicksum(self.u[j] for j in self.V) == int(self.n * (self.n - 1) / 2)
        )

        # Constraints set (28):
        # Each arc on the graph can only be traversed in one direction
        self.cstrTwoVerticesClique = self.model.addConstrs(
            self.x[i, j] + self.x[j, i] <= 1 for (i, j) in self.A
        )

class VI_GP_CTSP_d_Model(VI_BaseModel):
    """Class to instantiate the GP2 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (GP2).
    """
    
    alias = "GP2"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        # Variables set:
        # Creating the y variables.
        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)

        # Auxiliary set
        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i * j) > 0
        ]

        # Constraints set (31):
        # If j is the successor of i in the tour, then i precedes j in the tour.
        # If i does not precede j in the tour, then j cannot be the successor of i.
        self.cstrPrecedence1 = self.model.addConstrs(
            self.x[i, j] - self.y[i, j] <= 0 for (i, j) in self.non_zero_i_j
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

        # Constraints set (39):
        # No vertex j can be successor and predecessor of the origin at the same time.
        self.cstrPrecedence5 = self.model.addConstrs(
            self.x[0, j] + self.x[j, 0] <= 1 for j in self.V if j > 0
        )

        # Constraints set (30):
        # The d-relaxed priority rule constraint formulated using the precedence variables.
        self.cstrPrecedenceDRelax = self.model.addConstrs(
            self.y[i, j] == 1 for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A if q > p + self.d
        )

        # Constraints set (48):
        # Used to guarantee the relationship in (50)
        self.cstrYValueReturningToOrigin = self.model.addConstrs(
            self.y[i, 0] == 0 for i in self.V if i != 0
        )

        # Constraints set (49):
        # Used to guarantee the relationship in (50)
        self.cstrYValueLeavingOrigin = self.model.addConstrs(
            self.y[0, j] == 1 for j in self.V if j != 0
        )

        # Constraints set (53):
        # Obtained combining constraints (21) and (50)
        self.cstrFirstVertexDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        # Constraints set (54):
        # Obtained combining constraints (22) and (50)
        self.cstrLastVertexDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        # Constraints set (55):
        # Obtained combining constraints (23) and (50)
        self.cstrIntermediateVerticesDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )

        # Constraints set (57):
        # Obtained combining constraints (27) and (50)
        self.cstrSumYVars = self.model.addConstr(
            gp.quicksum(self.y[i, j] for (i, j) in self.A) == int((self.n) * (self.n-1) / 2)
        )

class VI_SSB_CTSP_d_Model(VI_BaseModel):
    """Class to instantiate the SSB2 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (SSB2).
    """
    
    alias = "SSB2"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        # Variables set:
        # Creating the y variables.
        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
        
        # Auxiliary set
        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i * j) > 0
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
        # y_ij = 1 if, and only if, vertex j is successor of i in the tour
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

        # Constraints set (48):
        # Used to guarantee the relationship in (50)
        self.cstrYValueReturningToOrigin = self.model.addConstrs(
            self.y[i, 0] == 0 for i in self.V if i != 0
        )

        # Constraints set (49):
        # Used to guarantee the relationship in (50)
        self.cstrYValueLeavingOrigin = self.model.addConstrs(
            self.y[0, j] == 1 for j in self.V if j != 0
        )

        # Constraints set (53):
        # Obtained combining constraints (21) and (50)
        self.cstrFirstVertexDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        # Constraints set (54):
        # Obtained combining constraints (22) and (50)
        self.cstrLastVertexDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        # Constraints set (55):
        # Obtained combining constraints (23) and (50)
        self.cstrIntermediateVerticesDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )

        # Constraints set (57):
        # Obtained combining constraints (27) and (50)
        self.cstrSumYVars = self.model.addConstr(
            gp.quicksum(self.y[i, j] for (i, j) in self.A) == int((self.n) * (self.n-1) / 2)
        )

class VI_SST_CTSP_d_Model(VI_BaseModel):
    """Class to instantiate the SST2 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (SST2).
    """
    
    alias = "SST2"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)


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

        # Constraints set (48):
        # Used to guarantee the relationship in (50)
        self.cstrYValueReturningToOrigin = self.model.addConstrs(
            self.y[i, 0] == 0 for i in self.V if i != 0
        )

        # Constraints set (49):
        # Used to guarantee the relationship in (50)
        self.cstrYValueLeavingOrigin = self.model.addConstrs(
            self.y[0, j] == 1 for j in self.V if j != 0
        )

        # Constraints set (53):
        # Obtained combining constraints (21) and (50)
        self.cstrFirstVertexDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        # Constraints set (54):
        # Obtained combining constraints (22) and (50)
        self.cstrLastVertexDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        # Constraints set (55):
        # Obtained combining constraints (23) and (50)
        self.cstrIntermediateVerticesDL = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )
        # Constraints set (57):
        # Obtained combining constraints (27) and (50)
        self.cstrSumYVars = self.model.addConstr(
            gp.quicksum(self.y[i, j] for (i, j) in self.A) == int((self.n) * (self.n-1) / 2)
        )

class VI_Ha_CTSP_d_Model(VI_BaseModel):
    """Class to instantiate the H2020 model.
    
    Attributes
    ----------
    alias : str
        Global class attribute storing the model alias (H2020).
    """
    
    alias = "H2020"
    
    def __init__(self, data: dict, relax: bool=False, memLimit: int=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        # Variables set:
        # Creating the u variables.
        self.u = self.model.addVars(self.V, ub = self.n - 1)

        # Constraints set (9):
        # Given two priority levels p and q, if q > p + d, then we must have x_ji = 0
        self.cstrGeneralVI4 = self.model.addConstrs(
            gp.quicksum(self.x[j, i] for i in self.V_P[p] for j in self.V_P[q] if (j, i) in self.A) == 0
            for p in range(self.P) for q in range(self.P) if q > p + self.d
        )

        # Constraints set (8):
        # The d-relaxed priority rule constraint, as proposed by Hà et. al. (2020)
        self.cstrMTZdRelax = self.model.addConstrs(
            self.u[i] + 1 <= self.u[j] for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if q > p + self.d
        )

        self.MTZ_M = self.n - 1

        # Constraints set (7):
        # The classical MTZ subtour removal constraint.
        # Impose the u variables meaning - the position of the vertices in a feasible solution
        self.cstrMTZ = self.model.addConstrs(
           self.u[i] - self.u[j] + self.n * self.x[i, j] <= self.n - 1
           for (i, j) in self.A if j != 0
        )
