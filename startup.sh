#!/bin/bash

echo "Running ETL pipeline..."


echo "Running get_datasets.py"
python get_datasets.py
echo "Running get_transform.py"
python get_transform.py
echo "Running get_fuels.py"
python get_fuels.py
echo "Running get_information.py"
python get_information.py
echo "Running get_predictions.py"
python get_predictions.py
echo "Running get_ranking.py"
python get_ranking.py
echo "All scripts executed successfully."

echo "Starting Streamlit..."

python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true