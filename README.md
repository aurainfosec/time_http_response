# About
Measure the average delay between sending an HTTP request and receiving the response. Use for time-based attacks or just to check the server load.

Requires **python3** and **numpy**.

# Features
- GET with URL parameters and no body
- POST with `application/x-www-form-urlencoded` body and no URL parameters
- POST with `application/json` body and no URL parameters
- http and https proxy with a custom SSL certificate
- session saving/restoring (url, parameters, method and measured delays)
- delay between each request

# What it does not do:
- does not handle custom HTTP headers
- does not handle arbitrary `Content-type`

# Usage
```
usage: time_http_response.py [-h] [-u URL] [-m get|fpost|post]
                             [-p [key=val [key=val ...]]] [-a] [-r FILE]
                             [-s FILE] [-o FILE] [-n N] [-w SECONDS]
                             [--proxy PROXY] [--sproxy PROXY] [--cert FILE]
                             [--no-verify]

Measure average response delay for HTTP request.

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Page to send request to, e.g. http://example.com.
                        Overwrites url read from session, if restoring. Must
                        be given unless restoring a session.
  -m get|fpost|post, --method get|fpost|post
                        Method to use: "get" (params are appended to target),
                        "fpost" (POST with URL encoded parameters in the
                        body), or "post" (POST with json data in the body)
                        Overwrites method read from session, if restoring.
                        Must be given unless restoring a session.
  -p [key=val [key=val ...]], --params [key=val [key=val ...]]
                        List of key=value parameters (spaces within key/value
                        names must be escaped. They replace those read from
                        session, if restoring (use --params with no arguments
                        to suppress those read from session).
  -a, --append          Append given parameters to those read from session.
                        (default: False)
  -r FILE, --restore FILE
                        Restore session (response time data points, method,
                        parameters) from file (default: None)
  -s FILE, --store FILE
                        Save session (response time data points, method,
                        parameters) to a file (default: None)
  -o FILE, --out FILE   Save delays to a file (one delay per line) (default:
                        None)
  -n N, --nreqs N       How many times to send the request. (default: 100)
  -w SECONDS, --wait SECONDS
                        Seconds to wait between requests (can be fractional)
                        (default: None)
  --proxy PROXY         Use an http proxy, e.g. http://localhost:8080. Fot
                        HTTP Basic Auth use http://user:password@host.
                        (default: None)
  --sproxy PROXY        Use an https proxy, e.g. https://localhost:8080. Fot
                        HTTP Basic Auth use http://user:password@host.
                        (default: None)
  --cert FILE           Server SSL certificate (PEM) to use for verification.
                        (default: None)
  --no-verify           Don't verify server SSL certificate (default: True)

```

# Examples:
- POST a forms to example.com

```
python3 time_http_response.py -m fpost -u http://example.com -n 1 -p input=value -s session.pickle
```
- Restore session and send 39 more forms:

```
python3 time_http_response.py -n 39 -s session.pickle -r session.pickle
```
- Just re-analyze old session, exporting data as text:

```
python3 time_http_response.py -n 0 -r session.pickle -o data.txt
```
