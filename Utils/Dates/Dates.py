NEPALI_MONTHS_ENG = ["Baishakh", "Jestha", "Asar", "Shrawan", "Bhadau", "Ashoj", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"]
NEPALI_MONTHS_NEP = ["बैशाख", "जेष्ठ", "असार", "श्रावन", "भदौ", "असोज", "कार्तिक", "मङ्सिर", "पौष", "माघ", "फाल्गुन", "चैत्र"]

def eng_to_nep_month(month):
    if not month:
        return ""
    mnth = NEPALI_MONTHS_NEP[NEPALI_MONTHS_ENG.index(month)]
    return mnth

def get_nep_month(month):
    index = int(month)
    return NEPALI_MONTHS_NEP[index - 1]