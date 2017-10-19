import time 
import math
import collection
import re
import os.path 

#for testing only
import sys

#global vars
total_circuit_request = 0
total_packets = 0
total_success_packets = 0
total_blocked_packets = 0
avg_cumulative_prog = 0
total_paths = 0
total_hops = 0

'''
example log 
0.123456 A D 12.527453 
7.249811 B C 48.129653 
8.975344 B D 6.124743 
10.915432 A C 106.724339 
15.817634 B C 37.634569


pre-requisite 

input: time(secs) nodeA(src) nodeB(dest) active_duration(secs)

output:

'''


def workload(input, packet_rate):
	#some vars
	m = re.search('(.*\d+) (/w) (/w) (.*\d+)', input )
	elapse = float(m.group(1))
	num_packets = round(float(packet_rate)*float(m.group(4)))
	source = m.group(2)
	destin = m.group(3)
	packet_dur = round(num_packets/float(packet_rate))


	print "debugging here:"
	print "elapse" + str(elapse)
	print "number of packets" + str(num_packets)
	print "source " + str(source)
	print "destination " + str(destin)

	#case 1
	#use routing protocol once and send packets through the same route


	#case 2
	#use routing protocol multiple times and 
	#find appropriate path for each packet (time elapse and time is important here)

	#blocked request

	#busy: route once the circuit has been established

#testing main 
def init_stats():
	#check if file exist 
	#if so delete and make new
	fname = "./log.txt"
	if (os.path.exists(fname)):
		print "it exists"
	else:
		print "no file exist in directory"
	

def log_statistics():
	#calculates the statistics and appedn to file

	success_percentage_routed_packets = total_success_packets/total_success_packets
	blocked_percent = total_blocked_packets/total_packets
	avg_hops = total_hops/total_paths

	f = open("stats.txt", 'a+')

	f.write("total number of virtual circuit requests:" + str(total_circuit_request))
	f.write("total number of packets:" + str())
	f.write("number of successfully routed packets:" + str())
	f.write("percentage of successfully routed packets:" + str()) 
	f.write("number of blocked packets:" + str())
	f.write("percentage of blocked packets:" + str())
	f.write("average number of hops per circuit:" + str())
	f.write("average cumulative propagation delay per circuit:" + str())

	f.close()


def print_stats():
	#for debugging purposes
	f = open("stats.txt", 'r')

	for line in iter(f):
		print line 
	f.close()


def cal_avg_delay():
	#array of delay over, each element calculated individually based off the other delay
	#add up all the delays in the array over total circuits
	pass


def cal_avg_hops():
	#total hops per circuit
	#over total circuits
	pass



workload(sys.args)
init_stats()
log_statistics()
print_stats()

