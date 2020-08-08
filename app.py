from flask import Flask, render_template, request, redirect, url_for
from stockInfo import stockInfo, stockNews, stockBio, stockFinancials
from watchlist import screener
from tweets import tickerPopularity
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def tickerInput():
    if request.method == "POST":
        ticker = request.form['ticker'].upper()
        #checks to see if ticker exits    
        url = 'https://finviz.com/search.ashx?p=' + ticker
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(html.text, 'lxml')
        match = soup.find('div', class_="container")
        try:
            result = match.find('h4').text # trys to find text between h4 tags "No results found for "ticker"".
        except:
            result = None
        if result == None: # if result is none means ticker exists            
            return redirect(url_for('infoPage', ticker=ticker))
        else: # if result is other than none ticker does not exist
            return render_template('notfound.html', ticker=ticker)
    return render_template('home.html')
                          
@app.route('/<ticker>')
def infoPage(ticker):
    ticker = ticker # place holder so AttributeError: NoneType isn't thrown on page load
    # functions to be passed as variables in jinja2 template
    info = stockInfo(ticker)
    news = stockNews(ticker)
    bio = stockBio(ticker)
    fin = stockFinancials(ticker)  
    return render_template('stockInfo.html', ticker=ticker, news=news, bio=bio, info=info, fin=fin )

@app.route('/watchlist')
def watchlistPage():
    scrn = screener()
    # list of handles to check
    handle = ['PJ_Matlock', 'Hugh_Henne', 'MrZackMorris', 'The_Analyst_81', 'buysellshort', 'ACInvestorBlog', 'Anonymoustocks',
              'notoriousalerts', 'beach_trades', 'Reformed_Trader', 'Mitch_Picks', 'RadioSilentplay']
    twit = tickerPopularity(handle)
    return render_template('watchlist.html', scrn=scrn, twit=twit)

if __name__ == '__main__':
    app.run(debug=True)