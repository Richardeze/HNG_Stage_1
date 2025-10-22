# HNG 13 Backend Wizards - Stage 1 Task
## String Analyzer API
This is a simple **Flask REST API** that analyzes strings and stores their computed properties (like palindrome check,
length, word count, etc.) in an **SQLite** database.

---
## Features
- Analyze and store string properties 
- Prevent duplicate entries using SHA-256 hash  
- Retrieve, filter, or delete analyzed strings 
- Natural language filtering support
---
## Tech Stack
- **Python 3**
- **Flask**
- **SQLite3**
- **Hashlib**
- **Datetime**
---
## ⚙️ Setup Instructions
```bash
# 1. Clone the repository
git clone https://github.com/Richardeze/HNG_Stage_1.git
cd HNG_Stage_1

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```
## 🔗 API ENDPOINT
| Method     | Endpoint                              | Description                                   |
| :--------- | :------------------------------------ | :-------------------------------------------- |
| **POST**   | `/strings`                            | Analyze and store a string                    |
| **GET**    | `/strings`                            | Get all analyzed strings                      |
| **GET**    | `/strings/<value>`                    | Get a specific analyzed string                |
| **POST**   | `/strings/filter-by-natural-language` | Filter strings using a natural language query |
| **DELETE** | `/strings/<value>`                    | Delete a specific string                      |

## Example Response
**POST /strings**  
{
  "value": "level"
}  
**Response**  
{
  "id": "e5a4b53f7a39f...",  
  "value": "level",  
  "properties": {
    "length": 5,  
    "is_palindrome": true,  
    "unique_characters": 4,  
    "word_count": 1
  },  
  "created_at": "2025-10-20T13:30:00+00:00"
}

## Live API URL


