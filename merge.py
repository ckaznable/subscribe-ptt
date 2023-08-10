import json
import os

def find(last, board, condition):
    for data in last:
        if data[0] == board and data[2] == condition:
            return data

def main():
    if not os.path.isfile("queue"):
        return None

    last = []
    queue = []
    new = []
    if os.path.isfile("last_status"):
        with open("last_status", "r") as f:
            last = json.load(f)

    with open("queue", "r") as f:
        queue = json.load(f)

    for q in queue:
        data = find(last, q[0], q[1])
        if data != None:
            new.append(data)
        else:
            new.append([q[0], 0, q[1]])

    with open("last_status", "w") as f:
        json.dump(new, f)

if __name__ == "__main__":
    main()
