from pprint import pprint
from Utils.Utils.Utils import Utils

NEPALI_DIGITS = ["०", "१", "२", "३", "४", "५", "६", "७", "८", "९"]
ONES_PLACES = ["","One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Forteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]
TENS_PLACES = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety", "Hundred"]
MILIONS_PLACES = ["", "Thousand", "Million", "Billion", "Trillion", "Quadritillion"]
LAKH_PLACES_ENG = ["One", "Thousand", "Lakh", "Crore", "Arab", "Kharab", "Nil", "Shankha", "Mahashankha"]
LAKH_PLACES_NEP = ["एक", "हजार", "लाख", "कराेड", "अरब", "खरब", "नील", "शंख", "महाशंख"]
NEPALI_ANKA_ONES = ["एक", "दुइ", "तिन", "चार", "पाँच", "छ", "सात", "आठ", "नाै", "दश", "एघार", "बाह्र", "तेह्र", "चाैद", "पन्ध्र", "साेह्र", "सत्र", "अठार", "उन्नाइस", "बीस"]
NEPALI_ANKA_TENS = ["दश", "बीस", "तीस", "चालिस", "पच्चास", "साठ्ठी", "सत्तरी", "अस्सी", "नब्बे", "सय"]

class Number():
    def __init__(self, num):
        self.num = num
        self.english = num
    
    def string_reverse(self, string = ""):
        if string == "":
            return string
        return string[::-1]

    def group_str(self, string = "", group = 3, nep = False):
        # pprint("group_str input:" + string)
        if string == "":
            return []
        if not nep:
            string = self.string_reverse(string=string)
            return [self.string_reverse(string[i:i+group]) for i in range(0, len(string), group)]
        else:
            ones = [string[-3:len(string)]]
            if len(string) > 3:
                string = self.string_reverse(string[:-3])
                higher = [self.string_reverse(string[i:i+2]) for i in range(0, len(string), 2)]
                return  ones  + higher
            return ones

    def split_number(self):
        if self.num:
            s = str(self.num).split(".")
            pos = str(self.num).find(".")
            if pos < 0 or pos == len(str(self.num)) - 1:
                self.decimal = ""
                self.whole = s[0]
            else:
                self.decimal = s[1]
                self.whole = s[0]
    
    def parseHundreds(self, value = ''):
        if value == '':
            return value
        res = ''
        hundred = ''
        tens = ''
        ones = ''
        if len(value) > 2:
            hundred = value[:1]
            tens = value[1:2]
            ones = value[2:]
        elif len(value) > 1:
            tens = value[:1]
            ones = value[1:]
        else:
            ones = value
        if hundred != '':
            if int(hundred) > 1:
                res = res + ONES_PLACES[int(hundred)] + " hundreds"
            else:
                res = res + ONES_PLACES[int(hundred)] + " hundred"
        if ones != '':
            res = res + " " +  ONES_PLACES[int(ones)]
        if tens != '':
            if int(tens) == 1:
                res = res + " " + ONES_PLACES[int(tens+ones)]
            else:
                res = res + " " + TENS_PLACES[int(tens)]
        return res

    def parseEng(self, value = ''):
        if value == '':
            return value
        value = value.split(",")
        res = ''
        for index, pos in enumerate(value):
            res = res + " " + self.parseHundreds(pos) + " " + MILIONS_PLACES[len(value) - index - 1]
        return res
    
    def parseNep(self, value = ''):
        if value == '':
            return value
        value = value.split(",")
        res = ''
        for index, pos in enumerate(value):
            res = res + " " + self.parseHundreds(pos) + " " + LAKH_PLACES_NEP[len(value) - index - 1]
        return res

    def num2words_eng(self, pre = "Nepali", post = "Only"):
        words = 'No Value!'
        if self.whole:
            words = pre
            num = self.million_format.split(".")
            if self.whole != "" and int(self.whole) > 0:
                rupees = str(num[0])
                words = words + " Rupees " + str(self.parseEng(rupees)).strip()
            if self.decimal != "" and int(self.decimal) > 0:
                paisa = str(num[1])[:2]
                words = words + " and " + str(self.parseEng(paisa)).strip() + " paisa"
            words = words + " " + post
        self.words_eng = words

    def num2words_nep(self, pre = "ने.", post = "मात्र"):
        words = 'No Value!'
        if self.whole:
            words = pre
            num = self.lakh_format.split(".")
            if self.whole != "" and int(self.whole) > 0:
                rupees = str(num[0])
                words = words + "रू. " + str(self.parseNep(rupees)).strip()
            if self.decimal != "" and int(self.decimal) > 0:
                paisa = str(num[1])[:2]
                words = words + " र " + str(self.parseNep(paisa)).strip() + " पैसा"
            words = words + " " + post
        self.words_nep = words 

    def nepali(self):
        if self.num:
            num_rs = Utils.split_characters(word = self.num)
            nep = Utils.join_characters(list_s = [NEPALI_DIGITS[int(lit)] if lit != '.' else '.' for lit in num_rs])
            self.nepali = nep
        else :
            self.nepali = "कुनै नम्बर भेटिएन!"
    
    def lakh_format(self, sep = ","):
        if self.whole != "":
            formatted = self.group_str(string = self.whole, nep = True)
            # pprint("nepali format: " + str(formatted))
            formatted.reverse()
            self.lakh_format = sep.join(formatted)
        else:
            self.lakh_format = ""
        if self.decimal != "" and int(self.decimal) > 1:
            self.lakh_format = self.lakh_format + "." + self.decimal
    
    def million_format(self, sep = ","):
        if self.whole != "":
            formatted = self.group_str(string = self.whole)
            # pprint("english format: " + str(formatted))
            formatted.reverse()
            self.million_format = sep.join(formatted)
        else:
            self.million_format = ""
        if self.decimal != "" and int(self.decimal) > 1:
            self.million_format = self.million_format + "." + self.decimal

    def get_num(self):
        self.nepali()
        self.split_number()
        self.lakh_format()
        self.million_format()
        self.num2words_eng()
        self.num2words_nep()
        return self.__dict__