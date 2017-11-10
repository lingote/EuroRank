#-*- encoding: utf-8 -*-
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
import pandas as pd


def creds(jsonfile=('C:/Users/euroadmin/PyCharmProjects/EuroRank/'
                   'euroanalysis-4ca6815c21ac.json'),
          scope=['https://www.googleapis.com/auth/webmasters.readonly']):
    return ServiceAccountCredentials.from_json_keyfile_name(jsonfile, scopes=scope)

def getservice(credentials):
    http_auth = credentials.authorize(Http())
    service = build('webmasters', 'v3', http=http_auth)
    return service

def buildrequest(service, startDate='2017-09-01', endDate = '2017-11-01',
                 dimensions = None):
    """"
    Build json request sent to API
    """
    request = {
        'startDate' : startDate,
        'endDate' : endDate,
        'rowLimit' : 5000,
        'dimensions' : dimensions
    }
    response = service.searchanalytics().query(siteUrl='https://eurodriver.ch', body=request).execute()
    totclicks = 0
    print(len(response['rows']))
    for k in response['rows']:
        totclicks += k['clicks']
    print(totclicks)
    return response


def makedf():
    res = buildrequest(getservice(creds()), startDate='2016-10-21',
                       endDate='2017-11-11', dimensions=['query'])
    res = pd.DataFrame(res['rows'])
    return res


def parseresponse(response):
    """"
    Extract info from the API response
    """
    for k, v in response.items():
        print('{} : {}'.format(k,v))


def main():
    r = buildrequest(getservice(creds()))
    return r
    print(r)
    parseresponse(r)



if __name__=='__main__':
    main()