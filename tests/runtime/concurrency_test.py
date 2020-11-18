from multiprocessing import Pool
from litecoder.usa import USCityIndex, USStateIndex
import time

NUM_PROCESSES = 4

# Load 50 test city lookups
with open("tests/runtime/test_city_lookups.txt", "r") as lookups_file:
    city_tests = lookups_file.read().splitlines()

# Increase the number of lookups for the speed test if necessary
for x in range (10):
    city_tests += city_tests
num_tests_per_process = len(city_tests)
num_tests = NUM_PROCESSES * num_tests_per_process

# Load USCityIndex
city_idx = USCityIndex()
city_idx.load()


def lookup_cities(process_num):
    print ('Process {}: looking up {} cities'.format(process_num, num_tests_per_process))
    start_time = time.time()
    for city in city_tests:
        city_idx[city]
    ms = 1000*(time.time() - start_time)
    print("Process {}: finished, took {}ms @ {} ms/lookup!".format(process_num, ms, float(ms/num_tests_per_process)))

if __name__ == '__main__':
    print("Looking up {} cities on {} processes...".format(num_tests, NUM_PROCESSES))
    start_time = time.time()
    with Pool(5) as p:
        p.map(lookup_cities, range(1, NUM_PROCESSES+1))
    ms = 1000*(time.time() - start_time)
    print("Fully finished: took {}ms @ {} ms/lookup!".format(ms, float(ms/num_tests)))
    
    print()
    print("Looking up all {} cities on one process...".format(num_tests), end="")
    start_time = time.time()
    for i in range(NUM_PROCESSES):
        for city in city_tests:
            city_idx[city]
    ms = 1000*(time.time() - start_time)
    print("finished: took {}ms @ {} ms/lookup!".format(ms, ms/num_tests))