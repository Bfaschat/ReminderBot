import re

def CheckForDateTimeText(input):
    """Check input text to match pattern via regular expressions"""
    pattern1 = r""" *[1-2][0-9]{3}\.[0-1][0-9]\.[0-3][0-9] *[0-2][0-9]:[0-5][0-9] .*"""
    pattern2 = r""" *[0-2][0-9]:[0-5][0-9] .*"""
    if re.match(pattern1, input, re.DOTALL) is not None:
        return 1
    if re.match(pattern2, input, re.DOTALL) is not None:
        return 2

    return 0

def CheckForDateTimeOrTime(input):
    """Check input text to match pattern via regular expressions. Done by Brunman Mikhail, Russia"""
    pattern1 = r""" *[1-2][0-9]{3}\.[0-1][0-9]\.[0-3][0-9] *[0-2][0-9]:[0-5][0-9] *"""
    pattern2 = r""" *[0-2][0-9]:[0-5][0-9] *"""
    if re.match(pattern1, input) is not None:
        return 1
    if re.match(pattern2, input) is not None:
        return 2

    return 0