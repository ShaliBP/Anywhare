from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import json
import time

app = Flask(__name__)
@app.route('/')
def index():
    with open('data.json') as f:
        data = json.load(f)
    return json.dumps(data)

def scrape_articles(chosencategory, articletype, category):
    url = ("https://shalhevetboilingpoint.com/category/" + chosencategory)
    page = 1
    articles = []
    while True:
        response = requests.get(f"{url}/page/{page}")
        soup = BeautifulSoup(response.content, 'html.parser')
        posts = soup.find_all("div", class_=articletype)
        if not posts:
            break
        for post in posts:
            article = {}
            article["title"] = post.find('a', {'class': 'homeheadline'}).text.strip()
            article["url"] = post.find('a')['href']
            article["description"] = post.find('div', {'class': 'catlist-teaser'}).text.strip()
            try:
                article["urlToImage"] = post.find('img')['src']
            except TypeError:
                pass
            try:
                article["author"] = post.find('span', {'class': 'catlist-writer'}).text.strip()
                # article["author"] = "Written By: Benjy Kolieb"
            except AttributeError:
                pass
            try:
                article["publishedAt"] = post.find('span', {'class': 'time-wrapper'}).text.strip()
            except AttributeError:
                pass
            article["category"] = category
            articles.append(article)
        page += 1
    return articles
def update_data():
    while True:
        def nw_data():
            articles = {}
            articles["top_stories"] = scrape_articles("top-stories/", "profile-rendered catlist-panel catlist_sidebar",
                                                      "top")
            articles["community"] = scrape_articles("community/", "profile-rendered catlist-panel catlist_sidebar",
                                                    "community")
            articles["arts"] = scrape_articles("arts/", "profile-rendered catlist-panel catlist_fullwidth", "arts")
            articles["torah"] = scrape_articles("torah/", "profile-rendered catlist-panel catlist_fullwidth", "torah")
            articles["outside_news"] = scrape_articles("outside-news/", "catlist-tile-inner", "outside")
            articles["opinion"] = scrape_articles("opinion/", "catlist-tile-inner", "opinion")
            articles["alumni"] = scrape_articles("alumni/", "catlist-tile-inner", "alumni")
            articles["features"] = scrape_articles("features/", "profile-rendered catlist-panel catlist_fullwidth",
                                                   "feature")
            return json.dumps(articles)
        new_data = nw_data()
        with open('data.json', 'w') as f:
            json.dump(new_data, f)
        time.sleep(1800)  # wait for 30 minutes


if __name__ == '__main__':
    # Start a new thread to update the data in the background
    import threading
    update_thread = threading.Thread(target=update_data)
    update_thread.start()

    # Start the Flask app
    app.run(debug=True)