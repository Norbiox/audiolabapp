import json
from datetime import datetime, timedelta

import flask
import pytest

from app.models import db, Record, Recorder, Series
from app.tests.factory import models