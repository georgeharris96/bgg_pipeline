# src/utils/api_auth.py


def get_bgg_auth():
    with open("bgg_auth.txt", "r") as file:
        return file.readline()
    