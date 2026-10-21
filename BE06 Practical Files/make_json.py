import random
import json


def generate_dummy_data():
    towns = [
        'Coleraine', 'Banbridge', 'Belfast',
        'Lisburn', 'Ballymena', 'Derry',
        'Newry', 'Enniskillen', 'Omagh',
        'Ballymoney'
    ]

    business_list = []

    for i in range(100):
        name = "Biz " + str(i)
        town = random.choice(towns)
        rating = random.randint(1, 5)

        business_list.append({
            "name": name,
            "town": town,
            "rating": rating,
            "reviews": []
        })

    return business_list


businesses = generate_dummy_data()

with open("data.json", "w") as fout:
    json.dump(businesses, fout, indent=4)

print("Successfully generated 100 businesses in data.json")