import re
import urllib.request
import urllib.error
import requests
import time
import json
import os
from bs4 import BeautifulSoup
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
token = 'panerurkar_p16@ce.vjti.ac.in'
max_block = 710000

def get_label_names(url):
    head = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }
    request1 = urllib.request.Request(url, headers=head)
    response1 = urllib.request.urlopen(request1)
    html = response1.read().decode("utf-8")
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', attrs={'class': 'serviceslist'})
    for td in table.find('tr').find_all('td'):
        label = td.find('h3').text[0:-1]
        com_list = []
        for li in td.find('ul').find_all('li'):
            i = 0
            com_name = ''
            for a in li.find_all('a'):
                if i == 0:
                    com_name = a.text
                else:
                    com_name += '-'
                    com_name += a.text
                i += 1
                com_list.append(com_name)
            
            dic = {}
            dic["label"] = label
            dic["com_list"] = com_list

            path1 = "jsondata"
            path2 = "label_name"
            last_path = os.path.join(path1, path2)
            if not os.path.exists(last_path):
                os.makedirs(last_path)
            with open(os.path.join(last_path, label.replace('/', '-') + ".json"), 'w+', encoding='utf-8') as f:
                # A json file will be exported for every company
                json.dump(dic, f)

def req_count(url):  # get the total page number
    # request_count = 1
    head = {
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }
    request1 = urllib.request.Request(url, headers=head)
    response1 = urllib.request.urlopen(request1)
    html = response1.read().decode("utf-8")
    html1 = json.loads(html)

    if html1['found'] is True:
        address_counts = int(html1['addresses_count'])
        if address_counts > 100:
            request_count = address_counts//100+1
        else:
            request_count = 1
        return request_count, True
    else:
        return 0, False


def API_request(com_name, url, url_part, cl):  # use API to access WalletExplorer
    try:
        head = {
            "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
        }
        request1 = urllib.request.Request(url, headers=head)
        response1 = urllib.request.urlopen(request1)
        html = response1.read().decode("utf-8")
        html1 = json.loads(html)

        json_html1 = json.dumps(html1)  # json format
        # addresses_list = html1['addresses']

        # for address in addresses_list:

        #     sql = "insert into exchanges2(com_bc_add, com_name, url_source,balance,incoming_txs,last_used_in_block,get_time) values ('" + str(
        #         address["address"]) + "','" + str(com_name) + "','" + url_part + "','"+str(address["balance"])+"','"+str(address["incoming_txs"])+"','"\
        #         + str(address["last_used_in_block"])+"','" + \
        #         str(time.strftime('%Y-%m-%d %H:%M:%S'))+"');"
        #     try:
        #         # excute sql command
        #         cursor.execute(sql)
        #         db.commit()
        #         # print([bc_value.string, company_name, url])
        #     except:
        #         db.rollback()
        #         print("except")
    except:
        time.sleep(5)
        html1, json_html1 = API_request(com_name, url, url_part, cl)

    return html1, json_html1


def test_json(path):
    with open(path) as f:
        line = f.readline()
        result = json.loads(line)
    print(result)

# label_names = get_label_names("http://www.walletexplorer.com/")

if __name__ == "__main__":
    class_lable = "Pools"  # classification lable

    path1 = "jsondata"
    label_path = os.path.join(path1, "label_name")
    label_path = os.path.join(label_path, class_lable + '.json')

    with open(label_path, "r") as json_file:
        data = json.load(json_file)
    com_list = data['com_list'] # company name
    # com_list = ["Korbit.co.kr", "Vaultoro.com", "Exchanging.ir",
    #             "796.com", "HappyCoins.com", "BtcMarkets.net"]  # company name
    for company_name in com_list:
        # company_name = company_name1.lower()  # Company name must be lowercase without suffix
        url = "http://www.walletexplorer.com/api/1/wallet-addresses?wallet=" + \
            company_name + "&from=0&count=100&caller=" + token
        request_count, if_found = req_count(url)
        if if_found:
            count = 0  # counter
            dic_data_list = []
            for i in range(0, request_count):
                print(company_name, i)
                url = "http://www.walletexplorer.com/api/1/wallet-addresses?wallet=" + company_name + "&from=" + str(
                    count) + "&count=100&caller=" + token
                url_1 = "http://www.walletexplorer.com/api/1/wallet-addresses?wallet=" + company_name + "&from=" + str(
                    count) + "&count=100"
                dic_data, json_data = API_request(
                    company_name, url, url_1, class_lable)
                count += 100
                # if dic_data['addresses'][-1]['last_used_in_block'] < max_block:
                #     dic_data_list.append(dic_data)
                #     break
                dic_data_list.append(dic_data)

            dic_all = {}
            dic_all["content"] = dic_data_list
            dic_all["count"] = request_count

            path2 = class_lable
            last_path = os.path.join(path1, path2)
            if not os.path.exists(last_path):
                os.makedirs(last_path)
            with open(os.path.join(last_path, company_name + ".json"), 'w+', encoding='utf-8') as f:
                # A json file will be exported for every company
                json.dump(dic_all, f)
