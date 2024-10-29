import math


DATETIME_FORMAT_FOR_KEYS = '%f%y%m%d%M%H%S'
MIN_QUES_QTY = 15
MAX_QUES_QTY = 50
MIN_QUES_TIME = 10 # minutes
TEST_MIN_CUT = 5
COMP_QUES_QTY = 5
COMP_INCLUSION_PERC = 1/3
DEFAULT_QUES_QTY_OPTIONS = [qty for qty in range(
    MIN_QUES_QTY, MAX_QUES_QTY, math.gcd(MIN_QUES_QTY, MAX_QUES_QTY))]
QUICK_TEST_SYLLABUS = ['Preposition']

comp_meta_qty = lambda qty: math.floor((qty * COMP_INCLUSION_PERC) / COMP_QUES_QTY)  
