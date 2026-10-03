"""
FastAPI Dashboard & Data Explorer
Relu Consultancy Data Extraction Challenge - Bonus Objective

Provides an interactive search, filtering, and analytics dashboard
over both Disney Cruise and Ingredients Network datasets.
Supports local CSV fallback and Supabase database connectivity.
"""

import os
import json
import logging
from typing import Optional
import pandas as pd
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Relu Data Extraction Dashboard", version="1.0.0")

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Data loader helper
def load_disney_df():
    path = os.path.join(OUTPUT_DIR, "disney_cruises.csv")
    if os.path.exists(path):
        return pd.read_csv(path).fillna("")
    return pd.DataFrame()

def load_ingredients_df():
    path = os.path.join(OUTPUT_DIR, "ingredients_network.csv")
    if os.path.exists(path):
        return pd.read_csv(path).fillna("")
    return pd.DataFrame()

def load_analysis_results():
    path = os.path.join(OUTPUT_DIR, "analysis_results.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    stats = load_analysis_results()
    disney_df = load_disney_df()
    ingredients_df = load_ingredients_df()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "disney_count": len(disney_df),
        "ingredients_count": len(ingredients_df),
    })


@app.get("/api/disney")
async def get_disney(
    search: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100)
):
    df = load_disney_df()
    if df.empty:
        return {"data": [], "total": 0, "page": page, "limit": limit}

    if search:
        mask = (
            df["cruise_title"].str.contains(search, case=False, na=False) |
            df["ship"].str.contains(search, case=False, na=False) |
            df["departure_port"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    if destination:
        df = df[df["destination_clean"].str.contains(destination, case=False, na=False)]

    total = len(df)
    start = (page - 1) * limit
    end = start + limit
    sliced = df.iloc[start:end].to_dict(orient="records")

    return {
        "data": sliced,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 1
    }


@app.get("/api/ingredients")
async def get_ingredients(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(15, ge=1, le=100)
):
    df = load_ingredients_df()
    if df.empty:
        return {"data": [], "total": 0, "page": page, "limit": limit}

    if search:
        mask = (
            df["company_name"].str.contains(search, case=False, na=False) |
            df["company_description"].str.contains(search, case=False, na=False) |
            df["primary_business_activity"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    if category:
        df = df[df["categories"].str.contains(category, case=False, na=False)]

    total = len(df)
    start = (page - 1) * limit
    end = start + limit
    sliced = df.iloc[start:end].to_dict(orient="records")

    return {
        "data": sliced,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 1
    }


@app.get("/api/stats")
async def get_stats():
    return JSONResponse(content=load_analysis_results())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
