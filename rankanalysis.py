#-*- encoding: utf-8 -*-
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from datetime import datetime, timedelta


def creds(jsonfile=('C:/Users/euroadmin/PyCharmProjects/EuroRank/'
                   'euroanalysis-4ca6815c21ac.json'),
          scope=['https://www.googleapis.com/auth/webmasters.readonly']):
    return ServiceAccountCredentials.from_json_keyfile_name(jsonfile, scopes=scope)

def getservice(credentials):
    http_auth = credentials.authorize(Http())
    service = build('webmasters', 'v3', http=http_auth)
    return service


def buildrequest(service, startDate='2017-09-01', endDate = '2017-11-01',
                 dimensions = None, dimfilter = None, rowlimit=5000):
    """"
    Build json request sent to API
    """
    request = {
        'startDate' : startDate,
        'endDate' : endDate,
        'rowLimit' : rowlimit,
        'dimensions' : dimensions,
        'dimensionFilterGroups' : dimfilter
    }
    response = service.searchanalytics().query(siteUrl='https://eurodriver.ch', body=request).execute()
    totclicks = 0
    #print(len(response['rows']))
    for k in response['rows']:
        totclicks += k['clicks']
    #print(totclicks)
    return response


def total(service):
    """
    Get the overall total
    """
    req = rankanalysis.buildrequest(service, startDate='2010-01-01',endDate='2025-01-01')['rows'][0]


def overalltop20(service, lookback = -1):
    """
    Top 20 keywords over full time period
    """
    latest = datetime.today() - timedelta(days=3)
    startDate = datetime.today() - timedelta(days=(3+lookback)
    if lookback == -1:
        startDate = '2010-01-01'
    df = buildrequest(service, startDate = startDate, endDate=latest.strftime('%Y-%m-%d'),
                      dimensions=['query'], rowlimit=1500)['rows']
    ts = pd.DataFrame(df)
    x = pd.Series(ts.columns)
    x[x[x == 'keys'].index[0]] = 'keyword'
    ts.columns = x
    ts['keyword'] = [i[0] for i in ts['keyword']]
    ts.sort_values('position', inplace=True)
    top20full = ts[ts.impressions>5][:20].to_html(index=False)
    top20noeuro = ts.ix[(ts['impressions']>5) &
                     (~ts['keyword'].str.contains('euro')),:
                    ]#.sort_values('impressions')
    badts = ts[(ts['impressions']>5) & (~ts['keyword'].str.contains('euro'))
                & (ts['position']<10)].sort_values('ctr')
    return (top20full, top20noeuro.sort_values('position')[:20].to_html(index=False),
            badts[:20].to_html(index=False))


def querywoeuro(service, start='2010-01-01', end='2025-01-01'):
    # Latest data has a 3 day lag to present
    latest = datetime.today() - timedelta(days=3)
    lookback = 30
    #latest = latest.strftime('%Y-%m-%d')
    index = pd.date_range(latest - timedelta(lookback), periods=lookback, freq='D')
    #ts = pd.DataFrame(colums=['key', 'impressions', 'ctr', 'rank'], index=index)
    dimfilter = [{'filters': [{'operator': 'notContains', 'expression': 'euro', 'dimension': 'query'}]}]
    resdf = {}
    for i in range(lookback):
        df = buildrequest(service, startDate = (latest - timedelta(days=1)).strftime('%Y-%m-%d'),
                           endDate=latest.strftime('%Y-%m-%d'), dimensions=['query'], rowlimit=1500)['rows']
                           #dimfilter=myfilter)
        latest = latest - timedelta(days=1)
        df = pd.DataFrame(df)
        x = pd.Series(df.columns)
        x[x[x == 'keys'].index[0]] = 'keyword'
        df.columns = x
        df['keyword'] = [i[0] for i in df['keyword']]
        df = df.ix[(~df['keyword'].str.contains('euro')),:].sort_values('impressions', ascending=False)
        for i in df.index:
            if df.ix[i,'keyword'] in resdf:
                #resdf[df.ix[i,'keyword']].append([latest.strftime('%Y-%m-%d'), df.ix[i,'position'], df.ix[i,'impressions'], df.ix[i, 'ctr']])
                resdf[df.ix[i,'keyword']].append([latest.strftime('%Y-%m-%d'), df.ix[i,'position'], df.ix[i,'impressions'], df.ix[i, 'ctr']])
            else:
                #resdf[df.ix[i,'keyword']] = [latest.strftime('%Y-%m-%d'), df.ix[i,'position'], df.ix[i,'impressions'], df.ix[i,'ctr']]
                resdf[df.ix[i,'keyword']] = pd.DataFrame(latest.strftime('%Y-%m-%d'), df.ix[i,'position'], df.ix[i,'impressions'], df.ix[i,'ctr']]
        #print(df[:20])
    print(len(resdf))
    return resdf


def makedf():
    res = buildrequest(getservice(creds()), startDate='2016-10-21',
                       endDate='2017-11-11', dimensions=['query'])
    res = pd.DataFrame(res['rows'])
    return res


def histograms(df):
    """
    Make some histograms
    """
    plt.rc('text', usetex=True)
    plt.hist2d([x['position'] for x in df['rows']], [x['ctr'] for x in df['rows']], bins=20, norm=LogNorm())
    plt.colorbar()
    plt.ylabel('click rate', fontsize=16)
    plt.xlabel('position', fontsize=16)
    plt.annotate(r'\huge{should be closer to 1.0}', xy=(10,0.05), xytext=(50, 0.2), arrowprops=dict(facecolor='black', shrink=0.05),)
    plt.title('Click rate vs Search rank',fontsize=24)
    plt.savefig('crtVsRank.png')


def lowctrandhighrank(df):
    """
    Get key words with good ranking but low click rate
    """
    df2 = df.ix[(df['position']<10) & (df['ctr']<0.1) & (df['impressions']>10),:]


def highctr(df):
    """
    Get keys with high ranking, high ctr and more than 10 impressions
    """
    df2 = df.ix[(df['position']<10) & (df['ctr']>0.1) & (df['impressions']>10),:].sort_values(by='position')


def parseresponse(response):
    """"
    Extract info from the API response
    """
    for k, v in response.items():
        print('{} : {}'.format(k,v))


def main():
    r = buildrequest(getservice(creds(jsonfile='/home/ignacio/data/eurodriver/EuroRank/euroanalysis-4ca6815c21ac.json')))
    return r
    print(r)
    parseresponse(r)



if __name__=='__main__':
    main()
