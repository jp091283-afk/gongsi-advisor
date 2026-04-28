from flask import Flask, send_file, request, Response
import requests
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/dart')
def dart_proxy():
    query = request.query_string.decode('utf-8')
    dart_url = 'https://opendart.fss.or.kr/api/list.json'
    if query:
        dart_url += '?' + query
    try:
        r = requests.get(
            dart_url,
            headers={'User-Agent': 'Mozilla/5.0 Chrome/120', 'Accept': 'application/json'},
            timeout=15,
            verify=False
        )
        return Response(
            r.content,
            content_type='application/json; charset=utf-8',
            headers={'Access-Control-Allow-Origin': '*'}
        )
    except Exception as e:
        return Response(
            '{"status":"ERR","message":"' + str(e) + '"}',
            content_type='application/json',
            headers={'Access-Control-Allow-Origin': '*'}
        )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
