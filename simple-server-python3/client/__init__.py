#!python3

"""
Very simple HTTP server in python

"""

from http.server import BaseHTTPRequestHandler
import json

# Server Configuration
HOST_NAME = '0.0.0.0'
HOST_NAME_TEST = HOST_NAME
PORT_NUMBER = 8080
PORT_NUMBER_TEST = PORT_NUMBER + 10

taxRateDict = {
    "DE" : 0.15,
    "UK" : .15,
    "FR" : .15,
    "IT" : .15,
    "ES" : .15,
    "PL" : .21,
    "RO" : .2,
    "NL" : .2,
    "BE" : .24,
    "EL" : .2,
    "CZ" : .19,
    "PT" : .23,
    "HU" : .27,
    "SE" : .23,
    "AT" : .22,
    "BG" : .21,
    "DK" : .21,
    "FI" : .17,
    "SK" : .10,
    "IE" : .21,
    "HR" : .23,
    "LT" : .23,
    "SI" : .24,
    "LV" : .2,
    "EE" : .22,
    "CY" : .21,
    "LU" : .25,
    "MT" : .2
}

taxReductions = {
    "STANDARD" : [(50000, .15),(10000, .1),(7000, .07),(5000, .05),(1000, .03)],
    "HALF PRICE" : [(0,.5)]
}


lastRequest = None


class ServerHandler(BaseHTTPRequestHandler):

    def __write_response(self, body_html_, code):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(body_html_.encode("utf_8"))

    def __get_object(self):
        length = int(self.headers['content-length'])
        content = self.rfile.read(length).decode("utf-8")
        return json.loads(content)

    def __feedback(self):
        object = self.__get_object()

        print("LOG in Feedback >> " , object)
        self.__write_response(json.dumps(object), 204)
        return object

    def __your_path(self):
        object = self.__get_object()

        # log
        print("LOG in PATH >> " , object)
        # Only for test
        #total = calculate(object)
        self.__write_response((json.dumps({'total': 1000})), 200)

    def do_GET(self):
        self.__write_response('hello world', 200)

    def do_POST(self):
        info = self.__get_object()
        print(info)
        if isinstance(info, (list, tuple)):
            self.__write_response('Unknown', 400)
        if 'prices' in info:
            if 'prices' not in info or 'quantities' not in info or 'country' not in info or 'reduction' not in info:
                self.__write_response('Unknown', 400)
            lastRequest = info
            print (info)
            prices = info['prices']
            quant = info['quantities']
            country = info['country']
            reduction = info['reduction']
            cost = 0
            if len(prices) != len(quant):
                self.__write_response('Unknown', 400)
            for x in range(0, len(prices)):
                cost += prices[x] * quant[x]
            tax = (taxRateDict[country]) * cost
            total = tax + cost
            print(cost)
            if country is 'FR' and cost < 500:
                total = cost
            else:
                total = tax + cost
            if reduction in taxReductions:
                reductionList = taxReductions[reduction]
                for val in reductionList:
                    if total > val[0]:
                        total -= total * val[1]
                        break
            print (total)
            self.__write_response((json.dumps({'total': total})), 200)
            # {

            #     '/ping': lambda: self.__write_response((json.dumps({'total': total})), 200),
            #     '/feedback': self.__feedback,
            #     '/order': self.__your_path

            # }.get(self.path, lambda: self.__write_response('Unknown', 404))()
        elif info['type'] is "ERROR" or info['type'] is "INFO":
            message = info['content']
            prices = lastRequest['prices']
            quant = lastRequest['quantities']
            cost = 0
            for x in range(0, len(prices)):
                cost += prices[x] * quant[x]
            words = message.split(" ")
            i = 0
            wrongVal = 0
            rightVal = 0
            for word in words:
                if word is "reply":
                    wrongVal = double(words[i + 1])
                if word is "was":
                    stringVal = words[i+1]
                    rightVal = double(stringVal[0:-1])
                i++
            wrongVal -= cost
            rightVal -= cost
            taxRateDict[lastRequest['country']] = taxRateDict[lastRequest['country']] * (rightVal / wrongVal)
        else:
            self.__write_response('Unknown', 400)

def start_server(testMode=False):
    global server
    from http.server import HTTPServer

    if testMode:
        host_name = HOST_NAME_TEST
        port_number = PORT_NUMBER_TEST
    else:
        host_name = HOST_NAME
        port_number = PORT_NUMBER

    server = HTTPServer((host_name, port_number), ServerHandler)
    print('Starting server %s:%s use <Ctrl-C> to stop' % (host_name, port_number))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
    print('Server interrupted')


def shutdown_server():
    global server
    server.server_close()
    print('Shutdown server %s:%s ' % (HOST_NAME, PORT_NUMBER))

if __name__ == '__main__':
    start_server()
