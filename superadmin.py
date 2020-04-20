from socket import *
import json
from math import log2
from admin import Admin
import sys
from random import randint
from remote_player import RemotePlayer, RemotePlayerError

def single_elim(connections):
    '''

    with open("go.config") as json_file:
        server_info = json.load(json_file)

    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', server_info["port"]))
    server.listen()
    connections = []
    scores = {}

    while len(connections) < sys.argv[2]:
        connection, address = server.accept()
        connections.append(connection)

    idx = 1
    while log2(len(connections)) % 1 != 0:
        connections.append("Local Player " + str(idx))
        idx += 1
    '''
    ###################

    scores = {}
    print("Starting single elimination")
    round = 1
    while len(connections) > 1:
        new_connections = []
        for cxn in range(0, len(connections), 2):
            if not isinstance(connections[cxn], str):
                if not isinstance(connections[cxn + 1], str):
                    # Both players are remote
                    new_admin = Admin(connections[cxn:cxn+2])
                else:
                    # First player is remote and second player is local
                    new_admin = Admin([connections[cxn]], player2=connections[cxn+1])
            else:
                if not isinstance(connections[cxn+1], str):
                    # First player is local and second player is remote
                    new_admin = Admin(connections[cxn+1], player1=connections[cxn])
                else:
                    # Both players are local
                    new_admin = Admin(player1=connections[cxn], player2=connections[cxn+1])


            player1 = new_admin.player_holder[0].get_player_name()
            player2 = new_admin.player_holder[1].get_player_name()

            # Run game between two players
            print("Running game")
            winners = new_admin.run()

            if len(winners) == 2:
                # Tie, choose random winner with coin flip
                winner = winners[randint(0, 1)]
            else:
                if len(winners) == 3:
                    # Put cheating player at bottom of rankings
                    scores[winners[1]] = -1
                winner = winners[0]


            # Increment the total win score
            if winner in scores:
                scores[winner] += 1
            else:
                scores[winner] = 1

            if winner == player1:
                # Move winning player on to next round
                new_connections.append(connections[cxn])
                if player2 not in scores:
                    scores[player2] = 0
                if not isinstance(connections[cxn + 1], str):
                    # If losing player remote, close connection
                    connections[cxn + 1].close()
            else:
                if player1 not in scores:
                    scores[player1] = 0
                # Move winning player on to next round
                new_connections.append(connections[cxn + 1])
                if not isinstance(connections[cxn], str):
                    # If losing player remote, close connection
                    connections[cxn].close()
        connections = new_connections
        print(scores)
        round += 1

    reversed_scores = {}
    for n, s in scores.items():
        if s in reversed_scores:
            reversed_scores[s].append(n)
        else:
            reversed_scores[s] = [n]
    rankings = {}
    top = 1
    final_scores = sorted(list(reversed_scores.keys()), reverse=True)
    for key in final_scores:
        rankings[top] = [reversed_scores[key]]
        top += 1

    print("\nRANKINGS:\n")
    print(json.dumps(rankings))

    # for d in list(filter(lambda x: not isinstance(x, str)), connections)

def round_robin(connections):
    
    # TODO move server connection to beginning of main


    print("Starting round robin")
    num_players = len(connections)
    # Only fills the "top right" of the scoresheet
    score_holder = [[-1 for i in range(num_players)] for j in range(num_players)]

    names = []
    name_to_id = {}
    # Map each player name to a unique id
    # for i, player in enumerate(connections):
    #     if isinstance(player, str):
    #         names.append(player)
    #         name_to_id[player] = i
    #     else:
    #         names.append("Remote player")
            # temp_remote = RemotePlayer(player)
            # remote_name = temp_remote.get_name()
            # names.append(remote_name)
            # name_to_id[remote_name] = i
    
    for i in range(len(connections)-1):
        for j in range(i+1, len(connections)):
            player1 = connections[i]
            player2 = connections[j]
            print("Player " + str(i) + " VS " + str(j))
            if not isinstance(player1, str):
                if not isinstance(player2, str):
                    new_admin = Admin([player1, player2])
                else:
                    new_admin = Admin([player1], player2=player2)
            else:
                if not isinstance(player2, str):
                    new_admin = Admin([player2], player1=player1)
                else:
                    new_admin = Admin(player1=player1, player2=player2)
            print("Admin made")
            for k, plyr in enumerate(new_admin.player_holder):
                name = plyr.get_player_name()
                if name not in names:
                    names.append(name)
                    if k == 0:
                        name_to_id[name] = i
                    else:
                        name_to_id[name] = j

            print(names)
            print(name_to_id)

            winner = new_admin.run()

            print(winner)

            if len(winner) == 3:
                # Cheating was detected
                winner_id = name_to_id[winner[0]]
                cheater_id = name_to_id[winner[1]]
                cheater_name = winner[1]
                print("Cheater: " + cheater_name)

                # If player 2 was the cheater:
                if winner_id == i:
                    score_holder[winner_id][cheater_id] = 1
                    score_holder[cheater_id][winner_id] = 0
                    for m, row in enumerate(score_holder):
                        if row[cheater_id] == 0:
                            row[cheater_id] = 1
                            score_holder[cheater_id][m] = 0
                else:
                    # Player 1 was the cheater
                    score_holder[cheater_id][winner_id] = 0
                    score_holder[winner_id][cheater_id] = 1
                    for k, score in enumerate(score_holder[cheater_id]):
                        if score == 1:
                            score_holder[cheater_id][k] = 0
                            score_holder[k][cheater_id] = 1
                
                # replacing connection with name string will cause it to be replaced with def player
                if not isinstance(connections[cheater_id], str):
                    connections[cheater_id].close()
                connections[cheater_id] = cheater_name

                
            elif len(winner) == 2:
                # Tie: flip a coin
                coin = randint(0,1)
                if coin:
                    score_holder[i][j] = 1
                    score_holder[j][i] = 0
                else:
                    score_holder[i][j] = 0
                    score_holder[j][i] = 1

            else:
                winner_id = name_to_id[winner[0]]
                if winner_id == i:
                    score_holder[i][j] = 1
                    score_holder[j][i] = 0
                else:
                    score_holder[i][j] = 0
                    score_holder[j][i] = 1

    # Set all -1 to 0
    for i, row in enumerate(score_holder):
        for j, score in enumerate(row):
            if score == -1:
                score_holder[i][j] = 0

    # Tally scores
    final_score = [0 for i in range(len(connections))]

    # For each player:
    for i, player in enumerate(score_holder):
        # add up all wins in the player's row
        for score in player:
            final_score[i] += score
        # add up all wins in the column
        # for j, row in enumerate(score_hoolder):
        #     final_score[i] += row[i]

    # print(final_score)
    rankings = {}
    place = 0
    prev_max = max(final_score) + 1
    while any([score >= 0 for score in final_score]):
        if max(final_score) != prev_max:
            place += 1
            rankings[place] = [names[final_score.index(max(final_score))]]
        else:
            rankings[place].append(names[final_score.index(max(final_score))])
        prev_max = max(final_score)
        final_score[final_score.index(max(final_score))] = -1

    for cxn in connections:
        if not isinstance(cxn, str):
            cxn.close()

    print("\nRANKINGS:\n")
    print(json.dumps(rankings))



    

if __name__ == "__main__":
    with open("go.config") as json_file:
        server_info = json.load(json_file)

    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind(('', server_info["port"]))
    server.listen()
    connections = []

    print(sys.argv[0])
    print(sys.argv[1])
    print(sys.argv[2])

    while len(connections) < int(sys.argv[2]):
        connection, address = server.accept()
        connections.append(connection)

    idx = 1
    while log2(len(connections)) % 1 != 0:
        connections.append("Local Player " + str(idx))
        idx += 1

    if sys.argv[1] == "--cup":
        single_elim(connections)
    
    
    elif sys.argv[1] == "--league":
        round_robin(connections)

    server.close()

