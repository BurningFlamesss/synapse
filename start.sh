#!/bin/bash
if [ -z "$API_KEY" ]; then
  read -p "Enter your OpenRouter API key: " API_KEY
  export API_KEY
fi
export BASE_URL="https://openrouter.ai/api/v1"
python main.py