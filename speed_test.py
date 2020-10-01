from litecoder.usa import USCityIndex, USStateIndex
import time

print("Loading USCityIndex... ", end="")
start_time = time.time()
city_idx = USCityIndex()
city_idx.load()
print("finished: {}s!".format(time.time() - start_time))

print("Loading USStateIndex... ", end="")
start_time = time.time()
state_idx = USStateIndex()
state_idx.load()
print("finished: {}s!".format(time.time() - start_time))

city_tests = """Edinburg, Texas
Lakeville , Minnesota
Woodland, CA.
Gary, IN
Cornelius, NC
Okeechobee, Fl
Saginaw Township South, MI
Lansdowne, PA
Knoxville TN
OAKLAND, CA
suffolk va
Port Orange, FL
Sedona, AZ
Cedar City UT 
Cincinnati. 
Huntington Beach CA
Wooster,Ohio
Lewisville, Texas
traverse city mi
Pennsauken, New Jersey
Jonesboro, Arkansas
Zephyrhills, FL
West Jefferson, NC
Escondido, CA 
Lumberton, NC
Cayce, SC
Stratford, Connecticut, USA
Avondale, AZ
Coral Springs, FL 
Gaithersburg, MD
Westchester, IL
Louisa, Virginia 
Norway, ME
Philadelphia PA, USA
Fort worth, tx
Eureka Springs, Arkansas
Nashville , TN
Ellenwood Ga
Floral Park, NY
Nashville Tennessee
Malvern, AR
Valdosta, Georgia
Valley Center Ca
St. Robert Mo. 
Hollandale, MS
New Castle, PA 
Harlem, FL
Kings Mills, OH
knoxville Tennessee
BrooklYn""".split("\n")
# for x in range (10):
#     city_tests += city_tests
print("measuring time for {} cities... ".format(len(city_tests)), end="")
start_time = time.time()
for city in city_tests:
    x = city_idx[city]
print("finished: took {}s!".format(1000*(time.time() - start_time)))
state_tests = """North Carolina, USA   
District of Columbia
Illinois, United States
Georgia United States 
north carolina
texas
iowa
Florida, United States
Vermont,  USA
TX USA 
FL U.S.A.
pennsylvania usa
nebraska 
 Oregon 
Pennsylvania 
New Hampshire  USA
Nebraska, USA
New mexico
Indiana    
South Dakota 
 Oklahoma
Ohio,US
Kansas, USA 
indiana
MA, USA
 New York
Ohio, United States
NJ USA
ohio usa
Connecticut, USA
MICHIGAN, United States
Missouri
New York
California - USA
Massachusetts, USA 
 Missouri
FL, United States of America
New Hampshire
Georgia.
Nevada USA
 PENNSYLVANIA
Virginia, USA.
Alabama, USA
Indiana 
Louisiana, United States
New Mexico 
Ohio USA
Nevada, USA
LOUISIANA
New Jersey, us""".split("\n")
print("measuring time for {} states... ".format(len(state_tests)), end="")
start_time = time.time()
for state in state_tests:
    x = state_idx[state]
print("finished: took {}s!".format(1000 * (time.time() - start_time)))
