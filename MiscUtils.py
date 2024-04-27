from BasicModels import MTZ_CTSP_d_Model, GP_CTSP_d_Model, SSB_CTSP_d_Model, SST_CTSP_d_Model
from ValidInequalitiesBaseClass import VI_MTZ_CTSP_d_Model, VI_GP_CTSP_d_Model, VI_SSB_CTSP_d_Model, VI_SST_CTSP_d_Model, VI_Ha_CTSP_d_Model

AVAILABLE_MODELS_LIST = [
    MTZ_CTSP_d_Model, GP_CTSP_d_Model, SSB_CTSP_d_Model, SST_CTSP_d_Model,
    VI_MTZ_CTSP_d_Model, VI_GP_CTSP_d_Model, VI_SSB_CTSP_d_Model, VI_SST_CTSP_d_Model,
    VI_Ha_CTSP_d_Model
]

def create_solvers_aliases_dict():
    return {
        model.alias: model
        for model in AVAILABLE_MODELS_LIST
    }
