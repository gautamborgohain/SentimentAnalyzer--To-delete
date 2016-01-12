import json


def getConfigs():
    config = json.load(open('/Users/gautamborgohain/PycharmProjects/SentimentAnalyzer/src/config.json'))
    return config
