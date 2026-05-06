import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

best_round = 9999999
best_sequence = []
graph_x_dim = 10
graph_y_dim = 10
#graph_size = graph_x_dim*graph_y_dim
graph_size = 11

list_of_best_sequences = []


def main():
    #tree_setup()
    #petersen_setup()
    f_tree_setup()



def f_tree_setup():
    trees = trees_no_deg2(graph_size)
    for i in range(3):
        tree = trees[i]
        leaves = sum(1 for v in tree.nodes if tree.degree(v) == 1)
        solving_sequence = tree_solver(tree)
        print("Solving sequence:", solving_sequence)
        nx.set_node_attributes(tree, "unburned", "state")
        #draw_graph(tree, nx.spring_layout(tree))
        if(len(solving_sequence) == leaves):
            play_sequence(tree, solving_sequence, nx.spring_layout(tree), True)



def count_leaves(G):
    """Return the number of leaves (degree-1 vertices) in graph G."""
    return sum(1 for v in G.nodes if G.degree(v) == 1)

def closest_cherry(G, start, burned_nodes_set):
    """
    Returns the closest cherry to 'start' in tree G.
    A cherry = two leaves sharing the same neighbor.

    Output: (leaf1, leaf2)
    or None if no cherry exists.
    """
    visited = set([start])
    queue = deque([start])

    while queue:
        v = queue.popleft()
        # Check if v is the center of a cherry
        leaf_neighbors = [u for u in G.neighbors(v) if G.degree(u) == 1]

        if len(leaf_neighbors) >= 2 and v is not burned_nodes_set and all(u not in burned_nodes_set for u in leaf_neighbors):
            # Return any pair of leaves (first two)
            return [leaf_neighbors[0], leaf_neighbors[1]]

        # Continue BFS
        for u in G.neighbors(v):
            if u not in visited:
                visited.add(u)
                queue.append(u)

    return None


def trees_no_deg2(n):
    return [
        T for T in nx.nonisomorphic_trees(n)
        if all(deg != 2 for _, deg in T.degree())
    ]

# Given a graph G the algorithm works as follows:
# 1. Pick a random cherry
# 2. Burn the cherry
# Now in loop:
# If a new vertex has been burned via spread (we did not pick) -> check if there is a leaf in distance 2. That has not been burned.
def tree_solver(G):
    sequence = []
    todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set = graph_setup()
    to_burn = closest_cherry(G, 0, burned_nodes_set)
    print(to_burn)
    sequence.append(to_burn[0])
    sequence.append(to_burn[1])
    burn_one_vertex(G, to_burn[0],burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo)
    burn_one_vertex(G, to_burn[1],burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo)
    the_cherry_dad = list(G[to_burn[0]])[0]
    print("The dad is:", the_cherry_dad)


    todo = burn(G,to_burn, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, False)  # todo tells us new events

    todo = burn_flamable_path(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, sequence)


    cherry = closest_cherry(G, todo[0], burned_nodes_set)
    if(cherry is None):                # no more cherries
        unburned_nodes_set_copy = unburned_nodes_set.copy()
        for vertex in unburned_nodes_set_copy:
            if(G.degree(vertex) == 1):
                burn_one_vertex(G,vertex,burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo)
                todo = burn(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict,False)# todo tells us new events
                sequence.append(vertex)

    if(len(unburned_nodes_set) > 0):
        print("Did not burn everything!! Missing: ", unburned_nodes_set)

    # Either the cherry dad has a connection to an innver vertexsome if not we should be done
    return sequence



def burn_flamable_path(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, sequence):
    to_follow = deque()
    for vertex in todo:
        to_follow.extend(leaf_in_dist2(G, vertex, burned_nodes_set))

    while(to_follow):
        leaf = to_follow.popleft()
        if(leaf not in burned_nodes_set)and(list(G[leaf])[0] not in burned_nodes_set):
            sequence.append(leaf)
            burn_one_vertex(G, leaf, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo)
            todo = burn(G, todo, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, False)

            for vertex in todo:
                to_follow.extend(leaf_in_dist2(G, vertex, burned_nodes_set))

    return todo


# only returns one!
def leaf_in_dist2(G, node, burned_nodes_set):
    leaves = []
    for neighbor in G.neighbors(node):
        if neighbor not in burned_nodes_set:
            for neighbor_neighbor in G.neighbors(neighbor):
                if neighbor_neighbor not in burned_nodes_set:
                    if G.degree(neighbor_neighbor) == 1:
                        leaves.append(neighbor_neighbor)
    return leaves

def burn_one_vertex(G, node_to_burn,burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo):
    nodes_dict[node_to_burn] = 2
    unburned_nodes_set.remove(node_to_burn)
    unburned_nodes_list.remove(node_to_burn)
    burned_nodes_set.add(node_to_burn)
    todo.append(node_to_burn)


def petersen_setup():
    global list_of_best_sequences
    global best_round

    todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set = graph_setup()
    G = nx.petersen_graph()
    nx.set_node_attributes(G, "unburned", "state")
    pos = nx.spring_layout(G)
    draw_graph(G, pos)

    rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo, 1, [])
    print("Number of best sequences:", len(list_of_best_sequences))
    print("First best sequence:", list_of_best_sequences[1])
    print("best sequences", list_of_best_sequences)


def tree_setup():
    global list_of_best_sequences
    global best_round
    matching_found = True
    for r in range(1):
        matching_found = False

        todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set = graph_setup()
        G = nx.random_labeled_tree(graph_size)
        nx.set_node_attributes(G, "unburned", "state")
        pos = nx.spring_layout(G)
        draw_graph(G, pos)
        leaf_nodes = get_leaf_nodes(G)

        rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo, 1,[])


       # print("Best round:", best_round)
        #print("Best sequence:", best_sequence)
        print("Number of best sequences:", len(list_of_best_sequences))
        print("First best sequence:", list_of_best_sequences[1])
        print("leaf nodes", leaf_nodes)
        print("number of leafs:", len(leaf_nodes))
        print("best sequences", list_of_best_sequences)

        for sequence in list_of_best_sequences:
            matching = True
            for i in range(len(leaf_nodes)):
                if(sequence[i] not in leaf_nodes):
                    matching = False
                    #print("false:", sequence[i])
                    break
            if(matching == True):
                matching_found = True
                print("all good!")
                break


        list_of_best_sequences = []
        best_round = 999

        # if(matching_found == False):
        #     draw_graph(G, pos)



    #play_sequence(G, list_of_best_sequences[0], pos, True)


def cube_setup():
    todo, unburned_nodes_list, nodes_dict, unburned_nodes_set, burned_nodes_set = graph_setup()

    G = nx.grid_2d_graph(graph_x_dim, graph_y_dim)  # create a grid graph
    G = nx.convert_node_labels_to_integers(G)  # relabel nodes to

    #  G = nx.erdos_renyi_graph(graph_size, 0.1, seed=432)
    nx.set_node_attributes(G, "unburned", "state")

    pos = nx.spring_layout(G)

    pos = nx.bfs_layout(G, 0)  # use this layout for grids

    draw_graph(G, pos)

    # rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, [], 1,[])

    ## For perimeter testing
    # todo, unburned_nodes_list, unburned_nodes_set, nodes_dict, burned_nodes_set = burn_sequence(G, get_diagonal_sequence())

    # rec_solve(G, burned_nodes_set, unburned_nodes_set, unburned_nodes_list, nodes_dict, todo, len(get_diagonal_sequence())+1, get_diagonal_sequence(), True, get_perimiter())

    print("Best round:", best_round)
    print("Best sequence:", best_sequence)
    print("Number of best sequences:", len(list_of_best_sequences))
    # print("Best sequences:", list_of_best_sequences)

    diagonal_sequence = get_diagonal_sequence()

    # 11x11 sequences
    r_19_11_11 = diagonal_sequence + [76, 115, 54, 113, 32, 110, 10]

    addition_sequence = diagonal_sequence + [76, 115, 43, 112, 10, 110]
    seq = [65, 78, 52, 91, 39, 104, 26, 117, 13, 130, 0, 143]

    # play_sequence(G,addition_sequence, pos, graph_size, True)

    # play_sequence(G, list_of_best_sequences[1], pos, True)
    play_sequence(G, seq, pos, True)


def get_leaf_nodes(G):
    leaf_nodes = []
    for g in G.nodes:
        if(len(list(G.neighbors(g))) == 1):
            leaf_nodes.append(g)

    return leaf_nodes


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
                list_of_best_sequences = []
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
                    list_of_best_sequences = []
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
    nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=700)
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