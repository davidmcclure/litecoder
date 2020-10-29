from litecoder.usa import USCityIndex, USStateIndex
import time

print("Loading USCityIndex... ", end="")
start_time = time.time()
city_idx = USCityIndex()
city_idx.load()
print("finished: {}s!".format(time.time() - start_time))

# Load 50 test city lookups
with open("tests/runtime/test_city_lookups.txt", "r") as lookups_file:
    city_tests = lookups_file.read().splitlines()

# Increase the number of lookups for the speed test if necessary
for x in range (5):
    city_tests += city_tests
num_tests = len(city_tests)
print("measuring time for {} cities... ".format(num_tests), end="")
start_time = time.time()
for city in city_tests:
    city_idx[city]
ms = 1000*(time.time() - start_time)
print("finished: took {}ms at {} ms/lookup!".format(ms, float(ms/num_tests)))

print("Loading USStateIndex... ", end="")
start_time = time.time()
state_idx = USStateIndex()
state_idx.load()
print("finished: {}s!".format(time.time() - start_time))

# Load 50 test state lookups
with open("tests/runtime/test_state_lookups.txt", "r") as lookups_file:
    state_tests = lookups_file.read().splitlines()

# Increase the number of lookups for the speed test if necessary
for x in range (5):
    state_tests += state_tests
num_tests = len(state_tests)
print("measuring time for {} states... ".format(num_tests), end="")
start_time = time.time()
for state in state_tests:
    state_idx[state]
ms = 1000*(time.time() - start_time)
print("finished: took {}ms at {} ms/lookup!".format(ms, float(ms/num_tests)))
