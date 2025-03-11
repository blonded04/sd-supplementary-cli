import pytest

def upper(x : str):
    return x.upper()

def test_capital_case():
    assert upper('semaphore') == 'SEMAPHORE'

def test_raises_exception_on_non_string_arguments():
    with pytest.raises(TypeError):
        test_capital_case(9)
