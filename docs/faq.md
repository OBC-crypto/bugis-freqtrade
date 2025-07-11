# Freqtrade FAQ

## Supported Markets

Freqtrade supports spot trading, as well as (isolated) futures trading for some selected exchanges. Please refer to the [documentation start page](index.md#supported-futures-exchanges-experimental) for an up-to-date list of supported exchanges.

### Can my bot open short positions?

Freqtrade can open short positions in futures markets.
This requires the strategy to be made for this - and `"trading_mode": "futures"` in the configuration.
Please make sure to read the [relevant documentation page](leverage.md) first.

In spot markets, you can in some cases use leveraged spot tokens, which reflect an inverted pair (eg. BTCUP/USD, BTCDOWN/USD, ETHBULL/USD, ETHBEAR/USD,...) which can be traded with Freqtrade.

### Can my bot trade options or futures?

Futures trading is supported for selected exchanges. Please refer to the [documentation start page](index.md#supported-futures-exchanges-experimental) for an up-to-date list of supported exchanges.

## Beginner Tips & Tricks

* When you work with your strategy & hyperopt file you should use a proper code editor like VSCode or PyCharm. A good code editor will provide syntax highlighting as well as line numbers, making it easy to find syntax errors (most likely pointed out by Freqtrade during startup).

## Freqtrade common questions

### Can freqtrade open multiple positions on the same pair in parallel?

No. Freqtrade will only open one position per pair at a time.
You can however use the [`adjust_trade_position()` callback](strategy-callbacks.md#adjust-trade-position) to adjust an open position.

Backtesting provides an option for this in `--eps` - however this is only there to highlight "hidden" signals, and will not work in live.

### The bot does not start

Running the bot with `freqtrade trade --config config.json` shows the output `freqtrade: command not found`.

This could be caused by the following reasons:

* The virtual environment is not active.
  * Run `source .venv/bin/activate` to activate the virtual environment.
* The installation did not complete successfully.
  * Please check the [Installation documentation](installation.md).

### The bot starts, but in STOPPED mode

Make sure you set the `initial_state` config option to `"running"` in your config.json

### I have waited 5 minutes, why hasn't the bot made any trades yet?

* Depending on the entry strategy, the amount of whitelisted coins, the
situation of the market etc, it can take up to hours or days to find a good entry
position for a trade. Be patient!

* Backtesting will tell you roughly how many trades to expect - but that won't guarantee that they'll be distributed evenly across time - so you could have 20 trades on one day, and 0 for the rest of the week.

* It may be because of a configuration error. It's best to check the logs, they usually tell you if the bot is simply not getting buy signals (only heartbeat messages), or if there is something wrong (errors / exceptions in the log).

### I have made 12 trades already, why is my total profit negative?

I understand your disappointment but unfortunately 12 trades is just
not enough to say anything. If you run backtesting, you can see that the
current algorithm does leave you on the plus side, but that is after
thousands of trades and even there, you will be left with losses on
specific coins that you have traded tens if not hundreds of times. We
of course constantly aim to improve the bot but it will _always_ be a
gamble, which should leave you with modest wins on monthly basis but
you can't say much from few trades.

### I’d like to make changes to the config. Can I do that without having to kill the bot?

Yes. You can edit your config and use the `/reload_config` command to reload the configuration. The bot will stop, reload the configuration and strategy and will restart with the new configuration and strategy.

### Why does my bot not sell everything it bought?

This is called "coin dust" and can happen on all exchanges.
It happens because many exchanges subtract fees from the "receiving currency" - so you buy 100 COIN - but you only get 99.9 COIN.
As COIN is trading in full lot sizes (1COIN steps), you cannot sell 0.9 COIN (or 99.9 COIN) - but you need to round down to 99 COIN.

This is not a bot-problem, but will also happen while manual trading.

While freqtrade can handle this (it'll sell 99 COIN), fees are often below the minimum tradable lot-size (you can only trade full COIN, not 0.9 COIN).
Leaving the dust (0.9 COIN) on the exchange makes usually sense, as the next time freqtrade buys COIN, it'll eat into the remaining small balance, this time selling everything it bought, and therefore slowly declining the dust balance (although it most likely will never reach exactly 0).

Where possible (e.g. on binance), the use of the exchange's dedicated fee currency will fix this.
On binance, it's sufficient to have BNB in your account, and have "Pay fees in BNB" enabled in your profile. Your BNB balance will slowly decline (as it's used to pay fees) - but you'll no longer encounter dust (Freqtrade will include the fees in the profit calculations).
Other exchanges don't offer such possibilities, where it's simply something you'll have to accept or move to a different exchange.

### I deposited more funds to the exchange, but my bot doesn't recognize this

Freqtrade will update the exchange balance when necessary (Before placing an order).
RPC calls (Telegram's `/balance`, API calls to `/balance`) can trigger an update at max. once per hour.

If `adjust_trade_position` is enabled (and the bot has open trades eligible for position adjustments) - then the wallets will be refreshed once per hour.
To force an immediate update, you can use `/reload_config` - which will restart the bot.

### I want to use incomplete candles

Freqtrade will not provide incomplete candles to strategies. Using incomplete candles will lead to repainting and consequently to strategies with "ghost" buys, which are impossible to both backtest, and verify after they happened.

You can use "current" market data by using the [dataprovider](strategy-customization.md#orderbookpair-maximum)'s orderbook or ticker methods - which however cannot be used during backtesting.

### Is there a setting to only Exit the trades being held and not perform any new Entries?

You can use the `/stopentry` command in Telegram to prevent future trade entry, followed by `/forceexit all` (sell all open trades).

### I sold the bot's capital and now there's errors in the log

Freqtrade assumes that the trades it opens are managed only though the bot.  
If you happen to (accidentally) sell the bot's capital, freqtrade will try to recover by trying to re-find on-exchange orders.

This is a best-effort approach, and will not work in all cases, especially when using order types that are not supported by freqtrade (OCO, iceberg, etc.), or when working with older trades (where the exchange no longer provides full order information).
The exact limits will vary between exchanges - with the details usually being documented in the exchange's API documentation.

### I want to run multiple bots on the same machine

Please look at the [advanced setup documentation Page](advanced-setup.md#running-multiple-instances-of-freqtrade).

### I'm getting "Impossible to load Strategy" when starting the bot

This error message is shown when the bot cannot load the strategy.
Usually, you can use `freqtrade list-strategies` to list all available strategies. 
The output of this command will also include a status column, showing if the strategy can be loaded.

Please check the following:

* Are you using the correct strategy name? The strategy name is case-sensitive and must correspond to the Strategy class name (not the filename!).
* Is the strategy in the `user_data/strategies` directory, and has the file-ending `.py`?
* Does the bot show other warnings before this error? Maybe you're missing some dependencies for the strategy - which would be highlighted in the log.
* In case of docker - is the strategy directory mounted correctly (check the volumes part of the docker-compose file)?

### I'm getting "Missing data fillup" messages in the log

This message is just a warning that the latest candles had missing candles in them.
Depending on the exchange, this can indicate that the pair didn't have a trade for the timeframe you are using - and the exchange does only return candles with volume.
On low volume pairs, this is a rather common occurrence.

If this happens for all pairs in the pairlist, this might indicate a recent exchange downtime. Please check your exchange's public channels for details.

Irrespectively of the reason, Freqtrade will fill up these candles with "empty" candles, where open, high, low and close are set to the previous candle close - and volume is empty. In a chart, this will look like a `_` - and is aligned with how exchanges usually represent 0 volume candles.

### I'm getting "Price jump between 2 candles detected"

This message is a warning that the candles had a price jump of > 30%.
This might be a sign that the pair stopped trading, and some token exchange took place (e.g. COCOS in 2021 - where price jumped from 0.0000154 to 0.01621).
This message is often accompanied by ["Missing data fillup"](#im-getting-missing-data-fillup-messages-in-the-log) - as trading on such pairs is often stopped for some time.

### I want to reset the bot's database

To reset the bot's database, you can either delete the database (by default `tradesv3.sqlite` or `tradesv3.dryrun.sqlite`), or use a different database url via `--db-url` (e.g. `sqlite:///mynewdatabase.sqlite`).

### I'm getting "Outdated history for pair xxx" in the log

The bot is trying to tell you that it got an outdated last candle (not the last complete candle).
As a consequence, Freqtrade will not enter a trade for this pair - as trading on old information is usually not what is desired.

This warning can point to one of the below problems:

* Exchange downtime -> Check your exchange status page / blog / twitter feed for details.
* Wrong system time -> Ensure your system-time is correct.
* Barely traded pair -> Check the pair on the exchange webpage, look at the timeframe your strategy uses. If the pair does not have any volume in some candles (usually visualized with a "volume 0" bar, and a "_" as candle), this pair did not have any trades in this timeframe. These pairs should ideally be avoided, as they can cause problems with order-filling.
* API problem -> API returns wrong data (this only here for completeness, and should not happen with supported exchanges).

### I'm getting the "Exchange XXX does not support market orders." message and cannot run my strategy

As the message says, your exchange does not support market orders and you have one of the [order types](configuration.md/#understand-order_types) set to "market". Your strategy was probably written with other exchanges in mind and sets "market" orders for "stoploss" orders, which is correct and preferable for most of the exchanges supporting market orders (but not for Gate.io).

To fix this, redefine order types in the strategy to use "limit" instead of "market":

``` python
    order_types = {
        ...
        "stoploss": "limit",
        ...
    }
```

The same fix should be applied in the configuration file, if order types are defined in your custom config rather than in the strategy.

### I'm trying to start the bot live, but get an API permission error

Errors like `Invalid API-key, IP, or permissions for action` mean exactly what they actually say.  
Your API key is either invalid (copy/paste error? check for leading/trailing spaces in the config), expired, or the IP you're running the bot from is not enabled in the Exchange's API console.  
Usually, the permission "Spot Trading" (or the equivalent in the exchange you use) will be necessary.  
Futures will usually have to be enabled specifically.

### How do I search the bot logs for something?

By default, the bot writes its log into stderr stream. This is implemented this way so that you can easily separate the bot's diagnostics messages from Backtesting, Edge and Hyperopt results, output from other various Freqtrade utility sub-commands, as well as from the output of your custom `print()`'s you may have inserted into your strategy. So if you need to search the log messages with the grep utility, you need to redirect stderr to stdout and disregard stdout.

* In unix shells, this normally can be done as simple as:
```shell
$ freqtrade --some-options 2>&1 >/dev/null | grep 'something'
```
(note, `2>&1` and `>/dev/null` should be written in this order)

* Bash interpreter also supports so called process substitution syntax, you can grep the log for a string with it as:
```shell
$ freqtrade --some-options 2> >(grep 'something') >/dev/null
```
or
```shell
$ freqtrade --some-options 2> >(grep -v 'something' 1>&2)
```

* You can also write the copy of Freqtrade log messages to a file with the `--logfile` option:
```shell
$ freqtrade --logfile /path/to/mylogfile.log --some-options
```
and then grep it as:
```shell
$ cat /path/to/mylogfile.log | grep 'something'
```
or even on the fly, as the bot works and the log file grows:
```shell
$ tail -f /path/to/mylogfile.log | grep 'something'
```
from a separate terminal window.

On Windows, the `--logfile` option is also supported by Freqtrade and you can use the `findstr` command to search the log for the string of interest:
```
> type \path\to\mylogfile.log | findstr "something"
```

## Hyperopt module

### Why does freqtrade not have GPU support?

First of all, most indicator libraries don't have GPU support - as such, there would be little benefit for indicator calculations.
The GPU improvements would only apply to pandas-native calculations - or ones written by yourself.

GPU's are only good at crunching numbers (floating point operations).
For hyperopt, we need both number-crunching (find next parameters) and running python code (running backtesting).
As such, GPU's are not too well suited for most parts of hyperopt.

The benefit of using GPU would therefore be pretty slim - and will not justify the complexity introduced by trying to add GPU support.

There is however nothing preventing you from using GPU-enabled indicators within your strategy if you think you must have this - you will however probably be disappointed by the slim gain that will give you (compared to the complexity).

### How many epochs do I need to get a good Hyperopt result?

Per default Hyperopt called without the `-e`/`--epochs` command line option will only
run 100 epochs, means 100 evaluations of your triggers, guards, ... Too few
to find a great result (unless if you are very lucky), so you probably
have to run it for 10000 or more. But it will take an eternity to
compute.

Since hyperopt uses Bayesian search, running for too many epochs may not produce greater results.

It's therefore recommended to run between 500-1000 epochs over and over until you hit at least 10000 epochs in total (or are satisfied with the result). You can best judge by looking at the results - if the bot keeps discovering better strategies, it's best to keep on going.

```bash
freqtrade hyperopt --hyperopt-loss SharpeHyperOptLossDaily --strategy SampleStrategy -e 1000
```

### Why does it take a long time to run hyperopt?

* Discovering a great strategy with Hyperopt takes time. Study www.freqtrade.io, the Freqtrade Documentation page, join the Freqtrade [discord community](https://discord.gg/p7nuUNVfP7). While you patiently wait for the most advanced, free crypto bot in the world, to hand you a possible golden strategy specially designed just for you.

* If you wonder why it can take from 20 minutes to days to do 1000 epochs here are some answers:

This answer was written during the release 0.15.1, when we had:

* 8 triggers
* 9 guards: let's say we evaluate even 10 values from each
* 1 stoploss calculation: let's say we want 10 values from that too to be evaluated

The following calculation is still very rough and not very precise
but it will give the idea. With only these triggers and guards there is
already 8\*10^9\*10 evaluations. A roughly total of 80 billion evaluations.
Did you run 100 000 evaluations? Congrats, you've done roughly 1 / 100 000 th
of the search space, assuming that the bot never tests the same parameters more than once.

* The time it takes to run 1000 hyperopt epochs depends on things like: The available cpu, hard-disk, ram, timeframe, timerange, indicator settings, indicator count, amount of coins that hyperopt test strategies on and the resulting trade count - which can be 650 trades in a year or 100000 trades depending if the strategy aims for big profits by trading rarely or for many low profit trades.

Example: 4% profit 650 times vs 0,3% profit a trade 10000 times in a year. If we assume you set the --timerange to 365 days.

Example:
`freqtrade --config config.json --strategy SampleStrategy --hyperopt SampleHyperopt -e 1000 --timerange 20190601-20200601`

## Official channels

Freqtrade is using exclusively the following official channels:

* [Freqtrade discord server](https://discord.gg/p7nuUNVfP7)
* [Freqtrade documentation (https://freqtrade.io)](https://freqtrade.io)
* [Freqtrade github organization](https://github.com/freqtrade)

Nobody affiliated with the freqtrade project will ask you about your exchange keys or anything else exposing your funds to exploitation.
Should you be asked to expose your exchange keys or send funds to some random wallet, then please don't follow these instructions.

Failing to follow these guidelines will not be responsibility of freqtrade.

## "Freqtrade token"

Freqtrade does not have a Crypto token offering.

Token offerings you find on the internet referring Freqtrade, FreqAI or freqUI must be considered to be a scam, trying to exploit freqtrade's popularity for their own, nefarious gains.
