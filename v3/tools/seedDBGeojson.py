import pymongo

CONN_STR = "mongodb+srv://aiden:bE9wTAjULtcBFz58@cluster0.o222wih.mongodb.net/?retryWrites=true&w=majority"


def createConnection():
    client = pymongo.MongoClient(
        CONN_STR, tls=True, tlsAllowInvalidCertificates=True)
    return client.notification


def main():
    notification = createConnection()
    arizona = notification.arizona
    # read geojson data
    # find smallest hexagon that surrounds polygon    


if __name__ == '__main__':
    main()
