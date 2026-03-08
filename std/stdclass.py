from myast import *
from tokens import *
from type import *
def make_std_class():

    Functionmember = []

    Call = Symbol("call", Functionmember=Functionmember)
    Call.Functionmember.append(Call)

    clsdata: dict[(Type), Symbol] = {
        TypeFunction: Symbol("function", Functionmember=[Call, *Functionmember])
    }
    return clsdata
