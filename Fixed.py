import networkx as nx
import matplotlib.pyplot as plt

best_round = 9999999
best_sequence = []
graph_x_dim = 5
graph_y_dim = 5
graph_size = graph_x_dim*graph_y_dim
list_of_best_sequences = []


def main():

    todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set = graph_setup()

    G = nx.grid_2d_graph(graph_x_dim, graph_y_dim)  # create a grid graph
    G = nx.convert_node_labels_to_integers(G)  # relabel nodes to

  #  G = nx.erdos_renyi_graph(graph_size, 0.1, seed=432)
    nx.set_node_attributes(G, "unburned", "state")

    pos = nx.spring_layout(G)

    pos = nx.bfs_layout(G,0)    # use this layout for grids

    draw_graph(G, pos)

    rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, [], 1,[])

    ## For perimeter testing
    #todo, unburned_nodes_list, unburned_nodes_set, nodes_dict, burned_nodes_set = burn_sequence(G, get_diagonal_sequence())

    #rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo, len(get_diagonal_sequence())+1, get_diagonal_sequence(), True, get_perimiter())


    print("Best round:", best_round)
    print("Best sequence:", best_sequence)
    print("Number of best sequences:", len(list_of_best_sequences))
    #print("Best sequences:", list_of_best_sequences)

    diagonal_sequence = get_diagonal_sequence()

    #11x11 sequences
    r_19_11_11 = diagonal_sequence+ [76,115, 54, 113, 32, 110, 10]

    addition_sequence = diagonal_sequence+ [76,115, 43, 112, 10, 110]

   # play_sequence(G,addition_sequence, pos, graph_size, True)

    play_sequence(G, list_of_best_sequences[1], pos, True)

def get_perimiter():         # Only works for x and y the same
    perimiter = []            # todo change to set maybe if you really don't need list cannot be asked right now
    for i in range(graph_x_dim):
        perimiter.append(i)
        perimiter.append(graph_size-i-1)

    for i in range(1, graph_x_dim-1):
        perimiter.append(i*graph_x_dim) ## add the left bottom row
        perimiter.append(i*graph_x_dim+graph_x_dim-1)  ## adds the top left row


    return set(perimiter)

def get_diagonal_sequence():
    diagonal_sequence = []
    for i in range(graph_x_dim):
        diagonal_sequence.append(i*(graph_x_dim+1))
    return diagonal_sequence

def graph_setup():
    todo = []
    unburned_nodes_list = [i for i in range(graph_size)]  # list of unburned nodes
    nodes_dict = {i: 0 for i in range(graph_size)}  # dict of unburned nodes
    unburned_nodes_set = {i for i in range(graph_size)}  # set of unburned nodes
    burned_nodes_set = set()

    return todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set

def burn_sequence(G, sequence):
    rounds = 0

    todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set = graph_setup()

    for node in sequence:
        rounds = rounds + 1

      #  G.nodes[node]["state"] = "burned"
        burned_nodes_set.add(node)
        unburned_nodes_list.remove(node)
        unburned_nodes_set.remove(node)
        nodes_dict[node] = 2

        todo = burn(G, todo, burned_nodes_set,unburned_nodes_set, unburned_nodes_list, nodes_dict, False)

        todo.append(node)

    return todo, unburned_nodes_list, unburned_nodes_set, nodes_dict, burned_nodes_set

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


def rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo, round, sequence, node_pick_contraint=False, node_pick_set=None):
    if node_pick_set is None:
        node_pick_set = []

    global list_of_best_sequences
    global best_round


    if(round > best_round):              # Make this equel for faster speed but will only get one result
        return

    todo = burn(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, False)

    if len(unburned_nodes_set) == 0:
        if round <= best_round:
            if(round == best_round):
                list_of_best_sequences.append(sequence.copy())
            else:
                list_of_best_sequences = [[]]
                best_round = round
                list_of_best_sequences.append(sequence.copy())
                print(len(list_of_best_sequences))
                print("New best round :", best_round)
                print("Sequence :", sequence)
        return

    for i in range(len(unburned_nodes_list)):

        if(node_pick_contraint):
            if(unburned_nodes_list[i] not in node_pick_set):
                print(unburned_nodes_list[i], " not in node_pick_set")
                continue

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
            if round <= best_round:
                if (round == best_round):
                    list_of_best_sequences.append(sequence.copy())
                else:
                    list_of_best_sequences = [[]]
                    best_round = round
                    list_of_best_sequences.append(sequence.copy())
                    print(len(list_of_best_sequences))
                    print("New best round :", best_round)
                    print("Sequence :", sequence)
            return

        if (round == 1):
            print("working on: ", node_to_burn)

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


def play_sequence(G, sequence, pos, play_till_burned):
    rounds = 0

    todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set = graph_setup()
    nx.set_node_attributes(G, "unburned", "state")

    for node in sequence:
        rounds = rounds + 1

        G.nodes[node]["state"] = "burned"
        burned_nodes_set.add(node)
        unburned_nodes_list.remove(node)
        unburned_nodes_set.remove(node)
        nodes_dict[node] = 2


        todo = burn(G, todo, burned_nodes_set,unburned_nodes_set, unburned_nodes_list, nodes_dict, True)
        draw_graph(G, pos)

        todo.append(node)
    print("Sequence ended after: ", rounds, " rounds")


    if(play_till_burned):
        while(len(unburned_nodes_set) != 0):
            print(unburned_nodes_list)
            rounds = rounds + 1
            todo = burn(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, True)
            draw_graph(G, pos)

    print("Simulation ended after: ", rounds, " rounds")


if __name__ == "__main__":
    main()