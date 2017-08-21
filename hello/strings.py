dicts = [
    {'name': 'Michelangelo',
     'food': 'PIZZA'},
    {'name': 'Garfield',
     'food': 'lasanga'},
    {'name': 'Walter',
     'food': 'pancakes'},
    {'name': 'Galactus',
     'food': 'worlds'}
]

sentence = "Hi, I'm %s and I love to eat %s!"


def string_factory(dicts, sentence):
    string = []
    for item in dicts:
        iv = item.values()
        index=0
        for v  in iv:
            string.append(v)
            index+=index

        print(sentence%(string[0],string[1]))


string_factory(dicts, sentence)
