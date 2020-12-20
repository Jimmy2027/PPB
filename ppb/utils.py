# HK, 17.12.20
def get_unique_str(prefix: str = '') -> str:
    from datetime import datetime
    dateTimeObj = datetime.now()
    dateStr = dateTimeObj.strftime("%Y_%m_%d_%H_%M_%S_%f")
    if prefix:
        return '_'.join([prefix, dateStr])
    else:
        return dateStr