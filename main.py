import json
import PyPtt
import os
from dotenv import dotenv_values

class LastStatus:
    def __init__(self):
        self.data = []

        if not os.path.isfile("last_status"):
            with open("last_status", "w") as f:
                json.dump(self.data, f)

        with open("last_status", "r") as f:
            self.data = json.load(f)

    def save(self):
        with open("last_status", "w") as f:
            json.dump(self.data, f)

    def set(self, id, value):
        obj = self.find(id)
        if obj != None:
            index, _ = obj
            self.data[index][1] = value
        else:
            self.data.append([id, value])

    def get(self, id):
        obj = self.find(id)
        if obj != None:
            _, data = obj
            return data
        return None

    def find(self, id):
        for (i, x) in enumerate(self.data):
            if x[0] == id:
                return (i, x[1])
        return None

def get_board_list(env):
    return env.split(',')

def get_post(ptt, board, limit=10, index=0):
    newest_index = ptt.get_newest_index(PyPtt.NewIndex.BOARD, board)
    if index >= newest_index:
        return []

    newest_range = limit
    newest_count = 0

    posts = []

    while newest_count < newest_range:
        cur_index = newest_index - newest_count
        newest_count += 1
        post = ptt.get_post(board, index=cur_index)

        if not post:
            continue

        if post["post_status"] != PyPtt.PostStatus.EXISTS:
            continue

        if not post["pass_format_check"]:
            continue

        if not post['content']:
            continue

        posts.append(post)

    return posts

def extract_post(post):
    return (post["title"], post["index"])

def extract_posts(posts):
    return list(map(extract_post, posts))

if __name__ == "__main__":
    config = dotenv_values(".env")
    boards = get_board_list(config.get("boards"))
    ptt = PyPtt.API()
    status = LastStatus()
    posts = []

    try:
        ptt.login(config.get("username"), config.get("pw"))

        for board in boards:
            # try:
            print("Getting posts from " + board)

            index = status.get(board)
            if index == None:
                index = 0

            posts = extract_posts(get_post(ptt, board, index=index))

            if len(posts) > 0:
                status.set(board, posts[0][1])

        print(status.data)
        print(posts)

    finally:
        ptt.logout()
        status.save()
