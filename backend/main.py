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
