# 14點
import networkx as nx
import random
import copy

# 建立空的圖形
G = nx.Graph()
nodes = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
G.add_nodes_from(nodes)

distances = {
    ("0", "1"): 21,
    ("0", "4"): 21,
    ("1", "2"): 21,
    ("1", "5"): 28,
    ("2", "3"): 7,
    ("2", "6"): 14,
    ("3", "7"): 7,
    ("4", "5"): 7,
    ("4", "8"): 7,
    ("5", "6"): 14,
    ("5", "9"): 28,
    ("6", "7"): 35,
    ("6", "10"): 21,
    ("7", "11"): 21,
    ("8", "9"): 28,
    ("9", "10"): 7,
    ("10", "11"): 7,
    ("10", "12"): 35,
    ("11", "13"): 14,
    ("12", "13"): 7,
}

# 建立距離矩陣
for i in nodes:
    for j in nodes:
        if i == j:
            distances[(i,j)] = 0
        else:
            if (i,j) not in distances.keys():
                distances[(i,j)] = -999

for (src, dst), distance in distances.items():
    if distance != -999:
        G.add_edge(src, dst, weight=distance)
        G.add_edge(dst, src, weight=distance)  

dist_matrix = nx.floyd_warshall_numpy(G, weight="weight")


# 初始化 
node_list = [0, 5, 6, 8, 10, 13]
speed = 70
working_hours = 9
total_dis = speed * working_hours
start_node = 0
max_power = 3000

# 這邊採用將時間改為距離的方式去對應其可送貨的時間，也就是車輛行駛總距離
# 以第一點為例，[0,630]，即是該點可以從[8:00 - 15:00(70*9=630)]都可以經過 
node_available = [[0, 630], [0, 70], [70, 210], [140, 280], [350, 490], [560, 630]]
node_demand = [0, 1000, 1500, 1300, 1000, 2000]

# fitness計算方法
def fitness_count_Show(orders):
    final_result = copy.deepcopy(orders)
    
    power_flow = 0 # 總送電
    dis_run = 0 # 總距離(時間)
    current_power = max_power # 車上電量

    for i, v in enumerate(orders[:-1]):
        current_point = orders[i] # 當前點
        next_point = orders[i+1] # 下一點
        next_power = node_demand[node_list.index(next_point)] # 下一點電量需求

        if next_power > current_power: # 如果到下一點的電量夠不夠
            dis_run += dist_matrix[current_point][0] # 先開回原點
            current_power = max_power # 把電補滿
            final_result.insert((final_result.index(current_point))+1,0)
            current_point = 0
        next_availabe = node_available[node_list.index(next_point)] # 下一點營業時間
        next_dis = dist_matrix[current_point][next_point] # 當前點跟下一點距離
        dis_run += next_dis # 繼續前往下一點
        # 如果早於該站點前到，則要等到時間到
        if dis_run < next_availabe[0]: 
            dis_run = next_availabe[0]        
            
        if dis_run < speed*working_hours and  (next_availabe[0]<=dis_run<=next_availabe[1]):          
            power_flow += next_power
            current_power -= next_power
        else:
            break
    return power_flow, orders, final_result


best_result = 0
best_path = []

# 用簡易的GA進行計算
best_parents = None
best_parents_score = 0
for _ in range(1000):
    parent = [0] + random.sample(node_list[1:], len(node_list)-1)
    flow, orders, result = fitness_count_Show(parent)
    if flow > best_parents_score:
        best_parents_score = flow
        best_parents = orders
best_order = best_parents.copy()
best_result = best_parents_score
fitness = []
for _ in range(1000):
    numbers = random.sample(range(1, len(node_list)), 2)
    candidate = best_order.copy()
    candidate[numbers[0]], candidate[numbers[1]] = candidate[numbers[1]], candidate[numbers[0]]
    flow, orders, result = fitness_count_Show(candidate)
    fitness.append(flow)
    if flow >= best_result:
        best_order = orders
        best_result = flow
        best_path = result

final_path = []
for i in range(len(best_path)-1):
    if i == (len(best_path)-2):
        final_path+=(nx.shortest_path(G, str(best_path[i]), str(best_path[i+1])))
    else:
        final_path+=(nx.shortest_path(G, str(best_path[i]), str(best_path[i+1]))[:-1])
print(f'最大流量: {best_result}')
print(f'節點順序: {best_path}')
print(f'總節點路徑: {final_path}')
