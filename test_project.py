from project import (
    calculate_usage, 
    calculate_production,
    adjust_for_packaging,
    insert_product
)

def test_calclulate_usage():
    test_remaining = [3.3, 5.2, 2, 3.2, 4, 1.5] # sum: 19,2 | mean: 3.2
    test_produced = [2, 3, 0.5, 2, 1, 3] # sum: 11,5 | mean: 1.916666666
    test_discarded = [0.5, 1, 0, 0.2, 0, 1] # sum: 2.7 | mean: 0.45
    # usage calculated at 4.6666666

    # calculation testing, rounded to default (1st) decimal point
    assert calculate_usage(test_remaining, test_produced, test_discarded) == 4.7
    # calculation testing, rounded to specific decimal point
    assert calculate_usage(test_remaining, test_produced, test_discarded, rounding_point=2) == 4.67
    assert calculate_usage(test_remaining, test_produced, test_discarded, rounding_point=4) == 4.6667


def test_calculate_production():
    # calculations testing
    assert calculate_production(3, 5,) == 2
    assert calculate_production(3, 5, 1.5) == 3
    # negative value returns zero
    assert calculate_production(7, 2, 2) == 0
    # decimal point testing
    assert calculate_production(3.4, 5.7, 1.5) == 3.5
    assert calculate_production(3.4, 5.7, 1.5, 2) == 3.45


def test_adjust_for_packaging():
    # 7 portions needed, packaging contains 5 portions, must use whole packaging
    assert adjust_for_packaging(7, False, 5) == 10
    # 4.5 portions needed, packaging contains 7 portions, can be portioned partially 
    assert adjust_for_packaging(4.5, True, 7) == 4.5 

