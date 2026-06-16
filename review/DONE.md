# Fixes done

## Summary view

### Sanity checks

#### Invalid from
```bash
╰─ curl -I "http://localhost:8010/api/summary/?from=test&to=2024-06-30"
HTTP/1.1 400 Bad Request
Date: Tue, 16 Jun 2026 10:06:32 GMT
Server: WSGIServer/0.2 CPython/3.11.15
Content-Type: application/json
```

#### Invalid to
```bash
╰─ curl -I "http://localhost:8010/api/summary/?from=2024-01-01&to=test"
HTTP/1.1 400 Bad Request
Date: Tue, 16 Jun 2026 10:06:57 GMT
Server: WSGIServer/0.2 CPython/3.11.15
Content-Type: application/json
```

#### Invalid from and to

```bash
╰─ curl -I "http://localhost:8010/api/summary/?from=test&to=test"
HTTP/1.1 400 Bad Request
Date: Tue, 16 Jun 2026 10:08:54 GMT
Server: WSGIServer/0.2 CPython/3.11.15
Content-Type: application/json
```

#### Valid fields 

##### from only

```bash
╰─ curl -I "http://localhost:8010/api/summary/?from=2024-01-01"
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:09:18 GMT
Server: WSGIServer/0.2 CPython/3.11.15
Content-Type: application/json
```

##### to only

```bash
╰─ curl -I "http://localhost:8010/api/summary/?to=2024-06-30"
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:09:18 GMT
Server: WSGIServer/0.2 CPython/3.11.15
Content-Type: application/json
```

##### Both
```bash
╰─ curl -I "http://localhost:8010/api/summary/?from=2024-01-01&to=2024-06-30"
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:06:42 GMT
Server: WSGIServer/0.2 CPython/3.11.15
Content-Type: application/json
```