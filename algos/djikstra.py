""""""
import sys
from heapq import heappush, heapify


def djikstra(graph, src, dest):
    inf = sys.maxsize
    node_data = {key: {'cost': inf, 'pred': []} for key in graph.keys()}
    node_data[src]['cost'] = 0
    visited = []
    temp = src

    for i in range(len(node_data.keys())):
        min_heap = []
        heapify(min_heap)
        if temp not in visited:
            visited.append(temp)
            for j in graph[temp]:
                if j not in visited:
                    cost = node_data[temp]['cost'] + graph[temp][j]
                    if cost < node_data[j]['cost']:
                        node_data[j]['cost'] = cost
                        node_data[j]['pred'] = node_data[temp]['pred'] + list(temp)
                    heappush(min_heap, (node_data[j]['cost'], j))

                    print("MIN HEAP:", min_heap)
                    temp = min_heap[0][1]

    print("Shortest Distance: " + str(node_data[dest]['cost']))
    print("Shortest Path: " + str(node_data[dest]['pred'] + list(dest)))
