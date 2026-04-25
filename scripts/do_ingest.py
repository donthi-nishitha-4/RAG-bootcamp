import os
import sys

# Add current dir and scripts dir to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from ingest_data import run_ingestion

if __name__ == "__main__":
    print("Running semantic ingestion...")
    run_ingestion(tenant_id="semantic", init_db=False)
    print("Running simple ingestion...")
    run_ingestion(tenant_id="simple", init_db=False)
    print("Running paragraph ingestion...")
    run_ingestion(tenant_id="paragraph", init_db=False)
