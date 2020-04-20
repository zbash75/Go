import typedefs
from jsonparser import read_json, output_to_json
from socket import *
import json

BUFFER_SIZE = 65536

error_msg = "GO has gone crazy!"

orig_commands = read_json()
commands = output_to_json(orig_commands)
# print(type(commands))
outputs = []

with open("go.config") as json_file:
    server_info = json.load(json_file)

client = socket(AF_INET, SOCK_STREAM)
client.connect((server_info["IP"], server_info["port"]))
# client.send(char_len.encode())
client.sendall(commands.encode())

if len(orig_commands) < 3:
    while len(outputs) < len(orig_commands):
        output = client.recv(4096).decode()
        outputs.append(output)
        if output == error_msg:
            break
else:
    while len(outputs) < len(orig_commands) - 1:
        output = client.recv(4096).decode()
        outputs.append(output)
        if output == error_msg:
            break
client.close()
# for idx, command in enumerate(commands):
#     if idx == 0:
#         if command != ["register"]:
#             output = error_msg
#     elif idx == 1:
#         if command[0] != "receive-stones":
#             output = error_msg
#     else:
#         if command[0] != "make-a-move":
#             output = error_msg
#         else:
#             client.send(command.encode())
#             output = client.recv(4096)
#         outputs.append(output)
#         if output == error_msg:
#             client.close()
#             break
    # if command == ['register']:
    #     outputs.append('no name')
    # elif command[0] == 'receive-stones':
    #     player.set_stone(command[1])
    # else:
    #     move_made = player.play(command[1])
    #     if type(move_made) is tuple:
    #         move_made = typedefs.point_to_string(move_made)
    #     outputs.append(move_made)
# print("done")
# for output in outputs:
#     print(output)
# print("json")
print(output_to_json(outputs))