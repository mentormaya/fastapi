import pprint
from Utils.Utils.Utils import Utils

NEPALI_DIGITS = ["०", "१", "२", "३", "४", "५", "६", "७", "८", "९"]

class Number():
    def __init__(self, num):
        self.num = num
    
    def split_number(self, nepali = True):
        if nepali:
            if self.num:
                s = str(self.num)
                return [s[i:i+3] for i in range(0, len(s), 3)]
        return [s[i:i+3] for i in range(0, len(s), 3)]

    def num2words_eng(self, pre = "Nepali Rupees ", past = " Only"):
        words = 'No Value!'
        if self.num:
            words = pre + self.split_number() + past
        return words       

    def nepali(self):
        num_rs = Utils.split_characters(word = self.num)
        nep = Utils.join_characters(list_s = [NEPALI_DIGITS[int(lit)] if lit != '.' else '.' for lit in num_rs])
        return {
            "nepali": nep,
            "english": self.num,
            "words_eng": self.num2words_eng()
        }