from fastapi import FastAPI
from .schemas import UsersData
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from .crud import process_data, cluster_users, calculate_weighted_matrices,categorize_time_of_day,categorize_weekday_vs_weekend,categorize_venue_preference
import json
from datetime import datetime
from fastapi import HTTPException
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from .visualization import plot_clusters, label_clusters,plot_time_of_day_categories,plot_venue_preference_categories,plot_weekday_vs_weekend_categories,graph_clusters,plot_visualize


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.get("/cluster")
def get_clusters():
    """
    STEP 1 : visualize users' data on plot(s) and try to understand the scope of given data.
    STEP 2 : group users based on their visiting behavior of different types of venues and different datetime of a month.
    """
    try:
        with open("app/data/data_20.json", "r") as file:
            data = json.load(file)

        for user, visits in data.items():
            for visit in visits:
                visit['ts'] = datetime.strptime(visit['ts'], '%Y-%m-%d %H:%M:%S.%f')

        user_vectors = process_data(data)
        clusters = cluster_users(user_vectors)

        venue_types = ["pub", "wine", "bar", "pastery", "cafe"]
        time_buckets = ["morning", "afternoon", "evening", "night"]
        graph_clusters(clusters, user_vectors, venue_types, time_buckets)

        return JSONResponse(content=clusters, status_code=200)
    except Exception as e:
        print(f"Error in clustering: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visualize")
def visualize():
    """
    STEP 1 : Visualizes user visit data over time using a pie chart.
    export file : app/visuals/visualize-data.png
    """
    try:
        with open("app/data/data_20.json", "r") as file:
            data = json.load(file)
            
        user_visits = defaultdict(list)

        for user, visits in data.items():
            for visit in visits:
                timestamp = visit['ts'] if isinstance(visit['ts'], datetime) else datetime.strptime(visit['ts'], '%Y-%m-%d %H:%M:%S.%f')
                user_visits[user].append((visit['venue_type'], timestamp))

        # Kullanıcıların ziyaretlerini kategorilendirme (örneğin, sadece ilk ziyaret türüne göre)
        user_categories = {}
        for user, visits in user_visits.items():
            first_visit = visits[0][0] if visits else None
            user_categories[user] = first_visit
        
        # Kategori sayımlarını yapma
        category_counts = defaultdict(int)
        for category in user_categories.values():
            category_counts[category] += 1
        
        # Veriyi grafik için hazırlama
        categories = list(category_counts.keys())
        counts = list(category_counts.values())

        # Pasta grafiği oluşturma
        plot_visualize(counts,categories)

        # plt.figure(figsize=(10, 8))
        # plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140)
        # plt.title('User Visit Categories')
        # plt.savefig("app/visuals/visualize-data.png")

        return JSONResponse(content={"message": "Visualization created"}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  


@app.get("/weighted-cluster")
def perform_weighted_cluster():
    """
    STEP 3 : Performs weighted clustering on user visit data and visualizes the results.
    export file : app/visuals/weighted_clusters.png
    """
    try:
        with open("app/data/data_20.json", "r") as file:
            data = json.load(file)

        for user, visits in data.items():
            for visit in visits:
                visit["ts"] = datetime.strptime(visit["ts"], '%Y-%m-%d %H:%M:%S.%f')

        weighted_matrices = calculate_weighted_matrices(data)
        clusters = cluster_users(weighted_matrices)
        
        venue_types = ["pub", "wine", "bar", "pastery", "cafe"]
        cluster_labels = label_clusters(clusters, weighted_matrices, venue_types)
        plot_clusters(clusters, weighted_matrices, cluster_labels)

        return JSONResponse(content={"message": "Weighted Cluster Visualization created"}, status_code=200)

    except Exception as e:
        print(f"Error in weighted clustering: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/visualize-categories")
def visualize_categories():
    """
    STEP 4 : Retrieves user visit data from 'app/data/data_20.json', categorizes users based on their visit patterns
    including time of day, weekday vs weekend preferences, and venue types. Generates visualizations for each
    category and saves them as images. Returns a success message upon completion or raises a server error if
    any issues occur during the process.

    export file : app/visuals/time_of_day_categories.png
    export file : app/visuals/weekday_vs_weekend_categories.png
    export file : app/visuals/venue_preference_categories.png

    """
    try:
        with open("app/data/data_20.json", "r") as file:
            data = json.load(file)
        

        time_of_day_categories = categorize_time_of_day(data)
        weekday_weekend_categories = categorize_weekday_vs_weekend(data)
        venue_types = ["pub", "wine", "bar", "pastery", "cafe"]
        venue_preference_categories = categorize_venue_preference(data, venue_types)

        plot_time_of_day_categories(time_of_day_categories)
        plot_weekday_vs_weekend_categories(weekday_weekend_categories)
        plot_venue_preference_categories(venue_preference_categories)

        return JSONResponse(content={"message": "Category visualizations created"}, status_code=200)

    except Exception as e:
        print(f"Error in visualizing categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categorize-users")
def categorize_users():
    """
    STEP 4
    """
    try:
        # Load data from file (you may have your own data loading mechanism)
        with open("app/data/data_20.json", "r") as file:
            data = json.load(file)

        # Assume these functions are defined earlier in your code
        time_of_day_categories = categorize_time_of_day(data)
        weekday_vs_weekend_categories = categorize_weekday_vs_weekend(data)
        venue_preference_categories = categorize_venue_preference(data, ["pub", "wine", "bar", "pastery", "cafe"])

        # Combine categories for each user
        categorized_users = {}
        for user in data.keys():
            categorized_users[user] = {
                "time_of_day": time_of_day_categories.get(user, "Unknown"),
                "weekday_vs_weekend": weekday_vs_weekend_categories.get(user, "Unknown"),
                "venue_preference": venue_preference_categories.get(user, "Unknown")
            }

        return categorized_users

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
