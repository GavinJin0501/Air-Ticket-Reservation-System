from datetime import *

month_wise = []  # List of lists: [[start_date, end_date, money], .......]

TODAY = datetime.today() - timedelta(days=120)
print(TODAY.strftime("%Y-%m-%d"))
PAST = (TODAY - timedelta(days=365))
THIS_YEAR, PAST_YEAR, THIS_MONTH = TODAY.year, TODAY.year - 1, TODAY.month
month_wise.append(["%d-%02d-01" % (THIS_YEAR, THIS_MONTH), TODAY.strftime("%Y-%m-%d"), 0])
for i in range(1, 6):
    if THIS_MONTH - i > 0:
        temp = ["%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i), "%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i + 1), 0]
    elif THIS_MONTH - i + 1 > 0:
        temp = ["%d-%02d-01" % (PAST_YEAR, 12 + (THIS_MONTH - i)), "%d-%02d-01" % (THIS_YEAR, THIS_MONTH - i + 1),
                0]
    else:
        temp = ["%d-%02d-01" % (PAST_YEAR, 12 + (THIS_MONTH - i)),
                "%d-%02d-01" % (THIS_YEAR, 12 + (THIS_MONTH - i + 1)), 0]
    month_wise.append(temp)
print(month_wise)