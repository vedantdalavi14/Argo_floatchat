# FloatChat: ARGO Data Intelligence Platform

FloatChat is an interactive web application designed to visualize and analyze oceanographic data from ARGO floats. It combines interactive mapping, advanced charting, and an AI-powered chat interface to provide deep insights into ocean parameters like temperature, salinity, and oxygen levels.

![Project Banner](https://argo.ucsd.edu/wp-content/uploads/sites/361/2020/06/Argo_logo.png)

## 🚀 Features

### 1. Interactive Dashboard
-   **Depth Profiles**: Visualize how temperature and salinity change at different ocean depths (Surface vs. Deep).
-   **Time-Series Charts**: Track trends over time with dynamic line charts using **Chart.js**.
-   **Statistical Analysis**: Real-time calculation of Min, Max, Average, and Range for selected parameters.

### 2. Geospatial Visualization
-   **Live Tracking**: Interactive Map (Leaflet) showing the float's path across the Indian Ocean.
-   **Waypoints**: Visual markers indicating recording stations with precise coordinates.
-   **Month Filtering**: Filter the map track by specific months to analyze seasonal movements.

### 3. AI-Powered Chat with Data
-   **Mistral AI Integration**: Ask natural language questions like *"What is the salinity trend in May?"*.
-   **Context-Aware**: The system intelligently filters the dataset based on your query (e.g., month, parameter) and sends only relevant context to the LLM.
-   **Rich Text Responses**: Get structured answers with bullet points, bold text, and headers directly in the chat.

### 4. Data Management
-   **Tabular View**: Explore the raw dataset in a paginated, sortable table.
-   **Export**: Download filtered datasets as CSV files for offline analysis.

---

## 🛠️ Tech Stack

### Frontend
-   **React (Vite)**: Fast, modern UI framework.
-   **Leaflet (React-Leaflet)**: For interactive maps.
-   **Chart.js (React-Chartjs-2)**: For beautiful data visualization.
-   **React-Markdown**: For rendering rich AI responses.
-   **CSS Variables**: For a consistent, dark-themed premium aesthetic.

### Backend
-   **FastAPI**: High-performance Python web framework.
-   **Pandas**: For powerful CSV data manipulation and filtering.
-   **Mistral AI SDK**: For Generative AI capabilities.
-   **Uvicorn**: ASGI server for running the API.

---

## ⚙️ Setup Instructions

### Prerequisites
-   **Node.js** (v16+)
-   **Python** (v3.9+)
-   **Mistral AI API Key** (Get one from [console.mistral.ai](https://console.mistral.ai/))

### 1. Clone the Repository
```bash
git clone https://github.com/vedantdalavi14/Argo_floatchat.git
cd Argo_floatchat
``` 

### 2. Backend Setup
Navigate to the backend folder and install dependencies:
```bash
cd backend
python -m pip install -r requirements.txt
```

**Configure API Key:**
1.  Create a file named `.env` in the `backend/` directory.
2.  Add your Mistral Key:
    ```env
    MISTRAL_API_KEY=your_actual_api_key_here
    ```

**Start the Server:**
```bash
python -m uvicorn main:app --reload --port 8000
```
*The backend runs on http://localhost:8000*

### 3. Frontend Setup
Open a new terminal, navigate to the frontend folder, and install dependencies:
```bash
cd frontend
npm install
```

**Start the Application:**
```bash
npm run dev
```
*The frontend runs on http://localhost:5173*

---

## 📖 How to Use

1.  **Dashboard**: Use the dropdowns to switch between Temperature, Salinity, and Oxygen charts. Toggle "Surface" or "Deep" layers.
2.  **Map**: Click "Show Map" to see the float's journey. Use the "Filter Month" dropdown to isolate specific time periods.
3.  **Chat**: Click the Hexagon icon in the sidebar. Ask questions like:
    - *"Where was the float in March?"*
    - *"Compare temperature between Jan and Feb."*
    - *"What is the average salinity?"*
4.  **Data**: Go to the "Data" tab to view the raw numbers and download reports.

---

## 🤝 Contributing
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request
