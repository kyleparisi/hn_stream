import json
from time import sleep

import requests
import os

slack_url = os.environ.get("SLACK_URL")
search_terms = os.environ.get("SEARCH_TERMS").split(",")


def headers():
    return {
        "User-Agent": "kyleparisi/hn_stream.git",
    }


def get_item(item: str) -> str:
    response = requests.get(
        f"https://hacker-news.firebaseio.com/v0/item/{item}.json", headers=headers()
    )
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.text


def search_item_found(item: str) -> bool:
    for s in search_terms:
        if s in item:
            return True
    return False


def make_link(item: str):
    payload = json.loads(item)
    return f"HN Mention: [{payload['title']}](https://news.ycombinator.com/item?id={payload['id']})"


def send_slack(link):
    data = {"text": link}
    response = requests.post(
        slack_url, json=data, headers={"Content-type": "application/json"}
    )
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def get_max_item() -> str:
    response = requests.get(
        "https://hacker-news.firebaseio.com/v0/maxitem.json?print=pretty",
        headers=headers(),
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    return response.text.strip().replace("\n", "")


def backfill(current: int, backfill: int):
    assert current >= backfill
    # ensure not going back too far
    max_backfill = max(backfill, current - 100)
    while current >= max_backfill:
        item = get_item(str(current))
        current -= 1
        found = search_item_found(item)
        if found:
            print(item)
            print("send slack!")
            link = make_link(item)
            send_slack(link)


def main():
    fd = False
    content = get_max_item()

    # setup .id file
    try:
        fd = open(".id", "r")
    except FileNotFoundError:
        writer = open(".id", "w")
        print(f"max item: {content}")
        writer.write(content)
        writer.close()
    if not fd:
        fd = open(".id", "r")

    file_content = fd.read()
    fd.close()

    # sometimes you write the file wrong (didn't close or flush), so just write it again
    if file_content == "":
        writer = open(".id", "w")
        writer.write(content)
        writer.close()

    # run startup back fill
    content_int = int(content)
    backfill_int = content_int - 100
    print("run first back fill")
    backfill(current=content_int, backfill=backfill_int)

    # read and search, record the pointer we've read till
    fd = open(".id", "r+")
    current = fd.read()
    current_int = int(current)
    while True:
        content = get_max_item()
        content_int = int(content)
        if current_int >= content_int:
            print("all caught up")
            sleep(30)
            continue
        backfill(current=content_int, backfill=current_int)
        # we have back filled, let's continue from here
        print(f"new max: {content}")
        current_int = content_int
        fd.truncate(0)
        fd.seek(0)
        fd.write(content)
        fd.flush()
        sleep(30)

    fd.close()


if __name__ == "__main__":
    main()
