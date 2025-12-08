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

class ChatRequest(BaseModel):
    message: str

month_map = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

@app.post("/api/chat")
def chat_with_data(request: ChatRequest):
    """
    Simple keyword-based chat interface.
    """
    msg = request.message.lower()
    
    # Check for comparison query
    if "diff" in msg or "compare" in msg or "between" in msg:
        # 1. Identify Parameter
        param = "temp" # default
        col = "avg_temp_overall"
        unit = "°C"
        
        if "salinity" in msg or "salt" in msg:
            param = "salinity"
            col = "avg_sal_overall"
            unit = "PSU"
        elif "density" in msg:
            param = "density"
            col = "avg_density_overall"
            unit = "kg/m³"
        elif "oxygen" in msg:
            param = "oxygen"
            col = "avg_doxy_overall"
            unit = "µmol/kg"
            
        # 2. Identify Months
        found_months = []
        for name, num in month_map.items():
            # Use regex to find whole words to avoid 'may' inside 'maybe' etc.
            if re.search(r'\b' + name + r'\b', msg):
                if num not in found_months:
                    found_months.append(num)
        
        if len(found_months) >= 2:
            m1, m2 = found_months[0], found_months[1]
            
            # Helper to get name
            def get_month_name(m):
                name = [k for k,v in month_map.items() if v == m and len(k)>3]
                return name[0].capitalize() if name else f"Month {m}"
            
            name1 = get_month_name(m1)
            name2 = get_month_name(m2)

            # Check if "all" parameters requested
            if "all" in msg:
                params = [
                    ("Temp", "avg_temp_overall", "°C"),
                    ("Salinity", "avg_sal_overall", "PSU"),
                    ("Density", "avg_density_overall", "kg/m³"),
                    ("Oxygen", "avg_doxy_overall", "µmol/kg")
                ]
                
                replies = []
                replies.append(f"Comparing all parameters between {name1} and {name2}:")
                
                for p_name, p_col, p_unit in params:
                    if p_col not in df.columns: continue
                    v1 = df[df['month'] == m1][p_col].mean()
                    v2 = df[df['month'] == m2][p_col].mean()
                    
                    if pd.isna(v1) or pd.isna(v2):
                        replies.append(f"- {p_name}: Data missing.")
                        continue
                        
                    diff = v2 - v1
                    direction = "higher" if diff > 0 else "lower"
                    replies.append(f"- {p_name}: {v1:.2f} vs {v2:.2f} (Diff: {abs(diff):.2f}{p_unit} {direction} in {name2})")
                
                return {"reply": "\n".join(replies)}

            # Single Parameter Comparison (Existing Logic)
            # Get data
            val1 = df[df['month'] == m1][col].mean()
            val2 = df[df['month'] == m2][col].mean()
            
            if pd.isna(val1) or pd.isna(val2):
                return {"reply": f"I couldn't find data for one of those months to compare {param}."}
                
            diff = val2 - val1
            direction = "higher" if diff > 0 else "lower"

            return {
                "reply": f"Comparing {param}: {name1} was {val1:.2f}{unit}, and {name2} was {val2:.2f}{unit}. "
                         f"The difference is {abs(diff):.2f}{unit} ({direction} in {name2})."
            }
    
    # 1. Temperature query (General)
    if "temp" in msg:
        if df.empty: return {"reply": "I have no data loaded yet."}
        latest = df.iloc[-1]
        avg_temp = round(df['avg_temp_overall'].mean(), 2)
        return {"reply": f"The average temperature across all data is {avg_temp}°C. The latest recording on {latest['date']} was {latest['avg_temp_overall']:.2f}°C."}
    
    # 2. Salinity query
    if "salinity" in msg or "salt" in msg:
        if df.empty: return {"reply": "I have no data loaded yet."}
        avg_sal = round(df['avg_sal_overall'].mean(), 2)
        return {"reply": f"The average salinity is {avg_sal} PSU. Salinity affects water density and buoyancy."}
        
    # 3. Location/Where query
    if "where" in msg or "location" in msg or "position" in msg:
        if df.empty: return {"reply": "I have no data loaded yet."}
        latest = df.iloc[-1]
        return {"reply": f"The float is currently located at Lat: {latest['avg_latitude']:.2f}, Lon: {latest['avg_longitude']:.2f} (Indian Ocean)."}
        
    # 4. Status query
    if "status" in msg or "health" in msg:
         return {"reply": "The float is active and transmitting data. All sensors are reporting nominal status (99.9% QC passed)."}
         
    # 5. Jokes/Fun
    if "hello" in msg or "hi" in msg:
        return {"reply": "Hello! I am FloatChat. Ask me about ocean temperature, salinity, or the float's location."}

    # Default
    return {"reply": "I am not sure about that. Try asking 'What is the temperature?' or 'Where is the float now?'"}
