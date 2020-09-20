from litecoder.usa import USCityIndex, USStateIndex

city_idx = USCityIndex()
state_idx = USStateIndex()

states = """North Carolina, USA   
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

cities = """Edinburg, Texas
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
output = ""
for state in states:
	if (len(state_idx[state]) == 0):
		print(state)
	wof_ids = [result.data.wof_id for result in state_idx[state]]
	output += """- query:
    - {}
  matches:\n""".format(state)
	for wof_id in wof_ids:
		output += "    - {}".format(wof_id)
	output += "\n"
with open("output.yml", "w") as o_file:
	o_file.write(output)
