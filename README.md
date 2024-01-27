1. Build the project

```bash
docker-compose build
```

2. Start the project

```bash
docker-compose up -d
```

3. Watch logs

```bash
docker-compose logs -f app
```

This command will start the FastAPI server on port 8000, the MongoDB service on port 27017 and Mongo admin panel on port 8081.
You can navigate to `http://localhost:8000/docs` in your browser to access the automatically generated API documentation.

## ⚙️ Local Development

```
poetry install
poetry shell
sh ./scripts/launch.sh
```
