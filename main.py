import re
import lxml
import requests
import numpy as np
import networkx as nx
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from TextRank4Keyword import TextRank4Keyword


def findURL(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
    movieURLs = ['https://' + url.split('/')[2] + link for link in links]
    return movieURLs


def findStoryline(movieURLs):
    storylines = []
    i = 0;

    for url in movieURLs:
        print(i)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        storylineContent = soup.find("div", class_="inline canwrap")
        storylines.append(storylineContent.find("span").text)
        i = i + 1

    return storylines


def findKeywords(storylines):
    keywords = {}
    i = 0
    for storyline in storylines:
        tr4w = TextRank4Keyword()
        tr4w.analyze(storyline, candidate_pos=['NOUN', 'PROPN'], window_size=4, lower=False)
        keywords[i] = tr4w.get_keywords(20)
        i = i + 1

    return keywords


def createGraph(keywords):
    graph = nx.Graph()
    for movieI in keywords:
        for movieJ in keywords:
            if movieI != movieJ:
                weight = 0
                for keywordI in keywords[movieI]:
                    for keywordJ in keywords[movieJ]:
                        if keywordI == keywordJ:
                            weight = weight + 1
                graph.add_edge(movieI, movieJ, weight=weight)

    return graph


def writeFile(graph):
    array = nx.to_numpy_array(graph)
    f = open("graph.txt", "w")
    for i in range(250):
        for j in range(250):
            if array[i][j] != 0:
                text = ""
                text = str(i) + " " + str(j) + " " + " " + str(array[i][j]) + "\n"
                f.write(text)
    f.close()


if __name__ == '__main__':
    url = 'http://www.imdb.com/chart/top'
    movieURLs = findURL(url)
    storylines = findStoryline(movieURLs)
    keywords = findKeywords(storylines)
    graph = createGraph(keywords)
    nx.draw(graph)
    plt.show()
    writeFile(graph)
