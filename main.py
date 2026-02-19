import networkx as nx
import matplotlib.pyplot as plt
import random
from line_profiler_pycharm import profile

best_round = 9999999
best_sequence = []
checked_sequences = dict()

def get_color_map(G):
    color_map = []
    for v in G.nodes():
        if G.nodes[v]["state"] == "burned":
            color_map.append("red")
        else:
            color_map.append("lightgray")
    return color_map

def draw_graph(G, pos):
    color_map = get_color_map(G)
    nx.draw(G, pos, node_color=color_map, with_labels=True)
    plt.show()


@profile
def do_todo_nodes(G, todo_nodes, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, burned_bitmap): # basically updates if the nodes are burned or not and updates status
    new_todo_nodes = list()
    while len(todo_nodes) > 0:
        current_node = todo_nodes.pop()
        for neighbor in G.neighbors(current_node):
            if neighbor in unburned_nodes_set:
                nodes_dict[neighbor] += 1
                if(nodes_dict[neighbor] >= 2):
                    #print("Burned :", neighbor)
                    burned_bitmap |= (1 << neighbor)
                    burned_nodes_set.add(neighbor)
                    unburned_nodes_set.remove(neighbor)
                    unburned_nodes_list.remove(neighbor)       # this takes O(n) time so bad you can fix with other data structures later todo
                    #G.nodes[neighbor]["state"] = "burned"
                    new_todo_nodes.append(neighbor)
    return new_todo_nodes, burned_bitmap

def main():
    graph_size = 100

    burned_nodes_set = set()

    unburned_nodes_list = [i for i in range(graph_size)]  # list of unburned nodes
    nodes_dict = {i: 0 for i in range(graph_size)}  # dict of unburned nodes
    unburned_nodes_set = {i for i in range(graph_size)}  # set of unburned nodes

    G = nx.erdos_renyi_graph(graph_size, 0.2, seed=123, directed=False)

    pos = nx.spring_layout(G, seed=432)

    nx.set_node_attributes(G, "unburned", "state")

    print(list(G.nodes))
    print(list(G.edges))

    draw_graph(G,pos)
    rec_alg(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, pos,[], 0, [], 0)

    nx.set_node_attributes(G, "unburned", "state")

    play_sequence(G, best_sequence,pos)


@profile
def rec_alg(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, pos, todo, round, sequence, burned_bitmap):
    #heuristic to burn the leaf nodes first
    if(round == 0):
        for i in range(len(G.nodes)):
            node = i
            if G.degree[node] <= 1:
                sequence.append(node)
                round=+1
                nodes_dict[node] = 2
                unburned_nodes_set.remove(node)
                unburned_nodes_list.remove(node)
                burned_nodes_set.add(node)
                burned_bitmap |= (1 << node)
                todo.append(node)
                todo, burned_bitmap = do_todo_nodes(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, burned_bitmap)


    global best_round
    global checked_sequences
    round += 1

    if burned_bitmap in checked_sequences and checked_sequences[burned_bitmap] <= round:
        return
    checked_sequences[burned_bitmap] = round

    if(round >= best_round):
        return

    todo, burned_bitmap = do_todo_nodes(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, burned_bitmap)
    if len(unburned_nodes_set) == 0:
        global best_sequence
        if round < best_round:
            best_round = round
            best_sequence = sequence.copy()

            print("New best round :", best_round)
            print("Sequence :", sequence)
        return
    else:
        for i in range(len(unburned_nodes_list)):
            node_to_burn = unburned_nodes_list[i]

            # backup
            burned_nodes_set_backup = burned_nodes_set.copy()
            unburned_nodes_set_backup = unburned_nodes_set.copy()
            unburned_nodes_list_backup = unburned_nodes_list.copy()
            nodes_dict_backup = nodes_dict.copy()
            todo_backup = todo.copy()
            old_burned_bitmap = burned_bitmap
            #G_backup = G.copy()

            # make changes
            nodes_dict[node_to_burn] = 2
            unburned_nodes_set.remove(node_to_burn)
            unburned_nodes_list.remove(node_to_burn)
            burned_nodes_set.add(node_to_burn)
           # G.nodes[node_to_burn]["state"] = "burned"
            todo.append(node_to_burn)
            sequence.append(node_to_burn)
            burned_bitmap |= (1 << node_to_burn)
            print(sequence)

            rec_alg(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, pos, todo, round, sequence, burned_bitmap)

            # restore
            burned_nodes_set = burned_nodes_set_backup
            unburned_nodes_set = unburned_nodes_set_backup
            unburned_nodes_list = unburned_nodes_list_backup
            nodes_dict = nodes_dict_backup
          #  G = G_backup
            todo = todo_backup
            sequence.pop()
            burned_bitmap = old_burned_bitmap

# def greedy_alg(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, pos):


def play_sequence(G, sequence, pos):
    burned_nodes_set = set()
    unburned_nodes_list = [i for i in range(len(G.nodes))]  # list of unburned nodes
    nodes_dict = {i: 0 for i in range(len(G.nodes))}  # dict of unburned nodes
    unburned_nodes_set = {i for i in range(len(G.nodes))}  # set of unburned nodes
    todo = list()
    round = 0
    for node_to_burn in sequence:
        round += 1
        print(f"Round {round}")

        todo, bitmap = do_todo_nodes(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, 0)

        if len(unburned_nodes_set) == 0:
            print("All nodes burned!")
            draw_graph(G, pos)
            return  # done

        print("Unburned nodes left :", unburned_nodes_set)
        print("Picked Burning node :", node_to_burn)

        nodes_dict[node_to_burn] = 2
        unburned_nodes_list.remove(node_to_burn)
        unburned_nodes_set.remove(node_to_burn)
        burned_nodes_set.add(node_to_burn)
        G.nodes[node_to_burn]["state"] = "burned"
        todo.append(node_to_burn)
        draw_graph(G, pos)
    print("All nodes burned!")
    nx.set_node_attributes(G, "burned", "state")
    draw_graph(G, pos)
    return


if __name__ == "__main__":
    main()