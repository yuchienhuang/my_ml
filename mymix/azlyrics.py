import numpy as np
import urllib3
from bs4 import BeautifulSoup
from mymix.utils import *
from time import sleep



http = urllib3.PoolManager()


  

def lyrics_string(lyrics_url):
    
    def soup(url):
        response = http.request('GET', url)
        return BeautifulSoup(response.data)

    return soup(lyrics_url).findAll('div',attrs={'class': None})[1].text


def search_box(song,page_number):

    p_link = "https://search.azlyrics.com/search.php?q=" + song + "&w=songs&p=" + str(page_number)
    print(p_link)
    response = http.request('GET', p_link)
    soup = BeautifulSoup(response.data)
    box = soup.findAll("td", {"class": "text-left visitedlyr"})
    text = []
    for td in box:
        bs = td.findAll('b')
        for b in bs:
                text.append(b.text.strip().lower())
        link = td.find('a',href=True)
        text.append(link.get('href'))
           
    data = np.array(text).reshape(-1,3)
    
    labels = []
    for i, s in enumerate(data[:,0]):
        if remove_comments(s)==song.lower():
            labels.append(i)
    

    return data[labels]

def all_versions(track_name,track_artistname):

    

    data = search_results(track_name)
    
    try:

    
        if track_artistname.lower() in data[:,1]:
            url = data[:,2][list(data[:,1]).index(track_artistname.lower())]        
            print(url)
            the_lyrics = lyrics_string(url)
    
    
            similarities = []
            for i, link in enumerate(data[:,2]):
                similarity = get_jaccard_sim(the_lyrics,lyrics_string(link))
                sleep(1)
                print('hello')
                similarities.append(similarity)
                
            similarities = np.array(similarities)[:,np.newaxis]
            data = np.concatenate((data,similarities),axis = 1)
            
    
            return True, data[data[:,3]>'0.5']
        else:
            return False, data
            
    except:
        return False, {}
    
    


def search_results(track_name):
    
    page_number = 1
    data = []
    page_data = search_box(track_name,page_number)

    while len(page_data)!=0:
        data.append(page_data)
        page_number += 1
        page_data = search_box(track_name,page_number)

    try:
        return np.array(np.concatenate(data)).reshape(-1,3)
    except:
        return []

        
def get_jaccard_sim(str1, str2): 

    a = set(strip_off_punc(str1.lower()).split()) 

    b = set(strip_off_punc(str2.lower()).split())

    c = a.intersection(b)
    
    return float(len(c)) / (len(a) + len(b) - len(c))
