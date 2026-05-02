import mlflow
import os

def init_mlflow():
    """
    Utility to initialize MLflow tracking.
    """
    mlflow.set_tracking_uri(f"sqlite:///mlflow.db")
    mlflow.set_experiment("RAG_Bootcamp_Experiments")
    print(f"[INFO] MLflow Initialized. Tracking to: {mlflow.get_tracking_uri()}")

if __name__ == "__main__":
    init_mlflow()
