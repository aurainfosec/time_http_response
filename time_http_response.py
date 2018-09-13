#!/usr/bin/env python3

import requests
import argparse
import numpy as np
import sys
import pickle
from time import sleep

parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Measure average response delay for HTTP request.')
parser.add_argument('-u', '--url', dest='target',
        default=argparse.SUPPRESS, metavar='URL',
        help='''Page to send request to, e.g. http://example.com.
        Overwrites url read from session, if restoring.
        Must be given unless restoring a session.''')
parser.add_argument('-m', '--method', dest='method', choices=['get', 'fpost', 'post'],
        default=argparse.SUPPRESS, metavar='get|fpost|post',
        help='''Method to use:
        "get" (params are appended to target),
        "fpost" (POST with URL encoded parameters in the body), or
        "post" (POST with json data in the body)
        Overwrites method read from session, if restoring.
        Must be given unless restoring a session.''')
parser.add_argument('-p', '--params', dest='params', nargs='*',
        default=argparse.SUPPRESS, metavar='key=val',
        help='''List of key=value parameters (spaces within key/value
        names must be escaped. They replace those read from session,
        if restoring (use --params with no arguments to suppress those
        read from session).''')
parser.add_argument('-a', '--append', dest='append',
        action='store_true', default=False,
        help='Append given parameters to those read from session.')
parser.add_argument('-r', '--restore', dest='restore', metavar='FILE',
        help='''Restore session (response time data points, method,
        parameters) from file''')
parser.add_argument('-s', '--store', dest='store', metavar='FILE',
        help='''Save session (response time data points, method,
        parameters) to a file''')
parser.add_argument('-o', '--out', dest='out', metavar='FILE',
        help='Save delays to a file (one delay per line)')
parser.add_argument('-n', '--nreqs', dest='nreqs', type=int, default=100, metavar='N',
        help='How many times to send the request.')
parser.add_argument('-w', '--wait', dest='wait', type=float, metavar='SECONDS',
        help='Seconds to wait between requests (can be fractional)')
parser.add_argument('--proxy', dest='http_proxy', metavar='PROXY',
        help='''Use an http proxy, e.g. http://localhost:8080. Fot
        HTTP Basic Auth use http://user:password@host.''')
parser.add_argument('--sproxy', dest='https_proxy', metavar='PROXY',
        help='''Use an https proxy, e.g. https://localhost:8080. Fot
        HTTP Basic Auth use http://user:password@host.''')
parser.add_argument('--cert', dest='verify', metavar='FILE',
        help='Server SSL certificate (PEM) to use for verification.')
parser.add_argument('--no-verify', dest='verify',
        action='store_false', default=True,
        help='Don\'t verify server SSL certificate')
args = parser.parse_args()

data = {'target': '', 'method': '', 'delays': [], 'payload': {}}

########## Restore session if given
if args.restore is not None:
    with open(args.restore, 'rb') as f:
        data.update(pickle.load(f))
        print('Read session with {} data points'.format(data['delays'].size))

########## Update data from args
try:
    data['target'] = args.target
except AttributeError:
    pass
try:
    data['method'] = args.method
except AttributeError:
    pass

try:
    args.params
except AttributeError:
    pass
else:
    if not args.append:
        data['payload'].clear()
    for p in args.params:
        try:
            k,v = p.split('=')
        except ValueError:
            print('Invalid parameter format, use key=value', file=sys.stderr)
            sys.exit(-1)
        data['payload'][k] = v

if not data['target']:
    print('You must specify a url, see --help.', file=sys.stderr)
    sys.exit(-1)
if not data['method']:
    print('You must specify a method, see --help.', file=sys.stderr)
    sys.exit(-1)

########## Set request options
proxies = {}
if args.http_proxy is not None:
    proxies['http'] = args.http_proxy
if args.https_proxy is not None:
    proxies['https'] = args.https_proxy

req_args = {
        'verify': args.verify,
        'proxies': proxies,
        }
sender = requests.post
if data['method'] == 'get':
    req_args['params'] = data['payload']
    sender = requests.get
elif data['method'] == 'fpost':
    req_args['data'] = data['payload']
else:
    req_args['json'] = data['payload']

########## Send the requests
# debug
print(req_args)
print(dict((k,v) for k,v in data.items() if k != 'delays'))
delays = np.full(args.nreqs, 0)
for r in range(args.nreqs):
    req = sender(data['target'], **req_args)
    delays[r] = req.elapsed.microseconds
    if args.wait is not None:
        sleep(args.wait)

########## Finalize
data['delays'] = np.append(data['delays'], delays)

if data['delays'].size > 0:
    print('Average delay in ms: {:.0f} +/- {:.0f}'.format(
        np.round(np.mean(data['delays'])/1000),
        np.round(np.std(data['delays'])/1000)))

if args.out is not None:
    with open(args.out, 'w') as f:
        for d in data['delays']:
            f.write('{:.0f}\n'.format(d))
        print('Wrote {} data points to {}'.format(data['delays'].size, args.out))

if args.store is not None:
    with open(args.store, 'wb') as f:
        pickle.dump(data, f)
        print('Saved session with {} data points to {}'.format(data['delays'].size, args.store))
