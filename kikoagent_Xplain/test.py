# import requests
# from bs4 import BeautifulSoup
# import numpy
#
# word = 'Sun'
# response = requests.get(
#     'https://www.rhymezone.com/r/rhyme.cgi?Word=' + word + '&typeofrhyme=perfect').text
#
# soup = BeautifulSoup(response)
# rhymes = []
# for a in soup.find_all('a'):
#     if a.get('class') is not None:
#         rhymes.append(a.get_text().replace(u'\xa0', u' '))
# rhymes = numpy.array(rhymes)
#
# sentense = word + ' rhymes with ' \
#            +  rhymes[numpy.random.choice(len(rhymes), 1)][0] \
#            + ', ' + str(rhymes[numpy.random.choice(len(rhymes), 1)][0]) \
#            + ', and ' + str(rhymes[numpy.random.choice(len(rhymes), 1)][0]) + '.'
#
# print(sentense)

test = 'test'
print(test)