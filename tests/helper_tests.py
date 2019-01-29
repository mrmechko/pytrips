from pytrips.helpers import Normalize

def test_nmlz_ont():
    assert Normalize.ont_name("test") == "ont::test"
    assert Normalize.ont_name("ont::test") == "ont::test"
