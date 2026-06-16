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

### Performance issue

#### Before

##### Time

```bash
╰─ ./review/summary_time.sh.sh
Request 1 took 0.009256 seconds
Request 2 took 0.000989 seconds
Request 3 took 0.001054 seconds
Request 4 took 0.000936 seconds
Request 5 took 0.000912 seconds
Request 6 took 0.001169 seconds
Request 7 took 0.001028 seconds
Request 8 took 0.001065 seconds
Request 9 took 0.000883 seconds
Request 10 took 0.000998 seconds
Average: .0018 seconds
```

##### Results

```json
{
   "results" : [
      {
         "category" : "health",
         "total" : "859110.21"
      },
      {
         "category" : "food",
         "total" : "834050.15"
      },
      {
         "category" : "entertainment",
         "total" : "830276.06"
      },
      {
         "category" : "travel",
         "total" : "821134.86"
      },
      {
         "category" : "utilities",
         "total" : "802218.96"
      },
      {
         "category" : "transport",
         "total" : "776398.69"
      }
   ]
}
```

#### After 

##### Time

```bash
╰─ ./review/summary_time.sh
Request 1 took 0.001248 seconds
Request 2 took 0.000973 seconds
Request 3 took 0.001038 seconds
Request 4 took 0.000882 seconds
Request 5 took 0.000937 seconds
Request 6 took 0.000841 seconds
Request 7 took 0.001022 seconds
Request 8 took 0.000902 seconds
Request 9 took 0.001377 seconds
Request 10 took 0.001187 seconds
Average: .0010 seconds
```

##### Results

```json
{
   "results" : [
      {
         "category" : "health",
         "total" : "859110.21"
      },
      {
         "category" : "food",
         "total" : "834050.15"
      },
      {
         "category" : "entertainment",
         "total" : "830276.06"
      },
      {
         "category" : "travel",
         "total" : "821134.86"
      },
      {
         "category" : "utilities",
         "total" : "802218.96"
      },
      {
         "category" : "transport",
         "total" : "776398.69"
      }
   ]
}
```

#### Conclusion

Targetting my local environment with only a CSV import in the database, it does not make so much difference, but on a full database the SQL aggregation will outperform the retrieval of all rows and then aggregating in Python.
