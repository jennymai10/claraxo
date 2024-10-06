### Docker Deployment Step

#### 1. Build docker images

For both backend and frontend

```
docker-compose build
```

Or, for each, frontend

```
docker-compose build frontend
```

Backend,

```
docker-compose build backend
```

#### 2. Run

```
docker-compose up -d
```

#### 3. Check logs

Check both frontend and backend

```
docker-compose logs -f
```

Check individual, frontend

```
docker-compose logs -f frontend
```

For backend,

```
docker-compose logs -f backend
```
