import pytest
from datetime import datetime

from app.helpers import (encode_recorder_key, increase_last_digit,
                         parse_filtering_dates)


def test_parsing_dates_to_filtering():
    created_from = '2018-04-21'
    created_to = '2018-11-09'

    # only created_from
    parsed = parse_filtering_dates(created_from)
    assert parsed[0] == datetime(2018, 4, 21, 0, 0)
    assert parsed[1] is None

    # only created_to
    parsed = parse_filtering_dates(None, created_to)
    assert parsed[0] is None
    assert parsed[1] == datetime(2018, 11, 9, 23, 59, 59)

    # both dates
    parsed = parse_filtering_dates(created_from, created_to)
    assert parsed[0] == datetime(2018, 4, 21, 0, 0)
    assert parsed[1] == datetime(2018, 11, 9, 23, 59, 59)


@pytest.mark.parametrize('number,result', [
    (10, 11),
    (13.7, 13.8),
    (1.0001, 1.0002),
    (2e-2, 0.03),
    (7.0, 8.0)
])
def test_increasing_last_digits_of_number(number, result):
    assert increase_last_digit(number) == result


def test_encoding_recorder_key():
    key = encode_recorder_key('recorder123')
    assert isinstance(key, bytes)
