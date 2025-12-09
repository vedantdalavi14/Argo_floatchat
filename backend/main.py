from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import glob
import os
import math
from typing import List, Optional

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dataframe
df = pd.DataFrame()

def load_data():
    global df
    path = r"C:\Users\vedan\OneDrive\Desktop\Mini Project\dataset_2024\profile_2024"
    all_files = glob.glob(os.path.join(path, "*.csv"))
    
    df_list = []
    for filename in all_files:
        temp_df = pd.read_csv(filename)
        df_list.append(temp_df)
    
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        # Parse date
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
        df['month'] = df['date'].dt.month
        # Sort by date
        df = df.sort_values('date')
    else:
        print("No CSV files found!")

# Load data on startup
load_data()

@app.get("/")
def read_root():
    return {"message": "FloatChat API Ready", "data_count": len(df)}

@app.get("/api/reload")
def reload_data_endpoint():
    """Reloads the CSV data from disk."""
    load_data()
    return {"message": "Data reloaded successfully", "data_count": len(df)}

@app.get("/api/track")
def get_track(months: Optional[List[int]] = Query(None)):
    """Returns lat, lon, date for mapping."""
    if df.empty:
        return []
        
    filtered_df = df.copy()
    if months:
        filtered_df = filtered_df[filtered_df['month'].isin(months)]
        
    # Drop NaNs in loc
    temp = filtered_df[['avg_latitude', 'avg_longitude', 'date']].dropna()
    # Sort by date to ensure correct path order
    temp = temp.sort_values('date')
    
    # Return as list of dicts
    return temp.to_dict(orient='records')

@app.get("/api/timeseries/{parameter}")
def get_timeseries(parameter: str, months: Optional[List[int]] = Query(None)):
    """
    Returns time series for a specific parameter.
    Parameters: temp, sal, sound, density, freezing, conductivity
    """
    if df.empty:
        return {"labels": [], "datasets": []}
    
    # Filter by month
    filtered_df = df.copy()
    if months:
        filtered_df = filtered_df[filtered_df['month'].isin(months)]
        
    filtered_df = filtered_df.sort_values('date')
    
    # Map parameter key to CSV columns
    col_map = {
        "temp": "avg_temp",
        "sal": "avg_sal",
        "sound": "avg_sound",
        "density": "avg_density",
        "freezing": "avg_freezing",
        "conductivity": "avg_conductivity"
    }
    
    base_col = col_map.get(parameter)
    if not base_col:
        return {"error": "Invalid parameter"}
        
    surface_col = f"{base_col}_surface"
    deep_col = f"{base_col}_deep"
    overall_col = f"{base_col}_overall"
    
    return {
        "labels": filtered_df['date'].dt.strftime('%Y-%m-%d').tolist(),
        "datasets": [
            {
                "label": "Surface",
                "data": filtered_df[surface_col].fillna(0).tolist(),
                "borderColor": "#ef4444", # Red
                "backgroundColor": "#ef4444",
            },
            {
                "label": "Deep",
                "data": filtered_df[deep_col].fillna(0).tolist(),
                "borderColor": "#38bdf8", # Blue
                "backgroundColor": "#38bdf8",
            },
            {
                "label": "Overall",
                "data": filtered_df[overall_col].fillna(0).tolist(),
                "borderColor": "#4ade80", # Green
                "backgroundColor": "#4ade80",
            }
        ]
    }

@app.get("/api/stats")
def get_stats(parameter: str = "temp", layer: str = "overall", months: Optional[List[int]] = Query(None)):
    """
    Returns aggregated stats for the filtered period, parameter, and layer.
    layer: 'overall', 'surface', 'deep'
    """
    if df.empty:
        return {}
        
    filtered_df = df.copy()
    if months:
        filtered_df = filtered_df[filtered_df['month'].isin(months)]
    
    # Base column map (prefix only)
    col_map = {
        "temp": "avg_temp",
        "sal": "avg_sal",
        "sound": "avg_sound",
        "density": "avg_density",
        "freezing": "avg_freezing",
        "conductivity": "avg_conductivity"
    }
    
    base_col = col_map.get(parameter)
    if not base_col:
        return {"error": "Invalid parameter"}
        
    # Construct target column based on layer
    # e.g., avg_temp_overall, avg_temp_surface
    target_col = f"{base_col}_{layer}"
    
    if target_col not in filtered_df.columns:
         return {"error": f"Column {target_col} not found"}

    series = filtered_df[target_col]
    
    if series.empty:
         return {"avg": 0, "max": 0, "min": 0, "range": 0, "count": 0}

    return {
        "avg": round(series.mean(), 2),
        "max": round(series.max(), 2),
        "min": round(series.min(), 2),
        "range": round(series.max() - series.min(), 2),
        "count": len(filtered_df)
    }

@app.get("/api/table")
def get_table_data(
    page: int = 1, 
    limit: int = 20, 
    sort_by: str = "date", 
    sort_order: str = "asc",
    months: Optional[List[int]] = Query(None)
):
    """
    Returns paginated data for the table view.
    """
    if df.empty:
        return {"data": [], "total": 0, "page": page, "pages": 0}
        
    filtered_df = df.copy()
    
    # Filter by months
    if months:
        filtered_df = filtered_df[filtered_df['month'].isin(months)]
        
    # Sorting
    if sort_by in filtered_df.columns:
        ascending = True if sort_order == "asc" else False
        filtered_df = filtered_df.sort_values(sort_by, ascending=ascending)
        
    # Pagination
    total_records = len(filtered_df)
    total_pages = math.ceil(total_records / limit)
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    if start_idx >= total_records:
        return {"data": [], "total": total_records, "page": page, "pages": total_pages}
        
    paginated_df = filtered_df.iloc[start_idx:end_idx]
    
    # NaN replacement for JSON compliance
    paginated_df = paginated_df.fillna(0) # Or replace with null if preferred, but 0 is safer for charts/tables sometimes
    
    # Convert date to string for JSON
    paginated_df['date'] = paginated_df['date'].dt.strftime('%Y-%m-%d')
    
    return {
        "data": paginated_df.to_dict(orient="records"),
        "total": total_records,
        "page": page,
        "pages": total_pages
    }

@app.get("/api/download")
def download_data(months: Optional[List[int]] = Query(None)):
    """
    Downloads the filtered dataset as a CSV file.
    """
    from fastapi.responses import StreamingResponse
    import io

    if df.empty:
        return {"error": "No data available"}
        
    filtered_df = df.copy()
    
    # Filter by months
    if months:
        filtered_df = filtered_df[filtered_df['month'].isin(months)]
        
    filtered_df = filtered_df.sort_values('date')
    
    # Select user-friendly columns if desired, or dump all
    # Let's dump the aggregated columns we use in the table + date
    # Or just dump the whole thing. Let's dump key columns to be clean.
    columns_to_export = [
        'date', 'month', 
        'avg_temp_overall', 'avg_sal_overall', 
        'avg_sound_overall', 'avg_density_overall', 
        'avg_conductivity_overall',
        'avg_latitude', 'avg_longitude'
    ]
    
    # Ensure columns exist
    valid_cols = [c for c in columns_to_export if c in filtered_df.columns]
    export_df = filtered_df[valid_cols]
    
    # Stream response
    stream = io.StringIO()
    export_df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=argo_float_data.csv"
    
    return response

# Chat Logic
from pydantic import BaseModel
import re
import os
from dotenv import load_dotenv
from mistralai import Mistral  # Updated SDK import
from pathlib import Path

# Explicitly load .env from the backend directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
mistral_client = None

if MISTRAL_API_KEY:
    try:
        mistral_client = Mistral(api_key=MISTRAL_API_KEY)
        print("Mistral API Key loaded successfully.")
    except Exception as e:
        print(f"Error initializing Mistral client: {e}")
else:
    print(f"Warning: Mistral API Key not found at {env_path}")

class ChatRequest(BaseModel):
    message: str

month_map = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

@app.post("/api/chat")
async def chat_with_data(request: ChatRequest):
    """
    Hybrid Chat: Uses Mistral LLM if available, falls back to keyword matching.
    """
    print(f"DEBUG: Processing chat request... Client exists: {mistral_client is not None}")
    msg = request.message.lower()
    
    # --- LLM Integration ---
    if mistral_client and not df.empty:
        try:
            # 1. Identify relevant data subset based on keywords
            # If valid months mentioned, filter by them
            found_months = []
            for name, num in month_map.items():
                if re.search(r'\b' + name + r'\b', msg):
                    if num not in found_months: found_months.append(num)
            
            context_df = df.copy()
            if found_months:
                 context_df = context_df[context_df['month'].isin(found_months)]
            
            # Select relevant columns to reduce token usage
            cols_to_use = ['date', 'month', 'avg_latitude', 'avg_longitude']
            
            # Add specific parameter columns
            include_all = "all" in msg or "compare" in msg or "diff" in msg
            if include_all or "temp" in msg: cols_to_use.append('avg_temp_overall')
            if include_all or "salinity" in msg or "salt" in msg: cols_to_use.append('avg_sal_overall')
            if include_all or "density" in msg: cols_to_use.append('avg_density_overall')
            if include_all or "oxygen" in msg: cols_to_use.append('avg_doxy_overall')
            
            # If generic query, fallback to key status columns
            if len(cols_to_use) == 4: # Only base cols added
                 cols_to_use.extend(['avg_temp_overall', 'avg_sal_overall'])

            # Limit rows
            data_context = context_df[cols_to_use].to_csv(index=False)
            
            prompt = f"""
            You are an oceanography data assistant. 
            Context Data (CSV format):
            {data_context}
            
            User Question: {request.message}
            
            Instructions:
            - If the question is about a concept (e.g., "What is this, where this can be any paramtere or related to oceanography?"), briefly define it first.
            - Then, analyze the provided data to answer specific to the dataset.
            - Be precise with numbers.
            - If comparing, calculate valid differences.
            - Keep answer concise.
            - IMPORTANT: Format your response clearly using Markdown.
            - Use Bullet points for lists.
            - Use Bold for key numbers.
            - Use Headers (##) for sections.
            """
            
            chat_response = mistral_client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return {"reply": chat_response.choices[0].message.content}
            
        except Exception as e:
            print(f"LLM Error: {e}")
            return {"reply": f"AI Error details: {str(e)}"}
            
    if not MISTRAL_API_KEY:
        return {"reply": "Mistral API Key is missing. Please configure backend/.env with MISTRAL_API_KEY."}

    return {"reply": "I couldn't process that query or no data context was found."}
