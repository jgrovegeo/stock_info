import pandas as pd
import datetime as dt
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def stockInfo():
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
            pass
        
        if result == None: # if result is none means ticker exists
            # scrapes stock chart/company info from finviz
            def stockInfo(ticker):
                chart = '<img src="https://finviz.com/chart.ashx?t=' + ticker + '&ty=c&ta=1&p=d&s=l">'
                
                url = 'https://finviz.com/quote.ashx?t=' + ticker
                html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(html.text, 'lxml')
                
                # finds news table within finviz website
                stock_website = soup.find('table', class_="fullview-title")
                company_name = stock_website.find('a', class_='tab-link').text
                website_link = stock_website.find('a', class_='tab-link', href=True)['href']
                industry = soup.find('td', class_='fullview-links')
                industry_link = stock_website.find('td', class_='fullview-links').text
                statement = 'https://finance.yahoo.com/quote/' + ticker + '/financials?p=' + ticker
                desc = soup.find('td', class_='fullview-profile').text
                tutions = 'https://fintel.io/so/us/' + ticker
                twitter = 'https://twitter.com/search?q=%24' + ticker + '&src=typed_query' 
                
                return company_name, website_link, statement, industry_link, desc, tutions, twitter
            
            # scrapes finacial table from finviz
            def stockFinancials(ticker):
                url = 'https://finviz.com/quote.ashx?t=' + ticker
                header = {
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
                            "X-Requested-With": "XMLHttpRequest"
                            }

                r = requests.get(url, headers=header)
                fin = pd.read_html(r.text)
                columns = []
                values = []

                # appends Market Cap
                columns.append(fin[6].iloc[1][0])
                values.append(fin[6].iloc[1][1])
                # appends EPS Q/Q
                columns.append(fin[6].iloc[9][4])
                values.append(fin[6].iloc[9][5])
                # appends Sales Q/Q
                columns.append(fin[6].iloc[8][4])
                values.append(fin[6].iloc[8][5])
                # appends shares outstanding
                columns.append(fin[6].iloc[0][8])
                values.append(fin[6].iloc[0][9])
                # appends shares float
                columns.append(fin[6].iloc[1][8])
                values.append(fin[6].iloc[1][9])
                # appends shares short float
                columns.append(fin[6].iloc[2][8])
                values.append(fin[6].iloc[2][9])
                
                fin = dict(zip(columns, values))
                return fin
                 
            # scrapes stock news from finviz
            def stockNews(ticker):
                url = 'https://finviz.com/quote.ashx?t=' + ticker
                html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(html.text, 'lxml')
                
                # finds news table within finviz website
                match = soup.find('table', class_="fullview-news-outer")
        
                dates = []
                time = []
                # appends dates in html to list
                for d in match.find_all("td", width="130"):
                    if len(d.text.split(' ')) == 2:
                        dates.append(d.text.split(' ')[0])
                        time.append(d.text.split(' ')[1])
                    elif len(d.text.split(' ')) == 1:
                        dates.append('None')
                        time.append(d.text.split(' ')[0])  
                # uses an assignment expression to replace 'None' with previous element in list
                dates = [current:=d if d != 'None' else current for d in dates]
                        
                articles = []
                # appends new title to titles list
                for t in match.find_all("a", class_="tab-link-news"):
                    match.find(class_='tab-link-news')['class'] = "news-link"
                    articles.append(str(t))
                
                df_news = pd.DataFrame(list(zip(dates, time, articles)), columns=['Date', 'Time', 'Article'])
                # formats Date column/datetime string in dataframe
                df_news['Date'] = pd.to_datetime(df_news['Date'], errors='ignore').dt.strftime('%Y-%m-%d')
                json_news = json.loads(df_news.to_json(orient='records'))
                return json_news
            # scrapes catalyst info from biopharm     
            def stockBio(ticker):
                url = 'https://www.biopharmcatalyst.com/company/' + ticker + '#drug-information'
                html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                soup = BeautifulSoup(html.text, 'lxml')
                
                # finds div with class drug-info
                match = soup.find('div', class_="drug-info-table-wrap")
                
                names = []
                cnotes = []
                
                try:
                    # appends drug name to list
                    for n in match.find_all("div", class_="drug-info__name"):
                        names.append(n.text)
                    # appends catalyst notes to list
                    for c in match.find_all('div', class_='catalyst-note'):
                        cnotes.append(c.text)
                    # throws both lists into a single dataframe
                    df_bio = pd.DataFrame(list(zip(names, cnotes)), columns = ['Name', 'Catalyst Notes'])
                    df_bio = json.loads(df_bio.to_json(orient='records'))
                except:
                    df_bio = None

                return df_bio
                                     
            # functions to be passed as variables in jinja2 template
            info = stockInfo(ticker)
            news = stockNews(ticker)
            bio = stockBio(ticker)
            fin = stockFinancials(ticker)
            
            return render_template('stockInfo.html', ticker=ticker, news=news, bio=bio, info=info, fin=fin)
        else: # if result is other than none ticker does not exist
            return render_template('notfound.html', ticker=ticker)
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
