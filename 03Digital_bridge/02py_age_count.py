import re
import json
import requests
url = 'https://coderbyte.com/api/challenges/json/age-counting'

def fetch_age_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response

def age_count():
    datas = fetch_age_data(url)
    data = datas.json()["data"]
    # print(data)
    age_data = re.findall(r"age=(\d+)", data)
    ages = [int(age) for age in age_data]
    # print(ages)
    counts = 0
    for age in ages:
        if age >= 50:
            counts += 1
    return counts

data = {"name": "Sagor", "age": 25, "name": "Raju", "age": 55, "name": "Kalam", "age": 62}
print("Result" , age_count())