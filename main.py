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
        else:
            with open("last_status", "r") as f:
                self.data = json.load(f)

    def get_boards_list(self):
        list = []
        for board in self.data:
            list.append(board[0])
        return list

    def save(self):
        with open("last_status", "w") as f:
            json.dump(self.data, f)

    def set(self, id, value, condition):
        data = [id, value, condition]
        obj = self.find(id)
        if obj != None:
            _, index, _ = obj
            self.data[index] = data
        else:
            self.data.append(data)

    def get(self, id):
        obj = self.find(id)
        if obj != None:
            _, index, condition = obj
            return (index, condition)
        return None

    def find(self, id):
        for (i, x) in enumerate(self.data):
            if x[0] == id:
                return (i, x[1], x[2])
        return None

def get_post(ptt, board, limit=10, index=0, condition=None):
    newest_index = ptt.get_newest_index(PyPtt.NewIndex.BOARD, board, search_condition=condition, search_type=PyPtt.SearchType.KEYWORD)
    if index >= newest_index:
        return []

    newest_range = limit
    newest_count = 0

    posts = []

    while newest_count < newest_range:
        cur_index = newest_index - newest_count
        newest_count += 1

        if index >= cur_index:
            continue

        post = ptt.get_post(board, index=cur_index, search_condition=condition, search_type=PyPtt.SearchType.KEYWORD)

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
    return (post["aid"], post["title"], post["index"])

def extract_posts(posts):
    return list(map(extract_post, posts))

def process(posts):
    print(posts)

if __name__ == "__main__":
    config = dotenv_values(".env")
    status = LastStatus()
    boards = status.get_boards_list()
    ptt = PyPtt.API()
    posts = []

    try:
        ptt.login(config.get("username"), config.get("pw"))

        for board in boards:
            print("Getting posts from " + board)

            index = 0
            condition = None
            s = status.get(board)
            if s != None:
                index = s[0]
                condition = s[1]

            posts = extract_posts(get_post(ptt, board, index=index, condition=condition))

            if len(posts) > 0:
                status.set(board, posts[0][2], condition)

        process(posts)

    finally:
        ptt.logout()
        status.save()
