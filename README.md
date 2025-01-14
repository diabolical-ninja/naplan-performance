# naplan-performance
Similar to vce-performance, but for NAPLAN. Still very much a WIP & data is currently quite limited. 



## Running the Web App

Build the environment:

```bash
poetry install
```

Start up the app:

```sh
poetry run python app.py
```

In a browser, navigate to `http://127.0.0.1:8050/`


Or in a prod environment:
```sh
poetry run gunicorn app:server
```