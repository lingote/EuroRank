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


def updateconf(htmlcode, title='Top 20 Positionen - voller Zeitraum', pid='4194374'):
    """
    Takes html and updates the Master-Slave status confluence page
    :param htmlcode:
    :return:
    """
    url = 'http://192.168.10.49:8090/rest/api/content/{}'.format('4194374')
    #requests.put(url, data={'value',htmlcode.encode('ascii')}, auth=('admin','1234'))
    timeinfo = '<h2>Status at {timenow}</h2>'.format(timenow = time.strftime('%X %x %Z'))
    timeinfo = timeinfo.replace('\n','')
    comment = ('<p>This is page is automatically generated',
              ' - do not edit manually (edits won\'t be saved)</p>')
    pageinfo = get_page_info()
    htmlcode = str(timeinfo + htmlcode)
    print(htmlcode)
    updata = {
        'id' : str(pageinfo[pid]),
        'type' : 'page',
        'title' : 'Master - Slave Status',
        'version' : {'number' : pageinfo['version']['number'] + 1},
        'space' : {'key' : "IT"},
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
    serice = rankanalysis.getservice(rankanalysis.cred())
    top20all, top20allnoeuro = rankanalysis.overalltop20(service)
    updateconf(top20all)


if __name__ == '__main__':
   main()
