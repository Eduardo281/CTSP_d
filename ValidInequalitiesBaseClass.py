import gurobipy as gp
from BasicModels import CTSP_d_BaseModel

class VI_BaseModel(CTSP_d_BaseModel):
    """Class to add common valid inequalities to the proposed models."""
    def __init__(self, data, relax=False, memLimit=None):
        CTSP_d_BaseModel.__init__(self, data, relax, memLimit)

        # Ha et. al. 2020 valid inequalities:
        self.c_Ha_16 = self.model.addConstrs(
            gp.quicksum(self.x[0, i] for i in self.V_P[p] if (0, i) in self.A) == 0
            for p in range(self.P) if p > self.d
        )

        self.c_Ha_17 = self.model.addConstrs(
            gp.quicksum(self.x[i, 0] for i in self.V_P[p] if (i, 0) in self.A) == 0
            for p in range(self.P) if p < self.P - 1 - self.d
        )

        self.c_Ha_18 = self.model.addConstrs(
            gp.quicksum(self.x[i, j] for i in self.V_P[p] for j in self.V_P[q] if (i, j) in self.A) <= 1
            for p in range(self.P) for q in range(self.P) if q > p + self.d
        )

class VI_MTZ_CTSP_d_Model(VI_BaseModel):
    """Class to add valid inequalities to the MTZ model."""
    def __init__(self, data, relax=False, memLimit=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        self.alias = "MTZ2"

        if(relax):
            self.u = self.model.addVars(self.V, ub = self.n - 1)
        else:
            #self.u = self.model.addVars(self.V, vtype = gp.GRB.INTEGER, ub = self.n - 1)
            self.u = self.model.addVars(self.V, ub = self.n - 1)

        # Valid inequalities presented in Ha et. al. (2020):
        self.c_Ha_15 = self.model.addConstrs(
            gp.quicksum(self.x[j, i] for i in self.V_P[p] for j in self.V_P[q] if (j, i) in self.A) == 0
            for p in range(self.P) for q in range(self.P) if q > p + self.d
        )

        self.c_d_relax = self.model.addConstrs(
            self.u[i] + 2 - self.x[i, j] <= self.u[j] for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if q > p + self.d
        )

        self.c_min_u_d_relax = self.model.addConstrs(
            self.u[j] >= sum(len(self.V_P[r]) for r in range(p - self.d)) + 1
            for p in range(self.d + 1, self.P) for j in self.V_P[p]
        )

        self.c_max_u_d_relax = self.model.addConstrs(
            self.u[j] <= sum(len(self.V_P[r]) for r in range(p + self.d + 1))
            for p in range(self.P - self.d - 1) for j in self.V_P[p]
        )

        self.MTZ_M = {(i, j):  sum(len(self.V_P[r]) for r in range(max(0, p - self.d), min(self.P, q + self.d + 1)))-1
        for p in range(self.P) for q in range(p, self.P) for i in self.V_P[p] for j in self.V_P[q]}

        self.MTZ_M.update({
            (j, i): self.MTZ_M[i, j] for (i, j) in list(self.MTZ_M.keys())
        })

        self.c_d_relax_lifted_MTZ = self.model.addConstrs(
            self.u[i] - self.u[j] + (self.MTZ_M[i,j]+1) * self.x[i, j] + 
            (self.MTZ_M[i,j]-1) * self.x[j, i] <= self.MTZ_M[i,j]
            for (i, j) in self.A if (i*j) != 0
        )

        self.c_DL_3 = self.model.addConstrs(
            self.u[i] <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        self.u_final = self.model.addConstrs(
            self.u[i] >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        self.c_DL_2_VI = self.model.addConstrs(
            self.u[i] >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )

        self.c_zero_u = self.model.addConstr(
            self.u[0] == 0
        )

        self.c_sum_u = self.model.addConstr(
            gp.quicksum(self.u[j] for j in self.V) == int(self.n * (self.n - 1) / 2)
        )

        # Simple TSP inequalities set
        self.c_xij_xji = self.model.addConstrs(
            self.x[i, j] + self.x[j, i] <= 1 for (i, j) in self.A
        )

class VI_GP_CTSP_d_Model(VI_BaseModel):
    """Class to add valid inequalities to the GP model."""
    def __init__(self, data, relax=False, memLimit=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        self.alias = "GP2"

        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
        
        self.non_zero_i_j = [
            (i, j) for (i, j) in self.A if (i * j) > 0
        ]

        self.c_prec_1 = self.model.addConstrs(
            self.x[i, j] - self.y[i, j] <= 0 for (i, j) in self.non_zero_i_j
        )

        self.c_yij_yji = self.model.addConstrs(
            self.y[i, j] + self.y[j, i] == 1 for (i, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) if (i * j * k) > 0
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

        self.c_y_zero_final = self.model.addConstrs(
            self.y[i, 0] == 0 for i in self.V if i != 0
        )

        self.c_y_um_orig = self.model.addConstrs(
            self.y[0, j] == 1 for j in self.V if j != 0
        )

        self.c_DL_3 = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        self.u_final = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        self.c_DL_2_VI = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )

        self.c_sum_y = self.model.addConstr(
            gp.quicksum(self.y[i, j] for (i, j) in self.A) == int((self.n) * (self.n-1) / 2)
        )

class VI_SSB_CTSP_d_Model(VI_BaseModel):
    """Class to add valid inequalities to the SSB model."""
    def __init__(self, data, relax=False, memLimit=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        self.alias = "SSB2"

        if(relax):
            self.y = self.model.addVars(self.A)
        else:
            self.y = self.model.addVars(self.A, vtype = gp.GRB.BINARY)
        
        self.non_zero_i_j = [(i, j) for (i, j) in self.A if (i * j) > 0]

        self.c_prec_1 = self.model.addConstrs(
            self.y[i, j] >= self.x[i, j] for (i, j) in self.non_zero_i_j
        )

        self.c_prec_2 = self.model.addConstrs(
            self.y[i, j] + self.y[j, i] == 1 for (i, j) in self.non_zero_i_j
        )

        del self.non_zero_i_j

        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) if (i * j * k) > 0
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

        self.c_y_zero_final = self.model.addConstrs(
            self.y[i, 0] == 0 for i in self.V if i != 0
        )

        self.c_y_um_orig = self.model.addConstrs(
            self.y[0, j] == 1 for j in self.V if j != 0
        )

        self.c_sum_y = self.model.addConstr(
            gp.quicksum(self.y[i, j] for (i, j) in self.A) == int((self.n) * (self.n-1) / 2)
        )

        self.c_DL_3 = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        self.u_final = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        self.c_DL_2_VI = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )

class VI_SST_CTSP_d_Model(VI_BaseModel):
    """Class to add valid inequalities to the SST model."""
    def __init__(self, data, relax=False, memLimit=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        self.alias = "SST2"

        self.non_zero_i_j_k = [
            (i, j, k) for i in self.V for j in self.V for k in self.V 
            if(i != j) if (i != k) if (j != k) if (i * j * k) > 0
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

        self.non_zero_i_j = [(i, j) for (i, j) in self.A if (i * j) > 0]

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

        self.c_y_zero_final = self.model.addConstrs(
            self.y[i, 0] == 0 for i in self.V if i != 0
        )

        self.c_y_um_orig = self.model.addConstrs(
            self.y[0, j] == 1 for j in self.V if j != 0
        )

        self.c_DL_3 = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) <= self.n - (self.n - 2) * self.x[0, i] - 
            gp.quicksum(self.x[i, j] for j in self.V if (i, j) in self.A if j != 0) 
            for i in self.V if (0, i) in self.A
        )

        self.u_final = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= (self.n - 2) * self.x[i, 0] + 
            gp.quicksum(self.x[j, i] for j in self.V if (j, i) in self.A if j!= 0) 
            for i in self.V if (i, 0) in self.A
        )

        self.c_DL_2_VI = self.model.addConstrs(
            gp.quicksum(self.y[k, i] for k in self.V if (k, i) in self.A) >= 1 + gp.quicksum(self.x[j, i] 
            for j in self.V if (j, i) in self.A if j != 0) 
            for p in range(self.d + 1) for i in self.V_P[p]
        )

        self.c_sum_y = self.model.addConstr(
            gp.quicksum(self.y[i, j] for (i, j) in self.A) == int((self.n) * (self.n-1) / 2)
        )

class VI_Ha_CTSP_d_Model(VI_BaseModel):
    """Class to add valid inequalities to the MTZ model."""
    def __init__(self, data, relax=False, memLimit=None):
        VI_BaseModel.__init__(self, data, relax, memLimit)

        self.alias = "H2020"

        if(relax):
            self.u = self.model.addVars(self.V, ub = self.n - 1)
        else:
            #self.u = self.model.addVars(self.V, vtype = gp.GRB.INTEGER, ub = self.n - 1)
            self.u = self.model.addVars(self.V, ub = self.n - 1)

        # Valid inequalities presented in Ha et. al. (2020):
        self.c_Ha_15 = self.model.addConstrs(
            gp.quicksum(self.x[j, i] for i in self.V_P[p] for j in self.V_P[q] if (j, i) in self.A) == 0
            for p in range(self.P) for q in range(self.P) if q > p + self.d
        )

        self.c_d_relax = self.model.addConstrs(
            self.u[i] + 1 <= self.u[j] for p in range(self.P) for q in range(self.P) 
            for i in self.V_P[p] for j in self.V_P[q] if q > p + self.d
        )

        self.MTZ_M = self.n - 1

        self.c_d_relax_lifted_MTZ = self.model.addConstrs(
            self.u[i] - self.u[j] + (self.MTZ_M+1) * self.x[i, j] <= self.MTZ_M
            for (i, j) in self.A if (i*j) != 0
        )

        self.c_zero_u = self.model.addConstr(
            self.u[0] == 0
        )
