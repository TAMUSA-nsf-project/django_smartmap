from routedatautil import BusStop, RouteSchedule

# create BusStop objects
# !!!TODO coords was just added as an argument to the constructor of BusStop, provide that data below
# TODO also provide the bus stop number
nwvc = BusStop("Northwest Vista College")
swme = BusStop("Sea World Main Entrance")
phwy = BusStop("Potranco &  Hwy. 151")
kltc = BusStop("Kel-Lac Transit Center")
dam = BusStop("Dolorosa & Main")

# create route objects
eastbound_mf = RouteSchedule("Route 555", "W")
eastbound_mf.addSchedule(nwvc, [615, *[x * 100 + 55 for x in range(6, 22)]])
eastbound_mf.addSchedule(swme, [1059, 1159, 1259, 1359, 1500, 1600, 1700, 1759, 1859, 1959, 2058, 2158])
eastbound_mf.addSchedule(phwy, [626, 707, 807, 907, 1007, 1108, 1208, 1308, 1408, 1510, 1610, 1710, 1807,
                                1907, 2007, 2106, 2206])
eastbound_mf.addSchedule(kltc, [642, 724, 823, 923, 1023, 1124, 1224, 1324, 1424, 1529, 1629, 1729, 1822,
                                1922, 2022, 2120, 2220])
eastbound_mf.addSchedule(dam, [716, 819, 913, 1013, 1113, 1213, 1314, 1414, 1515, 1615, 1718, 1813, 1913, 2013,
                               2113, 2213, 2313, 2417])
eastbound_mf.exportRouteScheduleToJSON()

westbound_mf = RouteSchedule("Route 64 (reverse)", "W")
westbound_mf.addSchedule(dam, [515, 615, 715, 819, 914, 1014, 1114, 1214, 1314, 1414, 1515, 1615, 1714, 1814, 1914,
                               2013, 2113])
westbound_mf.addSchedule(kltc, [534, 634, 734, 838, 934, 1034, 1134, 1234, 1334, 1434, 1538, 1638, 1737, 1837, 1935,
                                2034, 2133])
westbound_mf.addSchedule(phwy, [610, 711, 811, 911, 1011, 1111, 1211, 1311, 1411, 1513, 1613, 1713, 1813, 1911, 2011,
                                2110, 2210])
westbound_mf.addSchedule(nwvc, [621, 724, 824, 923, 1023, 1123, 1225, 1325, 1425, 1527, 1627, 1727, 1827, 1924, 2024,
                                2122, 1222])
westbound_mf.exportRouteScheduleToJSON()

eastbound_sat = RouteSchedule("Route 64", "S")
eastbound_sat.addSchedule(nwvc, [621, 721, 822, 922, 1024, 1124, 1224, 1324, 1424, 1524, 1624, 1724, 1824, 1924, 2024,
                                 2122, 2222])
eastbound_sat.addSchedule(swme, [1028, 1128, 1228, 1328, 1428, 1528, 1628, 1728, 1828, 1928, 2028, 2126, 2226])
eastbound_sat.addSchedule(phwy,
                          [631, 731, 833, 933, 1037, 1137, 1238, 1338, 1438, 1538, 1638, 1738, 1838, 1938, 2038, 2134,
                           2234])
eastbound_sat.addSchedule(kltc,
                          [644, 744, 848, 948, 1053, 1153, 1255, 1355, 1455, 1555, 1655, 1755, 1855, 1955, 2055, 2150,
                           2250])
eastbound_sat.addSchedule(dam,
                          [714, 814, 914, 1014, 1115, 1216, 1316, 1416, 1516, 1616, 1716, 1816, 1914, 2014, 2114, 2213,
                           2313, 2317, 2417])
eastbound_sat.exportRouteScheduleToJSON()

westbound_sat = RouteSchedule("Route 64 (reverse)", "S")
westbound_sat.addSchedule(dam,
                          [514, 614, 714, 814, 914, 1014, 1115, 1216, 1316, 1416, 1516, 1616, 1716, 1816, 1914, 2014,
                           2114])
westbound_sat.addSchedule(kltc,
                          [532, 632, 732, 833, 933, 1034, 1135, 1237, 1337, 1437, 1537, 1637, 1737, 1837, 1935, 2035,
                           2134])
westbound_sat.addSchedule(phwy,
                          [610, 710, 810, 910, 1011, 1111, 1211, 1311, 1411, 1511, 1611, 1711, 1811, 1911, 2011, 2110,
                           2210])
westbound_sat.addSchedule(nwvc, [621, 721, 822, 922, 1024, 1124, 1224, 1324, 1424, 1724, 2024, 2122, 2222])
westbound_sat.exportRouteScheduleToJSON()

eastbound_sun = RouteSchedule("Route 64", "F")
eastbound_sun.addSchedule(nwvc,
                          [722, 822, 922, 1022, 1122, 1222, 1322, 1422, 1522, 1622, 1722, 1822, 1923, 2023, 2122, 2222])
eastbound_sun.addSchedule(swme, [926, 1026, 1126, 1227, 1327, 1427, 1527, 1627, 1727, 1827, 1927, 2027, 2126, 2226])
eastbound_sun.addSchedule(phwy,
                          [732, 832, 936, 1036, 1136, 1237, 1337, 1437, 1537, 1637, 1737, 1837, 1937, 2037, 2135, 2235])
eastbound_sun.addSchedule(kltc,
                          [655, 747, 847, 952, 1052, 1152, 1253, 1353, 1453, 1553, 1653, 1753, 1853, 1952, 2052, 2149,
                           2249])
eastbound_sun.addSchedule(dam,
                          [714, 814, 914, 1014, 1114, 1214, 1314, 1414, 1514, 1614, 1714, 1814, 1913, 2013, 2113, 2213,
                           2313, 2317, 2417])
eastbound_sun.exportRouteScheduleToJSON()

westbound_sun = RouteSchedule("Route 64 (reverse)", "F")
westbound_sun.addSchedule(dam,
                          [614, 714, 814, 914, 1014, 1114, 1214, 1314, 1414, 1514, 1614, 1714, 1814, 1913, 2013, 2113])
westbound_sun.addSchedule(kltc,
                          [634, 734, 834, 934, 1034, 1134, 1235, 1335, 1435, 1535, 1635, 1735, 1835, 1933, 2033, 2133])
westbound_sun.addSchedule(phwy,
                          [709, 809, 909, 1010, 1110, 1210, 1310, 1410, 1510, 1610, 1710, 1810, 1910, 2010, 2110, 2210])
westbound_sun.addSchedule(nwvc,
                          [720, 820, 920, 1022, 1122, 1222, 1322, 1422, 1522, 1622, 1722, 1822, 1922, 2022, 2121, 2221])
westbound_sun.exportRouteScheduleToJSON()
