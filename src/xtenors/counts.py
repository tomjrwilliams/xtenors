
# def day_count_factor(dt1, dt2, dt3 = None, freq = None):
#     """

#     """
#     count_enum = conventions.COUNT
#     count = count_enum.current()

#     dc1 = day_count(dt1, dt2)

#     min_d = min((dt1, dt2))
#     max_d = max((dt1, dt2))

#     if dt3 is not None:
#         dc2 = day_count(dt1, dt3)

#     if count in conventions.COUNT_360:
#         return dc1 / 360
    
#     elif count == count_enum.ACTUAL_365_F:
#         return dc1 / 365
    
#     elif count == count_enum.ACTUAL_360:
#         return dc1 / 360
    
#     elif count == count_enum.ACTUAL_364:
#         return dc1 / 364
    
#     elif count == count_enum.ACTUAL_ACTUAL_ICMA:
#         return dc1 / (freq * dc2)
    
#     elif count == count_enum.ACTUAL_365_L:
#         if freq != 1 and _is_leap_year(dt2.year):
#             div = 366
#         elif freq == 1 and any((
#             _is_leap_year(y)
#             for y in range(min_d.year, max_d.year + 1)
#         )):
#             div = 366
#         else:
#             div = 365
        
#         return dc1 / div

#     elif count == count_enum.ACTUAL_ACTUAL_ISDA:
#         if dt1.year == dt.year:
#             return dc1 / (
#                 366 if _is_leap_year(dt1.year) else 365
#             )
        
#         sign = 1 if dt1 < dt2 else -1

#         left_stub = day_count(min_d, datetime.date(
#             min_d.year + 1, 1, 1
#         ))
#         right_stub = day_count(datetime.date(
#             max_d.year - 1, 12, 31
#         ), max_d)

#         y_delta = max_d.year - min_d.year

#         return sign * sum(
#             y_delta - 1,
#             left_stub / (
#                 366 if _is_leap_year(min_d.year) else 365
#             ),
#             right_stub / (
#                 366 if _is_leap_year(max_d.year) else 365
#             ),
#         )

#     elif count == count_enum.ACTUAL_ACTUAL_AFB:

#         sign = 1 if dt1 < dt2 else -1
#         n_years = max_d.year - min_d.year

#         dt_adj = max_d + Tenor(
#             unit=UNIT.Y, n = n_years
#         )

#         dc_adj = day_count(dt1, dt_adj)

#         return sign * sum((
#             n_years,
#             dc_adj / (
#                 366 if _is_leap_year(dt1) else 365
#             )
#         ))

#     elif count == count_enum.N_1_1:
#         assert False, dict(count=count, enum=count_enum)
#     else:
#         assert False, dict(count=count, enum=count_enum)

# @functools.lru_cache(maxsize=100)
# def _ndays_february(y):
#     return pycalendar.monthrange(y, 2)[1]

# @functools.lru_cache(maxsize=100)
# def _is_leap_year(y):
#     return _ndays_february(y) == 29

# # TODO: split cases to separate functions?
# # so that have separate doctests and easier to read?

# def day_count(dt1, dt2):
#     """
    
#     """
#     count_enum = conventions.COUNT
#     count = count_enum.current()

#     y1, m1, d1 = unpack_date(dt1)
#     y2, m2, d2 = unpack_date(dt2)

#     if (
#         count == count_enum.SIMPLE
#         or count in conventions.COUNT_ACTUAL
#     ):
#         return (dt2 - dt1).days

#     elif count in conventions.COUNT_360:

#         if count == count_enum.N_30_360_BOND:

#             d1 = min((d1, 30))
#             if d1 > 29:
#                 d2 = min((d2, 30))

#         elif count == count_enum.N_30_360_US:

#             # first two conditions, only iF interest end of month?

#             d1_eo_feb = d1 == _ndays_february(y2)
#             d2_eo_feb = d2 == _ndays_february(y2)

#             if d1_eo_feb and d2_eo_feb:
#                 d2 = 30
            
#             if d1_eo_feb:
#                 d1 = 30

#             if d2 > 30 and d1 > 29:
#                 d2 = 30
            
#             d1 = min((31, 30))

#         elif count == count_enum.N_30E_360:

#             d1 = min((d1, 30))
#             d2 = min((d2, 30))

#         elif count == count_enum.N_30E_360_ISDA:

#             d1 = min((d1, 30))
#             d2 = min((d2, 30))

#             if m1 == 2 and d1 == _ndays_february(y1):
#                 d1 = 30

#             # if d2 is not maturity date?
#             if m2 == 2 and d2 == _ndays_february(y2):
#                 d2 = 30

#         elif count == count_enum.N_30E_PLUS_360:

#             d1 = min((d1, 30))
#             if d2 == 31:
#                 m2 += 1
#                 d2 = 1
        
#         else:
#             assert False, dict(count=count, enum=count_enum)

#         return sum((
#             360 * (y2 - y1),
#             30 * (m2 - m1),
#             d2 - d1
#         ))
    
#     elif count == count_enum.N_1_1:
#         assert False
#     else:
#         assert False, dict(count=count, enum=count_enum)
    