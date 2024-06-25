from datetime import date, timedelta
from random import uniform, randint
from statistics import mean
import sqlite3


def generate_remaining(count: int, min: float, max: float, busy_days: list, 
                       busy_day_modifier: float, rounding_point: int,) -> list:
    """
    Generates a list of values for "remaining". Can generate lower values for specific
    days of the week to simulate "busy days".
    """
    result = []
    day_of_week = 1

    result.append(0)

    for num in range(count - 1):
        num_to_add = uniform(min, max)

        # Modify number to represent busy days
        if day_of_week in busy_days:
            num_to_add -= busy_day_modifier
            if num_to_add < 0:
                num_to_add == 0

        result.append(round(num_to_add, rounding_point))

        # Advance day of week count
        if day_of_week != 7:
            day_of_week +=1
        else:
            day_of_week = 1

    return result


def generate_dates_list(count: int, start_date: date) -> list:
    """
    Generates a list of dates ending before the given date.
    """
    result = []

    for n in range(count):
        date = start_date - timedelta(days=count - n)
        result.append(date)
    
    return result


def generate_discarded(count: int, percent_chance: int, min: float, max: float, rounding_point: int) -> list:
    result = []

    result.append(0)

    for n in range(count - 1):
        num = 0.0
        if randint(1, 100) < percent_chance:
            result.append(round(uniform(min, max), rounding_point))
        else:
            result.append(0)

    return result


def generate_prod_data(count: int, id: int, date: date, initial_production: int,
                       remaining_min: float, remaining_max: float,
                       discarded_min: float, discarded_max: float,
                       busy_days: list, busy_day_modifier: int, 
                       discard_chance: int, rounding_point: int) -> list:
    result = []

    # Generate data for date, remaining and discarded
    dates = generate_dates_list(count, date)
    remaining = generate_remaining(count, remaining_min, remaining_max, busy_days, busy_day_modifier, rounding_point)
    discarded = generate_discarded(count, discard_chance, discarded_min, discarded_max, rounding_point)
    produced = []

    # Add the initial production number
    produced.append(initial_production)

    # Calculate and fill production numbers
    for n in range(count):
        # Skip the zero index
        if n != 0:
            average = calculate_usage(remaining[0:n], discarded[0:n], produced[0:n])
            prod_number = calculate_production(remaining[n], average, 1, rounding_point)
            produced.append(prod_number)

    # Generate list of tuple data
    for n in range(count):
        data = (id, dates[n], remaining[n], discarded[n], produced[n])
        result.append(data)

    return result


def calculate_usage(remaining: list, discarded: list,
                    produced: list, rounding_point: int = 1) -> float:
    """
    Calculates the average usage for a given product, rounded to a specific decimal point
    """
    usage = (mean(remaining) + mean(produced)) - mean(discarded)

    return round(usage, rounding_point)


def calculate_production(remaining: float, average: float, 
                         safety_margin: float = 1, rounding_point: int = 1) -> float:
    """
    Calculates the sugested production numbers for the day, based on a safety margin
    and rounded to a specific decimal point
    """
    produce = (average - remaining) * safety_margin
    if produce < 0:
        produce = 0

    return round(produce, rounding_point)


def insert_production_data(conn_string: str, production_data: tuple) -> None:
    """
    Add ne production data for a certain product to the database
    """
    try:
        with sqlite3.connect(conn_string) as conn:
            result = conn.cursor().execute("""
                INSERT INTO ProductionData 
                (ProductID, Date, Remaining, Discarded, Produced)
                VALUES (?, ?, ?, ?, ?)
            """, production_data)
    except sqlite3.OperationalError as error:
        raise Exception(error)


def main():
    data = generate_prod_data(30, 10, date.today(), 2,
                              1, 1.5, 0.5, 1.2, [4,5,6],
                              0.5, 30, 1)
    
    for n in data:
        insert_production_data("test_database.db", n)


if __name__ == "__main__":
    main()