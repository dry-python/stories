import pytest

import helpers


@helpers.is_not_empty
def runners():
    yield "function"
    yield "coroutine"


# Fixtures.


@pytest.fixture(params=runners())
def r(request):
    import examples.runners

    return examples.runners.runners[request.param]


@pytest.fixture()
def c(r):
    return r.import_module("examples.context")


@pytest.fixture()
def f(r):
    return r.import_module("examples.failure_reasons")


@pytest.fixture()
def x(r):
    return r.import_module("examples.methods")


@pytest.fixture()
def m(r):
    return r.import_module("examples.contract")
