"""url = "https://ria.ru/20220502/sanktsii-1786520591.html?rcmd_alg=slotter"
url2 = "https://ria.ru/20220502/bibliya-1786532531.html"


print(len(".html?rcmd_alg=slotter"))
article_id1 = url2.split("/")[-1]
article_id1 = article_id1[:-5]
print(article_id1)
article_id2 = url.split("/")[-1]
article_id2 = article_id2[:-22]
print(article_id2)
urls = [ url, url2]
for url in urls:
"""

"""import json

with open("news_dict.json", encoding='utf-8') as file:
    news_dict = json.load(file)

search = "belgorod-17865286769"

if search in news_dict:
    print("Im here")
else:
    print("New add")"""
