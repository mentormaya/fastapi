import os
from tokenize import String
from typing import Dict, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


from Scrapers.NEA.Bills import ScraperNEA
from Scrapers.PAN.Pan import PANDetails
from Utils.Numbers.Numbers import Number

app = FastAPI()

nea = ScraperNEA()

pan = PANDetails()


class Meter(BaseModel):
    name: str
    desciption: str
    NEA_Location: str
    sc_no: str
    consumer_id: str
    Fromdatepicker: str
    Todatepicker: str

@app.get("/")
def home():
    return {"Hello": "World from FastAPI with Railway Server"}

# get random number between min(default:0) and max(default:9)
@app.get("/nea/v1/")
def get_bills():
    bills = nea.getBills()
    return bills

# get electricity bills for domestic/agri meter with parameter in url
@app.get("/nea/v1/{meter}")
def get_bill(meter: Optional[str]):
    bills = nea.getBill(meter = meter)
    return bills

# get electricity bills for domestic/agri meter with parameter in url
@app.post("/nea/v1/bill")
def get_bill_of(meter: Meter):
    bills = nea.getBillOf(meter = meter.dict())
    return bills

# get details of the PAN information with parameter in url
@app.get("/pan/v1/{pan_no}")
def get_pan_details(pan_no: int):
    details = pan.getDetails(pan_no)
    return details

# Utility REST API endpoint for converting any number in to nepali number
@app.get("/utilities/v1/numbers/nep_num/{num}")
def nepali_number(num):
    res = Number(num = num)
    return res.get_num()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", default=3000)), log_level="info", reload=True)
