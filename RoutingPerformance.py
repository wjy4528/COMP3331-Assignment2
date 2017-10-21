import sys
import socket
import time
import threading
import os.path 
import math
import re
from Graph import Graph


#program usable :  python3 RoutingPerformance.py CIRCUIT SDP topology1.txt workloadexample.txt 2

#global counters
total_request = 0
total_packets = 0

total_success_packets = 0
total_blocked_packets = 0

#to cal avg hops
total_circuits = 0
total_hops = 0

#arr of global counters
arr_avg_delay = []

def create_graph(TOPOLOGY_FILE):
	my_graph=Graph()
	with open(TOPOLOGY_FILE,'r') as ff:
		for line in ff:
			node_name=line.split(' ')[0]
			node_name_1=line.split(' ')[1]
			delay_time=line.split(' ')[2]
			max_laod=line.split(' ')[3].split('\n')[0]
			my_graph.add_Node(node_name)
			my_graph.add_Node(node_name_1)
			my_graph.add_adj(node_name,node_name_1,delay_time,max_laod)
			my_graph.add_adj(node_name_1,node_name,delay_time,max_laod)
	return my_graph


def dijsktra(ROUTING_SCHEME, graph,start_node,end_node):
	for each in graph.graph:
		for each_1 in each.adj_node:
			if each_1['used'] >= int(each_1['load']):
				each_1['Full']=True
			else:
				each_1['Full']=False
	visited={start_node:0}
	path={}
	nodes=set(graph.graph)
	while nodes:
		min_node=None
		for node in nodes:
			if node.name in visited:
				if min_node is None:
					min_node=node
				elif visited[node.name]<visited[min_node.name]:
					min_node=node
		if min_node is None:
			break
		nodes.remove(min_node)
		current_weight=visited[min_node.name]
		for edge in min_node.adj_node:
			if edge['Full']==False:
				if ROUTING_SCHEME=="SHP":
					weight=current_weight+1
				elif ROUTING_SCHEME== "SDP":
					weight=current_weight+int(edge['dtime'])
				else:
					current_load=float(edge['used'])/float(edge['load'])
					if current_weight<current_load:
						weight=current_load
					else:
						weight=current_weight
				if edge['name'] not in visited or weight < visited[edge['name']]:
					visited[edge['name']]=weight
					path[edge['name']]=min_node.name
	search_key=end_node
	path_to_return=search_key
	
	while search_key!=start_node:
		try:
			temp=path[search_key]
			path_to_return=temp+path_to_return
			search_key=temp
		except:
			return "",0
	
	total_delay=0
	for i in range(0,len(path_to_return)-1):
		node_name=path_to_return[i]
		adj_node_name=path_to_return[i+1]
		for each_1 in graph.graph:
			if each_1.name==node_name:
				for each_2 in each_1.adj_node:
					if each_2['name']==adj_node_name:
						total_delay+=int(each_2['dtime'])
						break
				break
	return path_to_return,total_delay

def update_used(my_graph, path, value):
	for i in range(0,len(path)-1):
		node_name=path[i]
		adj_node_name=path[i+1]
		for each_1 in my_graph.graph:
			if each_1.name==node_name:
				for each_2 in each_1.adj_node:
					if each_2['name']==adj_node_name:
						each_2['used']+=value
						for each_3 in each_2['Node'].adj_node:
							if each_3['name']==node_name:
								each_3['used']+=value
								break
						break
				break
	return my_graph

#dictionary of 
dict_prev_time = {}

#case only work for circuit switching, need to test
def circuit_case(graph, source, destin, curr_time, duration, n_scheme, r_scheme, num_packets):
	global total_delay
	global total_hops
	global total_success_packets
	global total_blocked_packets
	global total_circuits
	global total_packets
	global dict_prev_time

	
	print ("\n")
	print ("circuit switching---------------------")
	print ("source: " + source)
	print ("destination: " + destin)
	print ("the network scheme: " + r_scheme)

	packet_finish_t = float(curr_time) + float(duration)

	print ("packet finish time: " + str(packet_finish_t))

	#if dictionary is not empty
	if (bool(dict_prev_time)):
		print ("dictionary is not empty here")

		#sort the dictionary here to make it faster here
		sorted(dict_prev_time)

		for key in list(dict_prev_time.keys()):
			if (float(curr_time) >= key):
				#update, -1 for packet atm
				print("checking path: " + dict_prev_time[key])
				graph = update_used (graph, dict_prev_time[key], -1)
				#delete
				del dict_prev_time[key]


	#get path
	path, dij_delay = dijsktra (r_scheme,graph, source, destin)
	print ("the path is: " + path)

	if (path):
		#update the graph and stats, if path exist
		graph = update_used (graph, path, 1)#does not work here
		total_success_packets += num_packets
		total_hops += len(path)
		print ("the delay it is returning: "+ str(dij_delay))


		append_delay(dij_delay)#append delay here
		total_circuits += 1

		#append to dict_prev_time
		dict_prev_time[packet_finish_t ] = path
	else: 
		total_blocked_packets += num_packets

	total_packets+= num_packets
	#last two stats to answer, do we count it if no circuit/path is returned?

dict_to_send = {}
dict_to_finish = {}

def packet_case(graph, source, destin, curr_time, duration, n_scheme, r_scheme, num_packets, rate):
	#list of packets to route
	#list of tracked previous packets
	global total_delay
	global total_hops
	global total_success_packets
	global total_blocked_packets
	global total_circuits

	global dict_to_send
	global dict_to_finish

	segment_finish_time = float(curr_time) + float(duration)

	print ("the end time for this request:" + str(segment_finish_time))


	#check if the to finish list is empty
	if (bool (dict_to_finish)):
		#if not empty, mark off
		sorted(dict_to_finish)

		#eg {0.63->AB}
		for key,value in dict_to_finish.item():
			if (float(curr_time) >= key):
				#update, -1 for packet atm
				graph = update_used (graph, value, -1)
				#delete
				del dict_to_finish[key]
				#does not update stats


	if (bool (dict_to_send)):
		#if not empty, get path
		sorted(dict_to_send)

		#eg {0.63->AB}
		for key,value in dict_to_send.item():
			if (float(curr_time) >= key):
				#update, +1 for packet atm
				dij_list = list(value)

				#make a dij request here 
				path, dij_delay = dijsktra(graph, dij_list[0], dij_list[1])

				if (path):
					#add finish list to mark off
					packet_finish_t = key + 1/rate

					dict_to_finishp[packet_finish_t] = path

					#log stats here
					graph = update_used (graph, path, 1)
					total_success_packets += 1
					total_hops += len(path)
					append_delay(dij_delay)
					total_circuits += 1
				else:
					total_blocked_packets += 1

				#delete
				del dict_to_send[key]

	#for debbuging
	print ("\n")
	print ("circuit switching---------------------")
	print ("source: " + source)
	print ("destination: " + destin)
	print ("the network scheme: " + r_scheme)

	print("\n")
	check_total_packets = str(round (float(duration)*float(rate)))
	print ("total number of packets for the segment: " + check_total_packets)

	#push in the first element firsts
	i = float(curr_time)
	iterator_t = 1/int(rate)
	count = 1

	#add to start list, process the ones needed
	while (i < segment_finish_time):
		print (str(count) +". " +str(i) + " : " + source + " -> " + destin)
		count += 1
		i += iterator_t

		#process first packet , and insert the rest





#main processing function
def workload(graph, n_scheme, r_scheme, w_file, rate):

	global total_request

	with open(w_file) as fp:

		line = fp.readline()

		while line:

			val_arr = line.split(" ")
			#m = re.search('(.*\d+) (/w) (/w) (.*\d+)', line)
			
			elapse = val_arr[0]
			source = val_arr[1]
			destin = val_arr[2]
			num_packets = math.floor(float(rate)*float(val_arr[3]))
			request_duration = float(val_arr[3])

			'''			
			print ('\n')
			print ("debugging here:")
			print ("----------------------------")
			print ("elapse: " + str(elapse))
			print ("number of packets: " + str(num_packets))
			print ("source: " + str(source))
			print ("destination: " + str(destin))
			'''

			line = fp.readline()
			#increment the counter
			total_request += 1

			'''
			print ('\n')
			print ('reply')
			print ("----------------------------")
			print (dijsktra(graph, source, destin))
			print ("----------------------------")
			'''


			#print ("checking here: "+ n_scheme)

			if(n_scheme == 'CIRCUIT'):
				#print ("working here")
				#shortest hop path
				#feed function and log
				circuit_case(graph, source, destin, elapse, request_duration, n_scheme, r_scheme, num_packets)
			elif(n_scheme == 'PACKET'):
				packet_case(graph, source, destin, elapse, request_duration, n_scheme, r_scheme, num_packets, rate)
			else:
				print ("something went wrong, closing program...")
				break



#stats functions here
def init_stats():
	#check if file exist 
	#if so delete and make new
	fname = "./log.txt"
	if (os.path.exists(fname)):
		print ("log file exist in directory")
		print ("appending to file ")
	else:
		print ("no log file exist in directory")
	

def log_statistics(routing_type):
	#calculates the statistics and appedn to file

	success_percentage_routed_packets = (total_success_packets/total_packets)*100
	blocked_percent = (total_blocked_packets/total_packets)*100
	avg_hops = total_hops / total_circuits

	f = open("log.txt", 'a+')

	f.write(routing_type+"-----------------------------------------------------")
	f.write("\n")
	f.write("total number of virtual circuit requests:" + str(total_request))
	f.write("\n")
	f.write("total number of packets:" + str(total_packets))
	f.write("\n")
	f.write("number of successfully routed packets:" + str(total_success_packets))
	f.write("\n")
	f.write("percentage of successfully routed packets:" + str(success_percentage_routed_packets))
	f.write("\n") 
	f.write("number of blocked packets:" + str(total_blocked_packets))
	f.write("\n")
	f.write("percentage of blocked packets:" + str(blocked_percent))
	f.write("\n")
	f.write("average number of hops per circuit:" + str(avg_hops))
	f.write("\n")
	f.write("average cumulative propagation delay per circuit:" + str(cal_avg_delay()))
	f.write("\n")

	f.close()


def print_stats():
	#for debugging purposes
	f = open("log.txt", 'r')
	print ("\n")
	for line in iter(f):
		print (line)
	f.close()


def cal_avg_delay():
	#array of delay over, each element calculated individually based off the other delay
	#add up all the delays in the array over total circuits
	total_delay = 0

	for i in arr_avg_delay:
		total_delay += i

	avg_delay = total_delay / len(arr_avg_delay)
	return avg_delay
	#completed

#need to test this 
def append_delay(in_delay):
	global arr_avg_delay

	if (len(arr_avg_delay) == 0):
		arr_avg_delay.append(in_delay)
	else:
		arr_total = 0

		for i in arr_avg_delay:
			arr_total += i

		arr_total += in_delay
		arr_avg_delay.append(arr_total / (len(arr_avg_delay)+1))

	#completed, need to test

def validate_args (network, routing, topology, workload, packet_r):
	vad_boolean = True 
	'''
	print "--------------------------"
	print "valid args debugging log"
	print network 
	print routing
	print topology
	print workload
	print packet_r
	print "---------------------------"
	'''

	#lots of if statements on input checks
	if network not in ["CIRCUIT", "PACKET"]:
		vad_boolean = False
		#print "break 1"

	if routing not in ["SHP", "SDP", "LLP"]:
		vad_boolean = False
		#print "break 2"

	if (not os.path.exists(topology)):
		print ("topology does not exist")
		#print "break 3"
		vad_boolean = False 
	if (not os.path.exists(workload)):
		#print "work load does not exist"
		vad_boolean = False 
	if (int(packet_r) < 0):
		vad_boolean = False
		#print "break 4"


	#print "the return value is " + str(vad_boolean)
	return vad_boolean
	#working

def main():
	NETWORK_SCHEME=sys.argv[1]
	ROUTING_SCHEME=sys.argv[2]
	TOPOLOGY_FILE=sys.argv[3]
	WORKLOAD_FILE=sys.argv[4]
	PACKET_RATE=sys.argv[5]

	#checking arguements here
	if (validate_args(NETWORK_SCHEME, ROUTING_SCHEME, 
		TOPOLOGY_FILE, WORKLOAD_FILE, PACKET_RATE) == False):
		print ("inputs not valid, closing program...")
		sys.exit()


	init_stats()

	my_graph=create_graph(TOPOLOGY_FILE)
	

	#path=dijsktra(my_graph,'A','O')
	#print(visited)
	#print(path)

	workload(my_graph, NETWORK_SCHEME, ROUTING_SCHEME, WORKLOAD_FILE, PACKET_RATE)


	print ("temp debugging =============================")
	print ("the circuit count: "+ str(total_circuits))

	print ("the total packets is: " + str(total_packets))
	print ("the list of cumulative delay is :")
	counteri = 1
	for i in arr_avg_delay:
		print (str(counteri)+ ". " + str(i))
		counteri += 1


	log_statistics(ROUTING_SCHEME)
	print_stats()

	'''
	debugging the graph graph
	for each in my_graph.graph:

		print(each.name)
		print("adj_node")
		for one in each.adj_node:
			print(one['name'])
		print("------------")
	'''




if __name__=='__main__':
	main()
