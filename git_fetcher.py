import json
import requests
from datetime import datetime
from functools import reduce
from tqdm import tqdm
from time import sleep

token = "your_token_here"
ORG_NAME = "your_org_name_here"
ANY_REPO_NAME = "any_repo_name_in_your_org"

url1 = f"https://api.github.com/orgs/{ORG_NAME}/repos?per_page=100&page=1"
url2 = f"https://api.github.com/orgs/{ORG_NAME}/repos?per_page=100&page=2"

headers = {
    'Authorization': 'token ' + token,
    'Accept': 'application/vnd.github.v3+json',
}


# copy from browser
contributors_headers = {
    "accept": 'application/json',
    "Accept-Encoding": 'gzip, deflate, br',
    "Accept-Language": 'en-US,en;q=0.9,hi-IN;q=0.8,hi;q=0.7',
    "Cache-Control": 'no-cache',
    "Connection": 'keep-alive',
    'Cookie': '_octo=GH1.1.506912823.1566269566; _ga=GA1.2.288181271.1566269567; _device_id=a61263cb656c2cdfbbe38638c6f8689c; user_session=34bY-inbfXS0hTAmkSw2gPZMXBdiHTBmFnho6AsMAa0xkNWc; __Host-user_session_same_site=34bY-inbfXS0hTAmkSw2gPZMXBdiHTBmFnho6AsMAa0xkNWc; dotcom_user=Pkoiralap; logged_in=yes; tz=America%2FChicago; has_recent_activity=1; _gh_sess=LHIBJlf2f5CdlQ7YAEWFtpF5HA8cMoUk4BUCN%2BULzafeFy3L1CmcX2hwYndmPV%2BoTclmPnnjZNLbxrvU9IsTH5SZbTCZbMQTfKycp7EY7jqDAkOEndyxw5iFC56ICbMU09imhiou3Ct8UDUO%2BHKm6c8%2FXKyuMwIGju0xSZJTGXhFhQFrjnnB6j4QUYL8%2FYo9FfPBJw8QWw%2FeWxul16NkR%2Bjfip7D0oAaHqK4eB95DU%2B0pHURV%2BxuLw9MiqulqdtA4%2Fv3Fg79OyYmYIHm2Z9UjrH4uiYZMA85G2LqtXvapfaO5VndZcgbH8sjRD5JjlIAR5SadDYS4o6qu3kDqVjEDrSoHc07a1ulUSbkzI8mC7x9W22kdfzxHqujPvChPdrBm9sBvIZzqHuXkI4%2FwfduXTY8G%2FExrFGJP9%2B%2Fsig1r%2Fh49YGPmkQsNFiMEfTH%2BhxqS3sADm7Lt3N%2B1ghZ%2Fc43a8GvDZxYJViG%2FkDtgQl9h1V%2Btb184s0gZQnkMTsMX4jp4KylKf6dmqBb6RNcsZnrdPKTa11KdlSDRMAzi%2FwuS726UhEjwi7GElBswsOy1WOqOxYmK9EnsnrNT0kTEU5qBKUB4el6Y6l5O4y1GHvBvffj6I7o%2Bj2HGOec40OfZlIewJKdJUtu%2Blfupd89AzNG2KPduoDvOvFM0x%2Br083BmZTw12GnRQEeGAy1T0LjzMrR1%2BSVIzHPTrcp8JP27%2Fgq9qN1PYxvkE8L4CQY7Q7iJdEnv%2FhDc4e1IM2fF3QCN4Q9lV17RKSY9YwUSET7RVNUWMjsx7ipEsjo52hqKbb9oWDQZionl%2BXEkNTnAIVOchJBS5VYEPQ581n%2F%2BNRjPUlSSNvrdK8K9Pln--coH1HADXQf11p9f0--sDn5KXxsm6EaUj9H0poGbg%3D%3D',
    "Host": 'github.com',
    "Pragma": 'no-cache',
    "Referer": f'https://github.com/{ORG_NAME}/{ANY_REPO_NAME}/graphs/contributors',
    "sec-ch-ua": '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    "sec-ch-ua-mobile": '?0',
    "Sec-Fetch-Dest": 'empty',
    "Sec-Fetch-Mode": 'cors',
    "Sec-Fetch-Site": 'same-origin',
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    "X-Requested-With": 'XMLHttpRequest'
}


def save_all_repos():
    val1 = requests.get(url1, headers=headers).text
    val2 = requests.get(url2, headers=headers).text

    all_repo = json.loads(val1) + json.loads(val2)
    json.dump(all_repo, open("all_repos.json", "w"))


min_timestamp = datetime(2020, 1, 1).timestamp()


def reduce_func(acc, week):
    if (week["w"] < min_timestamp):
        return acc
    else:
        return {
            "a": acc["a"] + week["a"],
            "d": acc["d"] + week["d"],
            "c": acc["c"] + week["c"],
        }


def save_contributors(continue_from=0, sleep_time=10):
    with open("all_repos.json") as in_file:
        all_repos = json.load(in_file)

    count = continue_from

    for repo in tqdm(all_repos[continue_from:]):
        if repo["fork"]:
            continue
        try:
            url = f"https://github.com/{ORG_NAME}/{{}}/graphs/contributors-data".format(repo["name"])
            contributors_headers["Referer"] = f'https://github.com/{ORG_NAME}/{{}}/graphs/contributors'.format(repo["name"])

            sleep(sleep_time)

            contributors = requests.get(url, headers=contributors_headers).text
            contributors = json.loads(contributors)
            contributors = sorted(contributors, key=lambda x: x["total"])
            for con in contributors:
                con["weeks"] = reduce(reduce_func, con["weeks"])

            name = repo["name"]
            print("success for repo name:" + name)
            json.dump(contributors, open(f"contributions/contrubutions-{name}.json", "w"), indent=4)

            count += 1
        except Exception:
            print("Exception for repo name:" + repo["name"])
            print("BREAKING")

            print("CONTINUE FROM ", count)
            break

        sleep(sleep_time)


save_all_repos()
save_contributors(82, 5)
