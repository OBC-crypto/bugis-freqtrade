from freqtrade.strategy import IStrategy

class DefaultStrategy(IStrategy):
    minimal_roi = {
        "0": 0.01
    }

    stoploss = -0.10

    timeframe = '1h'

    def populate_indicators(self, dataframe, metadata):
        return dataframe

    def populate_buy_trend(self, dataframe, metadata):
        dataframe['buy'] = 0
        return dataframe

    def populate_sell_trend(self, dataframe, metadata):
        dataframe['sell'] = 0
        return dataframe
