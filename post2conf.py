#-*- coding: utf-8 -*-
import rankanalysis
import json
import requests
import time


BASE_URL = 'http://192.168.10.49:8090/rest/api/content'

def get_page_info(pageid=65628, url=''):
    """
    Get confluence page info
    :param pageid:
    :return: json dict
    """
    url = '{base}/{pageid}/{url}'.format(
        base = BASE_URL,
        pageid = pageid,
        url = url
    )

    auth = ('admin', '1234')
    r = requests.get(url, auth = auth)
    r.raise_for_status()
    #print(r.json())
    return r.json()


def updateconf(htmlcode, title='Top 20 Positionen - voller Zeitraum',
               comment = '', pid='4194374'):
    """
    Takes html and updates the Master-Slave status confluence page
    :param htmlcode:
    :return:
    """
    url = 'http://192.168.10.49:8090/rest/api/content/{}'.format(pid)
    #requests.put(url, data={'value',htmlcode.encode('ascii')}, auth=('admin','1234'))
    timeinfo = '<h2>Status at {timenow}</h2>'.format(timenow = time.strftime('%X %x %Z'))
    comment = '<h2>{com}</h2>'.format(com = comment)
    comment = comment + '<p>Automatically generated - edits will be overwritten</p>'
    timeinfo = timeinfo.replace('\n','')
    pageinfo = get_page_info(pageid=pid)
    htmlcode = str(timeinfo + comment + htmlcode)
    #print(htmlcode)
    updata = {
        'id' : str(pageinfo['id']),
        'type' : 'page',
        'title' : title,
        'version' : {'number' : pageinfo['version']['number'] + 1},
        'space' : {'key' : "GRA"},
        #'ancestors' : [anc],
        'body'  : {
            'storage' :
            {
                'representation' : 'storage',
                'value' : htmlcode,
            }
        }
    }
    #if payload is not None:
    #    updata['params'] = {'filename' : payload}
    updata = json.dumps(updata)
    r = requests.put(url, data=updata, auth=('admin', '1234'), headers={'Content-Type': 'application/json'})
    #print(r.text)
    return r


def uploadfile(htmlcode, title='Top 20 Positionen - voller Zeitraum',
               comment = '', pid='4194374', upfile=None):
    """
    Takes html and updates the Master-Slave status confluence page
    :param htmlcode:
    :return:
    """
    url = 'http://192.168.10.49:8090/rest/api/content/{}/child/attachment'.format(pid)
    timeinfo = '<h2>Status at {timenow}</h2>'.format(timenow = time.strftime('%X %x %Z'))
    comment = '<h2>Automatically generated with Google Search Console API and confluence REST API</h2>'
    #comment = comment + '<p>Automatically generated - edits will be overwritten</p>'
    timeinfo = timeinfo.replace('\n','')
    htmlcode = str(timeinfo + comment + htmlcode)
    fname = upfile[upfile.rfind('/')+1:]
    shortname = fname[:fname.rfind('_')] + '.png'
    pageinfo = get_page_info(pageid=pid, url='child/attachment')
    #attid = pageinfo['results'][0]['id']
    #print(pageinfo['results'])
    attid = -1
    for i in pageinfo['results']:
        #print(i['title'])
        if shortname == i['title']:
            attid = i['id']
    content_type = 'image/png'
    #print('shortname {} - attid {}'.format(shortname, attid))
    r = requests.post(
            url + '/{}/data'.format(attid),
            files={
                'file':(shortname, open(upfile, 'rb'),),
                'comment':"Uploaded automatically.",
                'minorEdit':"false"
                },
            auth=('admin', '1234'),
            headers={'X-Atlassian-Token':'no-check'})
    #print(r.text)
    return r


def main():
    service = rankanalysis.getservice(rankanalysis.creds())
    top20all, top20allnoeuro, top20lowctr = rankanalysis.overalltop20(service)
    # get today - 33 days:
    
    top20_30days, top20noeuro_30days, top20lowctr_30days = rankanalysis.overalltop20(service, lookback=30)
    comments = 'Eintr\xe4ge mit mindestens 5 \'impressions\''
    updateconf(top20all, 'Top 20 Positionen - voller Zeitraum', comments, 4194374)
    updateconf(top20allnoeuro, 'Top 20 Pos. ohne \'euro\' im Keyword - voller Zeitraum', comments, 4194383)
    updateconf(top20lowctr, 'Top 10 Position, schlechte Click Rate - voller Zeitraum', comments, 4194388)
    updateconf(top20_30days, 'Top 20 Positionen - letzte 30 Tage', comments, 4194442)
    updateconf(top20noeuro_30days, 'Top 20 Pos. ohne \'euro\' im Keyword - letzte 30 Tage', comments,4194440 )
    updateconf(top20lowctr_30days, 'Top 10 Position, schlechte Click Rate - letzte 30 Tage', comments, 4194438 )
    df1, f1 = rankanalysis.keywordtimeseries(service, start='2010-11-01', end='2025-01-01', keyword='czv')
    df2, f2 = rankanalysis.keywordtimeseries(service, start='2010-11-01', end='2025-01-01', keyword='fahrschule')
    df3, f3 = rankanalysis.keywordtimeseries(service, start='2010-11-01', end='2025-01-01', keyword='euro')
    df4, f4 = rankanalysis.keywordtimeseries(service, start='2010-11-01', end='2025-01-01', keyword='lkw')
    df5, f5 = rankanalysis.keywordtimeseries(service, start='2010-11-01', end='2025-01-01', keyword='lastwagen')
    comments = 'Rang Zeitreihe f\xfcr Suchbegriffe'
    uploadfile('', 'Search Rank Evolution', comments, 4194691, upfile='C:/Users/euroadmin/PyCharmProjects/EuroRank/{}'.format(f1))
    uploadfile('', 'Search Rank Evolution', comments, 4194691, upfile='C:/Users/euroadmin/PyCharmProjects/EuroRank/{}'.format(f2))
    uploadfile('', 'Search Rank Evolution', comments, 4194691, upfile='C:/Users/euroadmin/PyCharmProjects/EuroRank/{}'.format(f3))
    uploadfile('', 'Search Rank Evolution', comments, 4194691, upfile='C:/Users/euroadmin/PyCharmProjects/EuroRank/{}'.format(f4))
    uploadfile('', 'Search Rank Evolution', comments, 4194691, upfile='C:/Users/euroadmin/PyCharmProjects/EuroRank/{}'.format(f5))



if __name__ == '__main__':
   main()
