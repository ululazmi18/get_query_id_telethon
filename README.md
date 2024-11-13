## Requirements

- Python 3.7+
- A valid `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org/)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ululazmi18/get_query_id_telethon.git
   cd get_query_id_telethon
   ```

2. **Install Required Libraries**
   ```bash
   pip install telethon
   ```

3. **Configure API Credentials**
   - In the root folder of the project, you will find a `config.json` file created by the script. Open this file and fill in your `api_id` and `api_hash`.
   - Example:
     ```json
     {
       "api_id": 1234567,
       "api_hash": "your_api_hash_here"
     }
     ```

4. **Run the Script**
   - Start the program by running:
     ```bash
     python main.py
     ```
