import pytest
import rpy2.robjects as robjects
ri = robjects.rinterface
import array
import time
import datetime
import rpy2.rlike.container as rlc
from collections import OrderedDict

rlist = robjects.baseenv["list"]


def test_init():
    identical = ri.baseenv["identical"]
    py_a = array.array('i', [1,2,3])
    ro_v = robjects.IntVector(py_a)
    assert ro_v.typeof == ri.RTYPES.INTSXP

    ri_v = ri.IntSexpVector(py_a)
    ro_v = robjects.IntVector(ri_v)

    assert identical(ro_v, ri_v)[0]

    del(ri_v)
    assert ro_v.typeof == ri.RTYPES.INTSXP

    
def test_init_strvector():
    vec = robjects.StrVector(['abc', 'def'])
    assert 'abc' == vec[0]
    assert 'def' == vec[1]
    assert len(vec) == 2


def test_init_intvector():
    vec = robjects.IntVector([123, 456])
    assert 123 == vec[0]
    assert 456 == vec[1]
    assert len(vec) == 2


def test_init_floatvector():
    vec = robjects.FloatVector([123.0, 456.0])
    assert 123.0 == vec[0]
    assert 456.0 == vec[1]
    assert len(vec) == 2


def test_init_boolvector():
    vec = robjects.BoolVector([True, False])
    assert vec[0] is True
    assert vec[1] is False
    assert len(vec) == 2


listvector_testdata = (
    robjects.ListVector({'a': 1, 'b': 2}),
    robjects.ListVector((('a', 1), ('b', 2))),
    robjects.ListVector(iter([('a', 1), ('b', 2)]))
    )


@pytest.mark.parametrize('vec', listvector_testdata)
def test_new_listvector(vec):
    assert 'a' in vec.names
    assert 'b' in vec.names
    assert len(vec) == 2
    assert len(vec.names) == 2


def test_add_operator():
    seq_R = robjects.r["seq"]
    mySeqA = seq_R(0, 3)
    mySeqB = seq_R(5, 7)
    mySeqAdd = mySeqA + mySeqB

    assert len(mySeqA)+len(mySeqB) == len(mySeqAdd)

    for i, li in enumerate(mySeqA):
        assert mySeqAdd[i] == li
    for j, li in enumerate(mySeqB):
        assert mySeqAdd[i+j+1] == li


def test_r_add_aperator():
    seq_R = robjects.r["seq"]
    mySeq = seq_R(0, 10)
    mySeqAdd = mySeq.ro + 2
    for i, li in enumerate(mySeq):
        assert li + 2 == mySeqAdd[i]


def test_r_mult_operator():
    seq_R = robjects.r["seq"]
    mySeq = seq_R(0, 10)
    mySeqAdd = mySeq.ro + mySeq
    for i, li in enumerate(mySeq):
        assert li * 2 == mySeqAdd[i]


def test_r_power_operator():
    seq_R = robjects.r["seq"]
    mySeq = seq_R(0, 10)
    mySeqPow = mySeq.ro ** 2
    for i, li in enumerate(mySeq):
        assert li ** 2 == mySeqPow[i]


def test_getitem():
    letters = robjects.baseenv["letters"]
    assert letters[0] == 'a'
    assert letters[25] == 'z'


def test_getitem_outofbounds():
    letters = robjects.baseenv["letters"]
    with pytest.raises(IndexError):
        letters[26]


def test_setitem():
    vec = robjects.r.seq(1, 10)
    assert vec[0] == 1
    vec[0] = 20
    assert vec[0] == 20


def test_setitem_outofbounds():
    vec = robjects.r.seq(1, 10)
    with pytest.raises(IndexError):
        vec[20] = 20


def get_item_list():
    mylist = rlist(letters, "foo")
    idem = robjects.baseenv["identical"]
    assert idem(letters, mylist[0])[0] is True
    assert idem("foo", mylist[1])[0] is True


def test_getnames():
    vec = robjects.vectors.IntVector(array.array('i', [1,2,3]))
    v_names = [robjects.baseenv["letters"][x] for x in (0,1,2)]
    #FIXME: simplify this
    r_names = robjects.baseenv["c"](*v_names)
    vec = robjects.baseenv["names<-"](vec, r_names)
    for i in range(len(vec)):
        assert v_names[i] == vec.names[i]
    vec.names[0] = 'x'


def test_setnames():
    vec = robjects.vectors.IntVector(array.array('i', [1,2,3]))
    names = ['x', 'y', 'z']
    vec.names = names
    for i in range(len(vec)):
        assert names[i] == vec.names[i]


def test_nainteger():
    vec = robjects.IntVector(range(3))
    vec[0] = robjects.NA_Integer
    assert robjects.baseenv['is.na'](vec)[0] is True


def test_nareal():
    vec = robjects.FloatVector((1.0, 2.0, 3.0))
    vec[0] = robjects.NA_Real
    assert robjects.baseenv['is.na'](vec)[0] is True


def test_nalogical():
    vec = robjects.BoolVector((True, False, True))
    vec[0] = robjects.NA_Logical
    assert robjects.baseenv['is.na'](vec)[0] is True


def test_nacomplex():
    vec = robjects.ComplexVector((1+1j, 2+2j, 3+3j))
    vec[0] = robjects.NA_Complex
    assert robjects.baseenv['is.na'](vec)[0] is True


def test_nacharacter():
    vec = robjects.StrVector('abc')
    vec[0] = robjects.NA_Character
    assert robjects.baseenv['is.na'](vec)[0] is True


def test_repr():
    vec = robjects.IntVector((1,2,3))
    s = repr(vec)
    assert s.endswith('[1, 2, 3]')


def test_repr_nonvectorinlist():
    vec = robjects.ListVector(OrderedDict((('a', 1), 
                                           ('b', robjects.Formula('y ~ x')),
                                           )))
    s = repr(vec)
    assert s.startswith("R object with classes: (\'RTYPES.VECSXP',) "
                        "mapped to:\n[IntVector, Formula]")


def test_items():
    vec = robjects.IntVector(range(3))
    vec.names = robjects.StrVector('abc')
    names = [k for k,v in vec.items()]
    assert names == ['a', 'b', 'c']
    values = [v for k,v in vec.items()]
    assert values == [0, 1, 2]


def test_itemsnonames():
    vec = robjects.IntVector(range(3))
    names = [k for k,v in vec.items()]
    assert names == [None, None, None]
    values = [v for k,v in vec.items()]
    assert values == [0, 1, 2]


def test_sequence_to_vector():
    res = robjects.sequence_to_vector((1,2,3))
    assert isinstance(res, robjects.IntVector)

    res = robjects.sequence_to_vector((1,2,3.0))
    assert isinstance(res, robjects.FloatVector)

    res = robjects.sequence_to_vector((1,2,'a'))
    assert isinstance(res, robjects.StrVector)

    with pytest.raises(ValueError):
        robjects.sequence_to_vector(list())

