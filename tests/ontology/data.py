from setup import OntTypeData
import pytest

tests = [
    OntTypeData(name="bread",
                parent="baked-goods",
                ancestors=["baked-goods", "food", "phys-object"]),
    OntTypeData(name="nonhuman-animal",
                parent="mammal",
                ancestors=["animal", "phys-object"])
]

@pytest.fixture(params=tests)
def TestType(request):
    return request.param
