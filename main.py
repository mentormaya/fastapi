import os
from typing import Optional
from fastapi import FastAPI
import uvicorn
import random

from Scrapers.NEA.Bills import ScraperNEA

app = FastAPI()

@app.get("/")
def home():
    return {"Hello": "World from FastAPI with Railway Server"}

# get random number between min(default:0) and max(default:9)
@app.get("/nea/v1/")
def get_bills(min: Optional[int] = 0, max: Optional[int] = 9):
    nea = ScraperNEA()
    bills = nea.getBills()
    return bills

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", default=5000)), log_level="info", reload=True)
