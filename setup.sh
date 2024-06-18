#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running setup...${NC}"

# M* Mac
if [[ $(uname -m) == "arm64" ]]; then
    echo -e "${RED}❗Detected M1 Mac❗${NC}"
    echo "Installing cairo with brew"
    brew install cairo libffi pkg-config
    echo "✅ Libaries installed"
fi
# Mac Intel
if [[ $(uname -m) != "arm64" ]]; then
    echo -e "${YELLOW}Running on Intel-based Mac${NC}"
fi
# Windows
if [ -n "$WINDIR" ]; then
    echo -e "${YELLOW}Running on Windows${NC}"
fi


# Installing dependencies
pip install -r dependencies.txt
echo "✅ Dependencies installed"

config_file="config.cfg"
quotes_file="quotes.json"
default_quote_json='{
  "metaData": {
    "time": "",
    "currentQuote": {
      "quote": "",
      "author": ""
    }
  },
  "quotes": []
}
'

# Check if config.cfg exists
if [ ! -f "$config_file" ]; then
    echo "⌛ Creating $config_file..."
    touch "$config_file"

    echo "[bot]" >> "$config_file"
    echo "token=your_bot_token" >> "$config_file"
    echo "guildId=your_guid_id" >> "$config_file"
    echo "✅ $config_file created"
    echo "Make sure to enter your bot token in $config_file"

else
    echo "✅ $config_file exists."
fi

# Check if quotes db exists
if [ ! -f "$quotes_file" ]; then
    echo "⌛ Creating $quotes_file..."
    echo "$default_quote_json" > "$quotes_file"
    echo "✅ $quotes_file created"

else
    echo "✅ $quotes_file exists."
fi
