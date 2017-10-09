import sys
import socket
import time
import threading
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


def dijsktra(graph,start_node,end_node):
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
			weight=current_weight+int(edge['dtime'])
			if edge['name'] not in visited or weight < visited[edge['name']]:
				visited[edge['name']]=weight
				path[edge['name']]=min_node.name
	search_key=end_node
	path_to_return=search_key

	while search_key!=start_node:
		temp=path[search_key]
		path_to_return=temp+path_to_return
		search_key=temp

	return path_to_return





def main():
	NETWORK_SCHEME=sys.argv[1]
	ROUTING_SCHEME=sys.argv[2]
	TOPOLOGY_FILE=sys.argv[3]
	WORKLOAD_FILE=sys.argv[4]
	PACKET_RATE=sys.argv[5]

	my_graph=create_graph(TOPOLOGY_FILE)

	path=dijsktra(my_graph,'A','O')
	#print(visited)
	print(path)

	'''
	for each in my_graph.graph:

		print(each.name)
		print("adj_node")
		for one in each.adj_node:
			print(one['name'])
		print("------------")
	'''




if __name__=='__main__':
	main()