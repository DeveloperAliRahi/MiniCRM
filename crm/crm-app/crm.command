#!/bin/bash
export TK_SILENCE_DEPRECATION=1

# Auto-install tkcalendar if missing
pip3 show tkcalendar &> /dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing tkcalendar..."
    pip3 install tkcalendar
fi

# Navigate into CRM app folder
cd /Users/alirahi/Desktop/Files/python/crm/crm-app

# Run the CRM using your Python environment
python3 crm.py
