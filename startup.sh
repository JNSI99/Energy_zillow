#!/bin/bash

echo "Running ETL pipeline..."

python get_datasets.py
python get_transform.py
python get_fuels.py
python get_information.py
python get_predictions.py
python get_ranking.py


echo "Starting Streamlit..."

python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true