from datetime import datetime
from collections import defaultdict
from typing import Dict, List
from sklearn.cluster import KMeans
import numpy as np
from .schemas import Visit 

def process_data(data: Dict[str, List[Dict]]) -> Dict[str, np.ndarray]:
    venue_types = ["pub", "wine", "bar", "pastery", "cafe"]
    num_venue_types = len(venue_types)
    time_buckets = ["morning", "afternoon", "evening", "night"]
    num_time_buckets = len(time_buckets)

    def get_time_bucket(timestamp):
        hour = timestamp.hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    user_vectors = {}

    for user, visits in data.items():
        vector = np.zeros((num_venue_types, num_time_buckets))
        for visit in visits:
            venue_type = visit['venue_type']
            timestamp = visit['ts']
            time_bucket = get_time_bucket(timestamp)
            if venue_type in venue_types:
                venue_idx = venue_types.index(venue_type)
                time_idx = time_buckets.index(time_bucket)
                vector[venue_idx, time_idx] += 1
        user_vectors[user] = vector.flatten()

    return user_vectors

def cluster_users(user_vectors: Dict[str, np.ndarray], n_clusters: int = 3):
    try:
        vectors = list(user_vectors.values())
        vectors = np.array(vectors) 

        kmeans = KMeans(n_clusters=n_clusters)
        kmeans.fit(vectors)
        labels = kmeans.labels_.tolist()

        clustered_users = defaultdict(list)
        for label, user in zip(labels, user_vectors.keys()):
            clustered_users[label].append(user)

        return clustered_users

    except Exception as e:
        print(f"Error in clustering: {e}")
        return None
    
# Calculate weighted visit matrices
def calculate_weighted_matrices(data: Dict[str, List[Visit]]) -> Dict[str, np.ndarray]:
    weighted_matrices = defaultdict(lambda: np.zeros(len(data.values())))

    # Define the weight calculation mechanism (weekly weights as an example)
    current_week = None
    current_weight = 1

    for user, visits in data.items():
        for visit in visits:
            # Determine the week of the visit
            visit_week = visit['ts'].isocalendar()[1]
                        
            if current_week is None:
                current_week = visit_week
            elif current_week != visit_week:
                current_week = visit_week
                current_weight += 1

            venue_types = ["pub", "wine", "bar", "pastery", "cafe"]
            # Apply the weight to the corresponding venue type
            venue_type_index = venue_types.index(visit["venue_type"])
            weighted_matrices[user][venue_type_index] += current_weight

    return weighted_matrices

def categorize_time_of_day(data: Dict[str, List[Dict]]) -> Dict[str, str]:
    categories = {}
    for user, visits in data.items():
        day_visits = 0
        night_visits = 0
        for visit in visits:

            timestamp = datetime.strptime(visit["ts"], '%Y-%m-%d %H:%M:%S.%f')
            hour = timestamp.hour

            if hour >= 6 and hour < 18:
                day_visits += 1
            else:
                night_visits += 1
        if day_visits >= night_visits:
            categories[user] = "Güneş Aşığı"
        else:
            categories[user] = "Ay Aşığı"
    return categories

def categorize_weekday_vs_weekend(data: Dict[str, List[Dict]]) -> Dict[str, str]:
    categories = {}
    for user, visits in data.items():
        weekday_visits = 0
        weekend_visits = 0
        for visit in visits:
            timestamp = datetime.strptime(visit["ts"], '%Y-%m-%d %H:%M:%S.%f')
            weekday = timestamp.weekday()
            if weekday < 5:  # Hafta içi günleri 0-4 (Pazartesi-Cuma)
                weekday_visits += 1
            else:  # Hafta sonu günleri 5-6 (Cumartesi-Pazar)
                weekend_visits += 1
        if weekday_visits >= weekend_visits:
            categories[user] = "Hafta İçi Aşığı"
        else:
            categories[user] = "Hafta Sonu Aşığı"
    return categories

def categorize_venue_preference(data: Dict[str, List[Dict]], venue_types: List[str]) -> Dict[str, str]:
    categories = {}
    for user, visits in data.items():
        venue_counts = defaultdict(int)
        for visit in visits:
            venue_type = visit["venue_type"]
            venue_counts[venue_type] += 1
        favorite_venue = max(venue_counts, key=venue_counts.get)
        categories[user] = favorite_venue
    return categories
