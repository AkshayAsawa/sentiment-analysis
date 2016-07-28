from django.shortcuts import render,redirect
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from myapp import config
from myapp.sentiment_algo import info, search_google
import requests, unirest, datetime, collections, json, tweepy, urllib2, lxml
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from bs4 import BeautifulSoup

def landing(request):
    return render(request, 'landing.html', {})

def team(request):
    return render(request, 'team.html', {})

def landing_re(request):
    return redirect('/')

@csrf_exempt
def home(request):
    context = {}
    if request.POST:
        print "Fetching Tweets..."
        tag = request.POST['tag']
        tweet_l = get_tweets(str(tag))
        context['tweets'] = []
        senti_list = []
        an_hour_of_tweets = ''
        splitter = "#$#$#$#$#$#$#$#$"
        for i, tweet in enumerate(tweet_l):
            if 'RT @' in tweet.text:
                # Ignoring retweets
                continue
            tweet.text = ''.join(tweet.text.split('\n'))
            senti_list.append(tweet.text + splitter + str(tweet.created_at)[0:10])

        rows = info.main(senti_list)
        ct = 1
        pos = 0
        neg = 0
        neu = 0
        date_wise_dict = {}
        for row in rows:
            if not row == '':
                score = row['score']
                temp = row['text']
                temp2 = temp.split(splitter)
                sentence = temp2[0].strip('"')
                if len(temp2) < 2:
                    # Date Not Present
                    continue
                date = temp2[1].strip('"')
                if not date in date_wise_dict:
                    date_wise_dict[date] = []
                date_wise_dict[date].append({'sentence':temp, 'score':int(score)})
                context['tweets'].append({'count':str(ct), 'sentence':temp, 'score':int(score)})
                ct += 1
                if score == 0:
                    neg += 1
                elif score == 2:
                    neu += 1
                elif score == 4:
                    pos += 1

        c_date_wise = {}
        for k,v in date_wise_dict.items():
            key = datetime.datetime.strptime(k, "%Y-%m-%d")
            pos_score = 0
            neg_score = 0
            neu_score = 0
            total_score = 0
            for i in v:
                total_score += 1
                if i['score'] == 0:
                    neg_score += 1
                elif i['score'] == 2:
                    neu_score += 1
                    total_score -= 1
                elif i['score'] == 4:
                    pos_score += 1
            if total_score != 0:
                c_date_wise[key] = pos_score * 100 / total_score
            else:
                c_date_wise[key] = 0

        od_date_wise = sorted(c_date_wise.items())
        context['dates'] = []
        context['date_wise_score'] = []
        for i in od_date_wise:
            context['dates'].append(str(i[0])[0:10])
            context['date_wise_score'].append(int(i[1]))

        # Google scraping starts from here
        print "Fetching Google Results..."
        search_term = tag + ' reviews'
        google_result = get_google_results(search_term)
        context['google_articles'] = []
        for g_r in google_result:
            print "Analysing website:", g_r[1]
            p_l, li_l = get_bs(g_r[1])
            final_l = zip(p_l, li_l)
            sentiment_p = info.main(final_l)
            total = 0
            positive = 0
            for i in sentiment_p:
                total += 1
                if i['score'] == 4:
                    positive += 1
                if i['score'] == 2:
                    total -= 1
            pos_per = 0
            if total != 0:
                pos_per = positive * 100 / total
            context['google_articles'].append({'title': g_r[0], 'url': g_r[1], 'pos_percentage': pos_per})

        context['tag'] = tag
        context['pos_percentage'] = pos * 100 / ct
        context['neg_percentage'] = neg * 100 / ct
        context['neu_percentage'] = neu * 100 / ct
        context['date_wise'] = zip(context['dates'], context['date_wise_score'])
        context['for_twitter'] = ''.join(request.POST['tag'].split())
    return render(request,'index.html',context)

def auth_twitter():
    auth = OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)
    return auth

def get_tweets(query):
        auth = auth_twitter()
        api = tweepy.API(auth)
        date = datetime.datetime.today()
        results = []
        for i in range(8):
            until_date = str(date - datetime.timedelta(days=i))[0:10]
            temp = api.search(q=query, lang='en', count=100, until=until_date)
            print "Tweets of Date:", until_date
            results.extend(temp)
        return results


def get_google_results(search_term):
    return search_google.main(search_term)

def get_bs(url):
    url_home_tr = url
    response_home_tr = requests.get(url_home_tr)
    html_home_tr = response_home_tr.content
    soup_home_tr = BeautifulSoup(html_home_tr,'lxml')
    p_list = soup_home_tr.find_all('p')
    li_list = soup_home_tr.find_all('li')
    p_final = []
    li_final = []
    for i in p_list:
        p_final.append(str(i.contents))
    for i in li_list:
        li_final.append(str(i.contents))
    return p_final, li_final
