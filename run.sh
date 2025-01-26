#!/bin/bash
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "Installation successful!"
else
    echo "Installation failed!"
    exit 1
fi
echo "Running main.py..."
python main.py
