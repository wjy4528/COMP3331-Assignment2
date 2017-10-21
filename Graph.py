from Node import Node

class Graph(object):
	def __init__(self):
		self.graph=[]


	def add_Node(self, new_node):
		exist=False
		for node in self.graph:
			if node.name==new_node:
				exist=True
		if not exist:
			new_node=Node(new_node)
			self.graph.append(new_node)


	def add_adj(self, start_node, end_node, dtime, load):
		for node in self.graph:
			if start_node==node.name:
				exist=False
				for each in node.adj_node:
					if each['name']==end_node:
						exist=True
				if not exist:
					for ea in self.graph:
						if end_node==ea.name:
							info={'Node':ea,'name':end_node,'dtime':dtime,'load':load,'used':0, "Full": False}
							node.adj_node.append(info)

