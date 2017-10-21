import sys
import socket
import time
import threading
import os.path 
import math
import re
from random import randint

from Graph import Graph

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


def dijsktra(NETWORK_SCHEME, graph,start_node,end_node):
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
				if NETWORK_SCHEME=="SHP":
					weight=current_weight+1
				elif NETWORK_SCHEME== "SDP":
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


def main():
	NETWORK_SCHEME=sys.argv[1]
	ROUTING_SCHEME=sys.argv[2]
	TOPOLOGY_FILE=sys.argv[3]
	WORKLOAD_FILE=sys.argv[4]
	PACKET_RATE=sys.argv[5]
	my_graph=create_graph(TOPOLOGY_FILE)
	
	my_graph=update_used(my_graph,'BD',1)
	my_graph=update_used(my_graph,'AF',1)
	my_graph=update_used(my_graph,'EF',1)
	my_graph=update_used(my_graph,'BD',1)
	path,delay_time=dijsktra(ROUTING_SCHEME,my_graph,'A','C')
	print(path)
	print(delay_time)
	my_graph=update_used(my_graph,'BD',-1)
	path,delay_time=dijsktra(NETWORK_SCHEME,my_graph,'A','C')

	print(path)
	print(delay_time)
	print(randint(0, 9))
	print(randint(0, 9))
	print(randint(0, 9))
	print(randint(0, 9))
	



if __name__=='__main__':
	main()
