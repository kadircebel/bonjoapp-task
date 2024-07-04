import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np
from typing import Dict, List


def label_clusters(clustered_users: Dict[int, List[str]], user_vectors: Dict[str, np.ndarray], venue_types: List[str]) -> Dict[int, str]:
    cluster_labels = {}
    for cluster_id, users in clustered_users.items():
        cluster_vector = np.mean([user_vectors[user] for user in users], axis=0)
        dominant_venue_index = np.argmax(cluster_vector)
        dominant_venue_type = venue_types[dominant_venue_index]
        cluster_labels[cluster_id] = f"{dominant_venue_type.capitalize()} Lovers"
    return cluster_labels


def graph_clusters(clustered_users: Dict[int, List[str]], user_vectors: Dict[str, np.ndarray], venue_types: List[str], time_buckets: List[str]):
    num_clusters = len(clustered_users)
    fig, axes = plt.subplots(nrows=num_clusters, ncols=1, figsize=(15, 6 * num_clusters), sharex=True)
    
    if num_clusters == 1:
        axes = [axes]
    
    for i, (cluster_id, users) in enumerate(clustered_users.items()):
        cluster_matrix = np.zeros((len(venue_types), len(time_buckets)))
        
        for user in users:
            vector = user_vectors[user].reshape(len(venue_types), len(time_buckets))
            cluster_matrix += vector
        
        sns.heatmap(cluster_matrix, ax=axes[i], cmap="YlGnBu", xticklabels=time_buckets, yticklabels=venue_types)
        axes[i].set_title(f"Cluster {cluster_id}")

    plt.tight_layout()
    plt.savefig("app/visuals/clusters_heatmap.png")
    plt.close()

def plot_clusters(clustered_users: Dict[int, List[str]], user_vectors: Dict[str, np.ndarray], cluster_labels: Dict[int, str]):
    cluster_data = defaultdict(list)
    user_labels = defaultdict(list)
    
    for cluster_id, users in clustered_users.items():
        for user in users:
            cluster_data[cluster_id].append(user_vectors[user])
            user_labels[cluster_id].append(user)

    fig, axes = plt.subplots(nrows=1, ncols=len(cluster_data), figsize=(15, 5), sharey=True)
    if len(cluster_data) == 1:
        axes = [axes]

    for i, (cluster_id, vectors) in enumerate(cluster_data.items()):
        labels, counts = np.unique(user_labels[cluster_id], return_counts=True)
        axes[i].pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
        axes[i].set_title(cluster_labels[cluster_id])

    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.tight_layout()
    plt.savefig("app/visuals/weighted_clusters.png")
    plt.close()


def plot_time_of_day_categories(categories: Dict[str, str]):
    labels, counts = np.unique(list(categories.values()), return_counts=True)
    plt.figure(figsize=(8, 6))
    sns.barplot(x=labels, y=counts)
    plt.title('Günlük ve Gece Ziyaretleri Kategorileri')
    plt.xlabel('Kategori')
    plt.ylabel('Kullanıcı Sayısı')
    plt.savefig('app/visuals/time_of_day_categories.png')
    plt.close()

def plot_visualize(counts,categories):
    plt.figure(figsize=(10, 8))
    plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('User Visit Categories')
    plt.savefig("app/visuals/visualize-data.png")

def plot_weekday_vs_weekend_categories(categories: Dict[str, str]):
    labels, counts = np.unique(list(categories.values()), return_counts=True)
    plt.figure(figsize=(8, 6))
    sns.barplot(x=labels, y=counts)
    plt.title('Hafta İçi ve Hafta Sonu Ziyaretleri Kategorileri')
    plt.xlabel('Kategori')
    plt.ylabel('Kullanıcı Sayısı')
    plt.savefig('app/visuals/weekday_vs_weekend_categories.png')
    plt.close()

def plot_venue_preference_categories(categories: Dict[str, str]):
    labels, counts = np.unique(list(categories.values()), return_counts=True)
    plt.figure(figsize=(8, 6))
    sns.barplot(x=labels, y=counts)
    plt.title('Mekan Türü Tercihleri Kategorileri')
    plt.xlabel('Mekan Türü')
    plt.ylabel('Kullanıcı Sayısı')
    plt.savefig('app/visuals/venue_preference_categories.png')
    plt.close()

