import networkx as nx
import matplotlib.pyplot as plt

best_round = 9999999
best_sequence = []

def main():
    graphX = 4
    graph_size = graphX * graphX

    burned_nodes_set = set()

    unburned_nodes_list = [i for i in range(graph_size)]  # list of unburned nodes
    nodes_dict = {i: 0 for i in range(graph_size)}  # dict of unburned nodes
    unburned_nodes_set = {i for i in range(graph_size)}  # set of unburned nodes

    G = nx.grid_2d_graph(graphX, graphX)  # create a grid graph
    G = nx.convert_node_labels_to_integers(G)  # relabel nodes to

  #  G = nx.erdos_renyi_graph(graph_size, 0.1, seed=432)
    nx.set_node_attributes(G, "unburned", "state")
    pos = nx.spring_layout(G, seed=432)
    draw_graph(G, pos)

    rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, [], 1,[])
    print("Best round:", best_round)
    print("Best sequence:", best_sequence)

    #play_sequence(G,[0, 10, 5, 15, 7, 12], pos, graph_size)

    #play_sequence(G, best_sequence, pos)


def burn(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, change_colour):
    next_todo = []
    while len(todo) > 0:
        current_node = todo.pop()

        for neighbor in G.neighbors(current_node):
            if neighbor in unburned_nodes_set:
                nodes_dict[neighbor] += 1


                if nodes_dict[neighbor] >= 2:
                    if(change_colour):
                        G.nodes[neighbor]["state"] = "burned"
                    # burn the neighbor
                    nodes_dict[neighbor] = 2
                    unburned_nodes_set.remove(neighbor)
                    unburned_nodes_list.remove(neighbor)  # this takes O(n) time so bad you can fix with other data structures later todo
                    burned_nodes_set.add(neighbor)
                    next_todo.append(neighbor)
    return next_todo


def rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo, round, sequence):
    global best_round
    global best_sequence
    if(round >= best_round):
        return

    todo = burn(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, False)

    if len(unburned_nodes_set) == 0:
        if round < best_round:
            best_round = round
            best_sequence = sequence.copy()
            print("New best round :", best_round)
            print("Sequence :", best_sequence)
        return

    for i in range(len(unburned_nodes_list)):
        node_to_burn = unburned_nodes_list[i]     # backup
        burned_nodes_set_backup = burned_nodes_set.copy()
        unburned_nodes_set_backup = unburned_nodes_set.copy()
        unburned_nodes_list_backup = unburned_nodes_list.copy()
        nodes_dict_backup = nodes_dict.copy()
        sequence_backup = sequence.copy()
        todo_backup  = todo.copy()


            # burn the node
        nodes_dict[node_to_burn] = 2
        unburned_nodes_set.remove(node_to_burn)
        unburned_nodes_list.remove(node_to_burn)
        burned_nodes_set.add(node_to_burn)
        todo.append(node_to_burn)
        sequence.append(node_to_burn)

        if len(unburned_nodes_set) == 0:
            if round < best_round:
                best_round = round
                best_sequence = sequence.copy()
                print("New best round :", best_round)
                print("Sequence :", best_sequence)
            return

        rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo, round + 1, sequence)

        # restore
        burned_nodes_set = burned_nodes_set_backup
        unburned_nodes_set = unburned_nodes_set_backup
        unburned_nodes_list = unburned_nodes_list_backup
        nodes_dict = nodes_dict_backup
        sequence = sequence_backup
        todo = todo_backup


def draw_graph(G, pos):
    color_map = []
    for node in G.nodes:
        if G.nodes[node]["state"] == "burned":
            color_map.append("red")
        else:
            color_map.append("gray")

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=500)
    plt.show()


def play_sequence(G, sequence, pos, graph_size):
    todo = []
    unburned_nodes_list = [i for i in range(graph_size)]  # list of unburned nodes
    nodes_dict = {i: 0 for i in range(graph_size)}  # dict of unburned nodes
    unburned_nodes_set = {i for i in range(graph_size)}  # set of unburned nodes
    burned_nodes_set = set()

    for node in sequence:
        G.nodes[node]["state"] = "burned"
        todo = burn(G, todo, burned_nodes_set,unburned_nodes_set, unburned_nodes_list, nodes_dict, True)
        draw_graph(G, pos)

        todo.append(node)


if __name__ == "__main__":
    main()