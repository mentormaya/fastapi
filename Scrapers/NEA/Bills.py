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
from pydantic import BaseModel
from typing import Dict, Optional


#some state templates
UNPAID_MSG = "ने.रु. {} तिर्न बांकी"
ADVANCE_MSG = "ने.रु. {} बढी तिरेकाे"
UNPAID_ADVANCE_MSG = "ने.रु. {} तिर्न बांकी र {} पुरानाे बढी तिरेकाे"
PAID_MSG = "सबै बिलकाे भुक्तानी भइसकेकाे छ!"
NO_TRANSACTION_MSG = "कुनै बिल तथा काराेबार पाइएन!"


#months list

nep_months_eng = ["Baishakh", "Jestha", "Ashad", "Shrawan", "Bhadau", "Ashoj", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra", "ARREARS"]
nep_months_nep = ["बैशाख", "जेष्ठ", "असार", "श्रावन", "भदौ", "असोज", "कार्तिक", "मङ्सिर", "पौष", "माघ", "फाल्गुन", "चैत्र", "बक्याैता"]

nep_numbers = ["०", "१", "२", "३", "४", "५", "६", "७", "८", "९"]

def eng_to_nep_month(month):
    if not month:
        return ""
    mnth = nep_months_nep[nep_months_eng.index(month)]
    return mnth

def split_characters(word):
    return [char for char in word]

def join_characters(list_s):
    word = ""
    for item in list_s:
        word = word + item
    return word

def nep_num(num):
    num_rs = split_characters(str(num))
    nep = join_characters([nep_numbers[int(lit)] if lit != '.' else '.' for lit in num_rs])
    return nep

def get_nep_month(month):
    index = int(month)
    return nep_months_nep[index - 1]

def parseDate(date_str):
    if not date_str:
        return "No Date Given!"
    date_str = re.split("-",date_str)
    res = get_nep_month(date_str[1]) + " " + nep_num(date_str[0])
    return res

#Data type definition for bill data
class Bill(BaseModel):
    name: str = "NEA Bill"
    description: Optional[str]
    raw_data: dict
    state: Optional[str]
    status: Optional[str]
    consumer_name: Optional[str]
    sc_no: Optional[str]
    counter: Optional[str]
    consumer_id: Optional[int]
    bill_from: Optional[str]
    bill_to: Optional[str]
    paid_up_to: Optional[str]
    advance: Optional[float]
    unpaid: Optional[float]
    due_bill_of: Optional[str]
    records: Optional[int]
    consumed_units: Optional[float]
    rebate: Optional[str]
    rate: Optional[float]

class ScraperNEA:
    
    def __init__(self):
        #initializing custom headers
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'}

        #initializing some parameters
        self.home_url = 'https://www.neabilling.com/viewonline/'
        self.result_url = "https://www.neabilling.com/viewonline/viewonlineresult/"

    #calculate date function
    def dateCalculator(self, range = 'fiscalYear'):
        dt = datetime.datetime.now()
        if range == 'fiscalYear':
            range_from = '01/01/' + str(dt.year)
        else:
            range_from = (dt - datetime.timedelta(days=180)).strftime("%m/%d/%Y")
        return {
            "from": range_from,
            "to": dt.strftime("%m/%d/%Y")
        }

    def initDateAndSession(self):
        #Creating a session 
        self.session = Session()

        self.dt = self.dateCalculator(range = "last_six_months")

        self.domestic_meter = {
            "name": "Home NEA Bill",
            "NEA_Location": "334",
            "sc_no": "018.03.036",
            "consumer_id": "784",
            "Fromdatepicker": self.dt['from'],
            "Todatepicker": self.dt['to']
        }

        self.agri_meter = {
            "name": "Agriculture NEA Bill",
            "NEA_Location": "334",
            "sc_no": "018.03.206",
            "consumer_id": "753",
            "Fromdatepicker": self.dt['from'],
            "Todatepicker": self.dt['to']
        }

        self.agri_meter_old = {
            "name": "Agriculture NEA Bill(OLD)",
            "NEA_Location": "334",
            "sc_no": "001.09.701B",
            "consumer_id": "753",
            "Fromdatepicker": self.dt['from'],
            "Todatepicker": self.dt['to']
        }

        self.amita_meter = {
            "name": "Amita NEA Bill",
            "NEA_Location": "374",
            "sc_no": "038.02.067",
            "consumer_id": "501003293",
            "Fromdatepicker": self.dt['from'],
            "Todatepicker": self.dt['to']
        }

        self.puja_meter = {
            "name": "Puja NEA Bill",
            "NEA_Location": "374",
            "sc_no": "035.01.014",
            "consumer_id": "501005114",
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

    def parseDue(self, due):
        if not due:
            return ""
        res = re.split(", ",due)
        res = [eng_to_nep_month(dt.split("/")[0]) + "/" + nep_num(dt.split("/")[1]) if len(dt.split("/")) > 1 else eng_to_nep_month(dt.split("/")[0]) for dt in res]
        return ", ".join(res)

    def getConsumedUnits(self, unpaid):
        units = 0
        if unpaid:
            for month in unpaid:
                if month["CONSUMED UNITS "] is not None:
                   units = units + float(month["CONSUMED UNITS "])
        # pprint(units)
        return units

    def parseBillData(self, tranSoup):
        if not tranSoup:
            pprint(tranSoup)
            return { "result": False, "message": "No transactions Found!"}
        # Filter out the paid transactions
        paid = [tran for tran in tranSoup if tran['STATUS'] == 'PAID']

        if paid:
            paid_up_to = paid[-2]["DUE BILL OF"]
        else:
            paid_up_to = ""
        # pprint(paid_up_to)

        #extract advance paid amount if any
        advance = [tran for tran in tranSoup if tran["STATUS"] == "PAY ADVANCE"]
        total_advance = 0
        if advance:
            paid_up_to = advance[-2]["DUE BILL OF"]
            advance[-1]["STATUS"] = advance[0]["DUE BILL OF"]
            advance = advance[-1]
            total_advance = advance['BILL AMT']
            # return {"advance": advance, "unpaid": unpaid, "total_unpaid": 0}

        #extract unpaid transactions if any
        unpaid = [tran for tran in tranSoup if tran["STATUS"] == "UN-PAID"]
        total_unpaid = 0
        due_bill_of = ""
        consumed_units = 0
        rate = 0
        rebate = ''
        if unpaid:
            total_unpaid = unpaid[-1]['PAYABLE AMOUNT ']
            due_bill_of = ", ".join([str(month["DUE BILL OF"]) for month in unpaid if month["DUE BILL OF"] != None])
            consumed_units = self.getConsumedUnits(unpaid)
            rebate = unpaid[0]['REBATE']
            rate = unpaid[0]['RATE']
            # return {"advance": advance, "unpaid": unpaid, "total_unpaid": total_unpaid}
        return { 
            "advance": advance, 
            "unpaid": unpaid, 
            "total_unpaid": round(abs(float(total_unpaid)), 2), 
            "paid": paid, 
            "total_advance": round(abs(float(total_advance)), 2),
            "paid_up_to": paid_up_to,
            "due_bill_of": self.parseDue(due_bill_of),
            "consumed_units": consumed_units,
            "rate": rate,
            "rebate": rebate
        }
    
    def parseState(self, unpaid = 0, advance = 0):
        res = ''
        unpaid = round(abs(float(unpaid)), 2)
        advance = round(abs(float(advance)), 2)
        # pprint(advance)
        if unpaid > 0:
            if advance > 0:
                res = UNPAID_ADVANCE_MSG.format(nep_num(unpaid), nep_num(advance))
            else:
                res = UNPAID_MSG.format(nep_num(unpaid))
        else:
            if advance > 0:
                res = ADVANCE_MSG.format(nep_num(advance))
            else:
                res = PAID_MSG
        # pprint(res)
        return res

    def formatBill(self, billData):
        if billData['records'] > 0:
            bill = Bill(
                name = billData['name'],
                # description = None,
                raw_data = billData,
                state = self.parseState(advance = billData['total_advance'], unpaid = billData['total_unpaid']),
                status = "UNPAID" if len(billData['unpaid']) > 0 else "ADVANCE" if len(billData['advance']) > 0 else "No Bills No Advance",
                consumer_name = billData['consumer_detail']['customer_name'],
                sc_no = billData['consumer_detail']['sc_no'],
                counter = billData['consumer_detail']['counter'],
                consumer_id = int(billData['consumer_detail']['consumer_id']),
                bill_from = billData['from'],
                bill_to = billData['to'],
                paid_up_to = billData['paid_up_to'],
                advance = billData['total_advance'],
                unpaid = billData['total_unpaid'],
                due_bill_of = billData['due_bill_of'],
                records = billData['records'],
                consumed_units = billData['consumed_units'],
                rebate = billData['rebate'],
                rate = billData['rate']
            )
        else:
            bill = Bill(
                name = billData['name'],
                # description = None,
                raw_data = billData,
                state = NO_TRANSACTION_MSG,
                status = "NO TRANSACTIONS FOUND!",
                bill_from = billData['from'],
                bill_to = billData['to'],
                records = billData['records']
                # consumer_name = billData['consumer_detail']['customer_name'],
                # sc_no = billData['consumer_detail']['sc_no'],
                # counter = billData['consumer_detail']['counter'],
                # consumer_id = int(billData['consumer_detail']['consumer_id'])
            )

        return bill

    def parsePaidUpTo(self, paid_str):
        res = re.search("\d+-\d+|\d+-\d+-\d+", paid_str)
        if not res:
            return "Not Paid!"
        res = parseDate(res.group())
        return res

    def parseBill(self, html_text, trans = False, name = "NEA Bill"):
        billData = {}
        billSoup = BeautifulSoup(html_text, 'html.parser')
        table_rows = billSoup.table.find_all('tr')
        from_to = table_rows[1].find('th').string
        from_to = self.parseFromTo(from_to)
        billData['name'] = name
        billData['from'] = from_to['from']
        billData['to'] = from_to['to']
        billData['records'] = table_rows[4].text.strip('\n')
        if billData['records'] == "No Records Found.":
            billData['records'] = 0
            return self.formatBill(billData)
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
        billData['records'] = len(transactions) - 1
        bill_status = self.parseBillData(transactions)
        billData['advance'] = bill_status['advance']
        billData['unpaid'] = bill_status['unpaid']
        if trans:
            billData['paid'] = bill_status['paid']
        billData['paid_up_to'] = self.parsePaidUpTo(bill_status['paid_up_to'])
        billData['due_bill_of'] = bill_status['due_bill_of']
        billData['total_unpaid'] = bill_status['total_unpaid']
        billData['total_advance'] = bill_status['total_advance']
        billData['consumed_units'] = bill_status['consumed_units']
        billData['rebate'] = bill_status['rebate']
        billData['rate'] = bill_status['rate']
        return self.formatBill(billData)

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
            bill = self.parseBill(result.text, trans = transactions, name = meter['name'])
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
        elif meter == "amita":
            meter_data = self.amita_meter
        elif meter == "puja":
            meter_data = self.puja_meter
        elif meter == "old":
            meter_data = self.agri_meter_old
        else:
            meter_data = self.agri_meter
        
        result = self.session.post(self.result_url, headers=self.headers, data=meter_data)
        bill = self.parseBill(result.text, trans = transactions, name = meter_data['name'])
        return bill

    def getBillOf(self, meter, transctions = False):
        #init Date and Session Variables
        self.initDateAndSession()

        #getting home page and extracting locations
        home = self.session.get(self.home_url, headers = self.headers)

        locations = self.parseLocations(home.text)

        #getting bills info for each meter
        result = self.session.post(self.result_url, headers=self.headers, data=meter)
        bill = self.parseBill(result.text, trans = transctions, name = meter['name'])
        return bill