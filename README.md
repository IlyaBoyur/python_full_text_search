# Full text search App

## Technologies
#### Python3.12, Flask, SQLite, Elasticsearch

### Service includes:
- SQLite database with legacy data
- ETL-script (Extract, transform, load), which migrates data SQLite -> Elasticsearch.
- Flask API endpoints


## Quick start
### 1. Start up Elasticsearch + Kibana
```bash
docker compose up -d --remove-orphans
```

### 3. Create & activate virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run ETL (SQLite -> Elasticsearch)
```bash
python3 etl_script.py
```

### 5. Start up API server
```bash
python3 server.py
```

### 6. Checkout APIs 
```
http://localhost:8000/
```

### Additional
#### Go inspect created indexes in ES
```bash
docker compose exec -it elasticsearch elasticsearch-sql-cli
```
#### Check out Kibana Dev Tools
Enter in web browser query string:  
```
http://localhost:5601/app/dev_tools#/console
```


### API Documentation

- List video files in DB:
```
GET /api/v1/movies?limit=50&page=int&search=str&sort=str&sort_order=str

// search — full text search (title, description, directors, etc).
// limit — number of files in response.
// page — page number.
// sort — sorting field.
// sort_order — sorting direction (asc, desc).
```

- Get video file detail:
```
GET /api/v1/movies/<movie_id>
```

- Get client info:
```
GET /client/info
```
