from . import openrlib


def getrank(cdata):
    dim_cdata = openrlib.rlib.Rf_getAttrib(cdata,
                                           openrlib.rlib.R_DimSymbol)
    if dim_cdata == openrlib.rlib.R_NilValue:
        return 1
    else:
        return openrlib.rlib.Rf_length(dim_cdata)


def getshape(cdata, rk=None):
    if rk is None:
        rk = getrank(cdata)
    dim_cdata = openrlib.rlib.Rf_getAttrib(cdata,
                                           openrlib.rlib.R_DimSymbol)
    shape = [None, ] * rk
    if dim_cdata == openrlib.rlib.R_NilValue:
        shape[0] = openrlib.rlib.Rf_length(cdata)
    else:
        for i in range(rk):
            shape[i] = openrlib.rlib.INTEGER_ELT(dim_cdata, i)
    return shape


def getstrides(cdata, shape, itemsize):
    rk = len(shape)
    strides = [None, ] * rk
    strides[0] = itemsize
    for i in range(1, rk):
        strides[i] = shape[i-1] * strides[i-1]
    return strides


def getbuffer(cdata):
    raise NotImplementedError()
