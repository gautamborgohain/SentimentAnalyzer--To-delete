import json


def getConfigs(c):
    config = json.load(open('/Users/gautamborgohain/PycharmProjects/SentimentAnalyzer/src/config.json'))
    return config
