import jwt
from datetime import datetime
from dateutil.parser import parse

from flask import abort, current_app
from sqlalchemy.orm import exc

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
ISO_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def datetime_to_string(dt, date_format=False):
    if not date_format:
        return dt.strftime(DATETIME_FORMAT)
    return dt.strftime(DATE_FORMAT)


def encode_recorder_key(recorder_uid):
    payload = {'uid': recorder_uid}
    key = jwt.encode(payload, current_app.config['SECRET_KEY'],
                     algorithm='HS256')
    return key.decode("utf-8")


def get_object(model, key):
    """Looks for model object with uid equal to given key. Returns this
    object or raises NoResultFound.
    """
    try:
        object = model.query.filter(model.uid == key).one()
        return object
    except exc.NoResultFound:
        raise exc.NoResultFound("Member of {} with uid {} not found.".format(
                                str(model), key))


def get_object_or_404(model, key):
    """Looks for model object with uid equal to given key. Returns this
    object or raises 404 if not found.
    """
    try:
        object = model.query.filter(model.uid == key).one()
        return object
    except exc.NoResultFound:
        abort(404, "Member of {} with uid {} not found.".format(
              str(model), key))
    except exc.MultipleResultsFound:
        abort(404, "Many results for class {} with uid {} has been found.".
              format(str(model), key))


def increase_last_digit(number):
    is_floated_integer = int(number) == number
    string = str(int(number) if is_floated_integer else number)
    string = string[:-1] + str(int(string[-1]) + 1)
    if '.' in string or is_floated_integer:
        return float(string)
    return int(string)


def parse_filtering_dates(created_from=None, created_to=None):
    try:
        if created_from:
            created_from = parse(created_from)
        if created_to:
            created_to = parse(created_to)
            if not any([created_to.hour,
                        created_to.minute,
                        created_to.second]):
                created_to = created_to.replace(hour=23, minute=59, second=59)
        if created_from and created_to:
            if created_to <= created_from:
                raise ValueError(
                    "Date 'created_to' must be greater than 'created_from'"
                )
    except ValueError:
        raise ValueError('Invalid datetime format')
    return created_from, created_to


def string_to_datetime(date_string):
    for f in [DATE_FORMAT, DATETIME_FORMAT, ISO_DATETIME_FORMAT]:
        try:
            return datetime.strptime(date_string, f)
        except ValueError:
            pass
    raise ValueError('Invalid datetime format')
