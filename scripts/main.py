import json

import requests


def main():
    USER_NAME = 'dilmnqvovpnmlib'
    REPOSITORY_NAME = 'hakiwata'
    API_URL = 'https://api.github.com/repos/{}/{}/contents/content/post/20210830'.format(
        USER_NAME,
        REPOSITORY_NAME,
    )
    REPOSITORY_BASE_URL = 'https://github.com/{}/{}/blob/main/'.format(
        USER_NAME,
        REPOSITORY_NAME,
    )

    res = requests.get(API_URL)
    res_json = json.loads(res.text)
    latest_data = {
        'name': res_json[-1]['name'],
        'path': REPOSITORY_BASE_URL + res_json[-1]['path'],
    }
    return latest_data


if __name__ == '__main__':
    print(main())
