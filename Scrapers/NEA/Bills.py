#!/usr/bin/env python
# coding: utf-8

#Importing requests Library
import re
import json
import datetime
import itertools
from time import sleep
from pprint import pprint
from bs4 import BeautifulSoup
from requests import Request, Session

class ScraperNEA:
    
    def __init__(self):
        #initializing custom headers
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'}

        #initializing some parameters
        self.home_url = 'https://www.neabilling.com/viewonline/'
        self.result_url = "https://www.neabilling.com/viewonline/viewonlineresult/"

    #calculate date function
    def dateCalculator(self):
        dt = datetime.datetime.now()
        return {
            "from": (dt - datetime.timedelta(days=90)).strftime("%m/%d/%Y"),
            "to": dt.strftime("%m/%d/%Y")
        }

    def initDateAndSession(self):
        #Creating a session 
        self.session = Session()

        self.dt = self.dateCalculator()

        self.domestic_meter = {
            "NEA_Location": "334",
            "sc_no": "018.03.036",
            "consumer_id": "784",
            "Fromdatepicker": self.dt['from'],
            "Todatepicker": self.dt['to']
        }
        self.agri_meter = {
            "NEA_Location": "334",
            "sc_no": "018.03.206",
            "consumer_id": "753",
            "Fromdatepicker": self.dt['from'],
            "Todatepicker": self.dt['to']
        }
        self.meters = [self.domestic_meter, self.agri_meter]


    #parse locations as a list of dict (JSON)
    def parseLocations(self, html_text):
        locations = []
        locations_soup = BeautifulSoup(html_text, 'html.parser')
        locations_soup = locations_soup.find(id="NEA_location")
        for location in locations_soup.find_all('option'):
            id = location['value']
            if id != '' and id != 'SELECT...':
                locations.append({"id": id, "name": location.string})
        return locations

    # Print the json data with formatting (Utility Function)
    # use this function direct call. calling this function inside a print() will add an extra None at the end
    def printJson(self, jsn):
        if isinstance(jsn, dict):
            print(json.dumps(jsn, ensure_ascii=False, indent=4))
        elif isinstance(jsn, list):
            for item in jsn:
                print(json.dumps(item, ensure_ascii=False, indent=4))
        else:
            print(jsn)

    def parseRow(self, rowSoup, headers):
        data = {}
        rowSoup = rowSoup.find_all('td')
        for index, header in enumerate(headers):
            data[header] = rowSoup[index].string
        return data

    def parseFromTo(self, from_to):
        dates = re.findall(r'\b\d{2}[-\./]\d{2}[-\./]\d{2}\b|\b\d{4}[-\./]\d{2}[-\./]\d{2}\b|\b\d{2}[-\./]\d{2}[-\./]\d{4}\b',from_to)
        dates = [datetime.datetime.strptime(date, "%m/%d/%Y").strftime("%d %b %Y") for date in dates]
        return {"from": dates[0], "to": dates[1]}

    def parseBillData(self, tranSoup):
        if not tranSoup:
            pprint(tranSoup)
            return {"advance": 0, "unpaid": 0, "total_unpaid": 0, "message": "No transactions Found!"}
        # Filter out the paid transactions
        tranSoup = [tran for tran in tranSoup if tran["STATUS"] != "PAID"]

        if not tranSoup:
            pprint(tranSoup)

        #extract advance paid amount if any
        advance = [tran for tran in tranSoup if tran["STATUS"] == "PAY ADVANCE"]
        if advance:
            pprint(advance)
            advance[-1]["STATUS"] = advance[0]["DUE BILL OF"]
            advance = advance[-1]

            #extract unpaid transactions if any
            unpaid = [tran for tran in tranSoup if tran["STATUS"] == "UN-PAID"]

            if unpaid:
                total_unpaid = unpaid[-1]
                total_unpaid["DUE BILL OF"] = ", ".join([str(month["DUE BILL OF"]) for month in unpaid if month["DUE BILL OF"] != None])
                return {"advance": advance, "unpaid": unpaid, "total_unpaid": total_unpaid}
                
            return {"advance": advance, "unpaid": unpaid, "total_unpaid": 0}
        else:
            return {"advance": 0, "unpaid": 0, "total_unpaid": 0, "message": "Data not Found!"}
    def parseBill(self, html_text, trans = False):
        billData = {}
        billSoup = BeautifulSoup(html_text, 'html.parser')
        table_rows = billSoup.table.find_all('tr')
        from_to = table_rows[1].find('th').string
        billData['from_to'] = self.parseFromTo(from_to)
        billData['records'] = table_rows[4].text.strip('\n')
        if billData['records'] == "No Records Found.":
            billData['records'] = 0
            return billData
        consumer_details_soup = table_rows[1].table.find_all('tr')[3].find('td').table.find_all('tr')
        consumer_detail = {
            "customer_name": consumer_details_soup[0].find_all('td')[1].string,
            "sc_no": consumer_details_soup[0].find_all('td')[3].string,
            "counter": consumer_details_soup[1].find_all('td')[1].string,
            "consumer_id": consumer_details_soup[1].find_all('td')[3].string
        }
        billData['consumer_detail'] = consumer_detail
        bill_headers_soup = table_rows[1].find_all('strong')
        bill_headers = []
        for bill_header in bill_headers_soup:
            bill_headers.append(bill_header.string)
        transactions = []
        for transaction_soup in itertools.islice(table_rows , 10, len(table_rows)):
            transactions.append(self.parseRow(transaction_soup, bill_headers))
        if trans:
            billData['bill_headers'] = bill_headers
            billData['transactions'] = transactions
        billData['records'] = len(transactions)
        bill_status = self.parseBillData(transactions)
        billData['advance'] = bill_status['advance']
        billData['unpaid'] = bill_status['unpaid']
        billData['total_unpaid'] = bill_status['total_unpaid']
        return billData

    def getBills(self, transactions = False):
        #init Date and Session Variables
        self.initDateAndSession()

        #getting home page and extracting locations
        home = self.session.get(self.home_url, headers = self.headers)

        locations = self.parseLocations(home.text)

        sleep(0.3)

        #getting bills info for each meter
        bills = []
        for meter in self.meters:
            result = self.session.post(self.result_url, headers=self.headers, data=meter)
            bill = self.parseBill(result.text, trans = transactions)
            bills.append(bill)

        return bills
    
    def getBill(self, meter, transactions = False):
        #init Date and Session Variables
        self.initDateAndSession()

        #getting home page and extracting locations
        home = self.session.get(self.home_url, headers = self.headers)

        locations = self.parseLocations(home.text)

        #getting bills info for each meter
        bill = []
        if meter == "domestic":
            meter_data = self.domestic_meter
        else:
            meter_data = self.agri_meter
        result = self.session.post(self.result_url, headers=self.headers, data=meter_data)
        bill = self.parseBill(result.text, trans = transactions)
        return bill

    def getBillOf(self, meter, transctions = False):
        #init Date and Session Variables
        self.initDateAndSession()

        #getting home page and extracting locations
        home = self.session.get(self.home_url, headers = self.headers)

        locations = self.parseLocations(home.text)

        #getting bills info for each meter
        result = self.session.post(self.result_url, headers=self.headers, data=meter)
        bill = self.parseBill(result.text, trans = transctions)
        return bill