import codecs

with codecs.open('ES.txt','r','utf8') as fic:
    for line in fic:
        print(line)
