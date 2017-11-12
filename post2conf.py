#-*- coding: utf-8 -*-
import rankanalysis
import json
import requests
import time


BASE_URL = 'http://192.168.10.49:8090/rest/api/content'

def get_page_info(pageid=65628):
    """
    Get confluence page info
    :param pageid:
    :return: json dict
    """
    url = '{base}/{pageid}'.format(
        base = BASE_URL,
        pageid = pageid)

    auth = ('admin', '1234')
    r = requests.get(url, auth = auth)
    r.raise_for_status()
    print(r.json())
    return r.json()


def updateconf(htmlcode, title='Top 20 Positionen - voller Zeitraum',
               comment = '', pid='4194374'):
    """
    Takes html and updates the Master-Slave status confluence page
    :param htmlcode:
    :return:
    """
    url = 'http://192.168.10.49:8090/rest/api/content/{}'.format('4194374')
    #requests.put(url, data={'value',htmlcode.encode('ascii')}, auth=('admin','1234'))
    timeinfo = '<h2>Status at {timenow}</h2>'.format(timenow = time.strftime('%X %x %Z'))
    comment = '<h2>{com}</h2>'.format(com = comment)
    timeinfo = timeinfo.replace('\n','')
    pageinfo = get_page_info(pageid=pid)
    htmlcode = str(timeinfo + comment + htmlcode)
    print(htmlcode)
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
    updata = json.dumps(updata)
    r = requests.put(url, data=updata, auth=('admin','1234') ,headers = { 'Content-Type' : 'application/json' })
    print(r.text)
    return r


def main():
    service = rankanalysis.getservice(rankanalysis.creds())
    top20all, top20allnoeuro = rankanalysis.overalltop20(service)
    comments = 'Eintrage mit mindestens 5 \'impressions\''
    updateconf(top20all, 'Top 20 Positionen - voller Zeitraum', comments)


if __name__ == '__main__':
   main()
