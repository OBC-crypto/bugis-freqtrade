"""
A Rest Client for Freqtrade bot

Should not import anything from freqtrade,
so it can be used as a standalone script, and can be installed independently.
"""

import json
import logging
from typing import Any
from urllib.parse import urlencode, urlparse, urlunparse

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestConnectionError


logger = logging.getLogger("ft_rest_client")

ParamsT = dict[str, Any] | None
PostDataT = dict[str, Any] | list[dict[str, Any]] | None


class FtRestClient:
    def __init__(
        self,
        serverurl,
        username=None,
        password=None,
        *,
        pool_connections=10,
        pool_maxsize=10,
        timeout=10,
    ):
        self._serverurl = serverurl
        self._session = requests.Session()
        self._timeout = timeout

        # allow configuration of pool
        adapter = HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize)
        self._session.mount("http://", adapter)

        if username and password:
            self._session.auth = (username, password)

    def _call(self, method, apipath, params: dict | None = None, data=None, files=None):
        if str(method).upper() not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError(f"invalid method <{method}>")
        basepath = f"{self._serverurl}/api/v1/{apipath}"

        hd = {"Accept": "application/json", "Content-Type": "application/json"}

        # Split url
        schema, netloc, path, par, query, fragment = urlparse(basepath)
        # URLEncode query string
        query = urlencode(params) if params else ""
        # recombine url
        url = urlunparse((schema, netloc, path, par, query, fragment))

        try:
            resp = self._session.request(
                method, url, headers=hd, timeout=self._timeout, data=json.dumps(data)
            )
            # return resp.text
            return resp.json()
        except RequestConnectionError:
            logger.warning(f"Connection error - could not connect to {netloc}.")

    def _get(self, apipath, params: ParamsT = None):
        return self._call("GET", apipath, params=params)

    def _delete(self, apipath, params: ParamsT = None):
        return self._call("DELETE", apipath, params=params)

    def _post(self, apipath, params: ParamsT = None, data: PostDataT = None):
        return self._call("POST", apipath, params=params, data=data)

    def start(self):
        """Start the bot if it's in the stopped state.

        :return: json object
        """
        return self._post("start")

    def stop(self):
        """Stop the bot. Use `start` to restart.

        :return: json object
        """
        return self._post("stop")

    def stopbuy(self):
        """Stop buying (but handle sells gracefully). Use `reload_config` to reset.

        :return: json object
        """
        return self._post("stopbuy")

    def reload_config(self):
        """Reload configuration.

        :return: json object
        """
        return self._post("reload_config")

    def balance(self):
        """Get the account balance.

        :return: json object
        """
        return self._get("balance")

    def count(self):
        """Return the amount of open trades.

        :return: json object
        """
        return self._get("count")

    def entries(self, pair=None):
        """Returns List of dicts containing all Trades, based on buy tag performance
        Can either be average for all pairs or a specific pair provided

        :return: json object
        """
        return self._get("entries", params={"pair": pair} if pair else None)

    def exits(self, pair=None):
        """Returns List of dicts containing all Trades, based on exit reason performance
        Can either be average for all pairs or a specific pair provided

        :return: json object
        """
        return self._get("exits", params={"pair": pair} if pair else None)

    def mix_tags(self, pair=None):
        """Returns List of dicts containing all Trades, based on entry_tag + exit_reason performance
        Can either be average for all pairs or a specific pair provided

        :return: json object
        """
        return self._get("mix_tags", params={"pair": pair} if pair else None)

    def locks(self):
        """Return current locks

        :return: json object
        """
        return self._get("locks")

    def delete_lock(self, lock_id):
        """Delete (disable) lock from the database.

        :param lock_id: ID for the lock to delete
        :return: json object
        """
        return self._delete(f"locks/{lock_id}")

    def lock_add(self, pair: str, until: str, side: str = "*", reason: str = ""):
        """Lock pair

        :param pair: Pair to lock
        :param until: Lock until this date (format "2024-03-30 16:00:00Z")
        :param side: Side to lock (long, short, *)
        :param reason: Reason for the lock
        :return: json object
        """
        data = [{"pair": pair, "until": until, "side": side, "reason": reason}]
        return self._post("locks", data=data)

    def daily(self, days=None):
        """Return the profits for each day, and amount of trades.

        :return: json object
        """
        return self._get("daily", params={"timescale": days} if days else None)

    def weekly(self, weeks=None):
        """Return the profits for each week, and amount of trades.

        :return: json object
        """
        return self._get("weekly", params={"timescale": weeks} if weeks else None)

    def monthly(self, months=None):
        """Return the profits for each month, and amount of trades.

        :return: json object
        """
        return self._get("monthly", params={"timescale": months} if months else None)

    def profit(self):
        """Return the profit summary.

        :return: json object
        """
        return self._get("profit")

    def stats(self):
        """Return the stats report (durations, sell-reasons).

        :return: json object
        """
        return self._get("stats")

    def performance(self):
        """Return the performance of the different coins.

        :return: json object
        """
        return self._get("performance")

    def status(self):
        """Get the status of open trades.

        :return: json object
        """
        return self._get("status")

    def version(self):
        """Return the version of the bot.

        :return: json object containing the version
        """
        return self._get("version")

    def show_config(self):
        """Returns part of the configuration, relevant for trading operations.
        :return: json object containing the version
        """
        return self._get("show_config")

    def ping(self):
        """simple ping"""
        configstatus = self.show_config()
        if not configstatus:
            return {"status": "not_running"}
        elif configstatus["state"] == "running":
            return {"status": "pong"}
        else:
            return {"status": "not_running"}

    def logs(self, limit=None):
        """Show latest logs.

        :param limit: Limits log messages to the last <limit> logs. No limit to get the entire log.
        :return: json object
        """
        return self._get("logs", params={"limit": limit} if limit else {})

    def trades(self, limit=None, offset=None, order_by_id=True):
        """Return trades history, sorted by id (or by latest timestamp if order_by_id=False)

        :param limit: Limits trades to the X last trades. Max 500 trades.
        :param offset: Offset by this amount of trades.
        :param order_by_id: Sort trades by id (default: True). If False, sorts by latest timestamp.
        :return: json object
        """
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if not order_by_id:
            params["order_by_id"] = False
        return self._get("trades", params)

    def list_open_trades_custom_data(self, key=None, limit=100, offset=0):
        """List open trades custom-data of the running bot.

        :param key: str, optional - Key of the custom-data
        :param limit: limit of trades
        :param offset: trades offset for pagination
        :return: json object
        """
        params = {}
        params["limit"] = limit
        params["offset"] = offset
        if key is not None:
            params["key"] = key

        return self._get("trades/open/custom-data", params=params)

    def list_custom_data(self, trade_id, key=None):
        """List custom-data of the running bot for a specific trade.

        :param trade_id: ID of the trade
        :param key: str, optional - Key of the custom-data
        :return: JSON object
        """
        params = {}
        params["trade_id"] = trade_id
        if key is not None:
            params["key"] = key

        return self._get(f"trades/{trade_id}/custom-data", params=params)

    def trade(self, trade_id):
        """Return specific trade

        :param trade_id: Specify which trade to get.
        :return: json object
        """
        return self._get(f"trade/{trade_id}")

    def delete_trade(self, trade_id):
        """Delete trade from the database.
        Tries to close open orders. Requires manual handling of this asset on the exchange.

        :param trade_id: Deletes the trade with this ID from the database.
        :return: json object
        """
        return self._delete(f"trades/{trade_id}")

    def cancel_open_order(self, trade_id):
        """Cancel open order for trade.

        :param trade_id: Cancels open orders for this trade.
        :return: json object
        """
        return self._delete(f"trades/{trade_id}/open-order")

    def whitelist(self):
        """Show the current whitelist.

        :return: json object
        """
        return self._get("whitelist")

    def blacklist(self, *args):
        """Show the current blacklist.

        :param add: List of coins to add (example: "BNB/BTC")
        :return: json object
        """
        if not args:
            return self._get("blacklist")
        else:
            return self._post("blacklist", data={"blacklist": args})

    def forcebuy(self, pair, price=None):
        """Buy an asset.

        :param pair: Pair to buy (ETH/BTC)
        :param price: Optional - price to buy
        :return: json object of the trade
        """
        data = {"pair": pair, "price": price}
        return self._post("forcebuy", data=data)

    def forceenter(
        self,
        pair,
        side,
        price=None,
        *,
        order_type=None,
        stake_amount=None,
        leverage=None,
        enter_tag=None,
    ):
        """Force entering a trade

        :param pair: Pair to buy (ETH/BTC)
        :param side: 'long' or 'short'
        :param price: Optional - price to buy
        :param order_type: Optional keyword argument - 'limit' or 'market'
        :param stake_amount: Optional keyword argument - stake amount (as float)
        :param leverage: Optional keyword argument - leverage (as float)
        :param enter_tag: Optional keyword argument - entry tag (as string, default: 'force_enter')
        :return: json object of the trade
        """
        data = {
            "pair": pair,
            "side": side,
        }

        if price:
            data["price"] = price

        if order_type:
            data["ordertype"] = order_type

        if stake_amount:
            data["stakeamount"] = stake_amount

        if leverage:
            data["leverage"] = leverage

        if enter_tag:
            data["entry_tag"] = enter_tag

        return self._post("forceenter", data=data)

    def forceexit(self, tradeid, ordertype=None, amount=None):
        """Force-exit a trade.

        :param tradeid: Id of the trade (can be received via status command)
        :param ordertype: Order type to use (must be market or limit)
        :param amount: Amount to sell. Full sell if not given
        :return: json object
        """

        return self._post(
            "forceexit",
            data={
                "tradeid": tradeid,
                "ordertype": ordertype,
                "amount": amount,
            },
        )

    def strategies(self):
        """Lists available strategies

        :return: json object
        """
        return self._get("strategies")

    def strategy(self, strategy):
        """Get strategy details

        :param strategy: Strategy class name
        :return: json object
        """
        return self._get(f"strategy/{strategy}")

    def pairlists_available(self):
        """Lists available pairlist providers

        :return: json object
        """
        return self._get("pairlists/available")

    def plot_config(self):
        """Return plot configuration if the strategy defines one.

        :return: json object
        """
        return self._get("plot_config")

    def available_pairs(self, timeframe=None, stake_currency=None):
        """Return available pair (backtest data) based on timeframe / stake_currency selection

        :param timeframe: Only pairs with this timeframe available.
        :param stake_currency: Only pairs that include this timeframe
        :return: json object
        """
        return self._get(
            "available_pairs",
            params={
                "stake_currency": stake_currency if timeframe else "",
                "timeframe": timeframe if timeframe else "",
            },
        )

    def pair_candles(self, pair, timeframe, limit=None, columns=None):
        """Return live dataframe for <pair><timeframe>.

        :param pair: Pair to get data for
        :param timeframe: Only pairs with this timeframe available.
        :param limit: Limit result to the last n candles.
        :param columns: List of dataframe columns to return. Empty list will return OHLCV.
        :return: json object
        """
        params = {
            "pair": pair,
            "timeframe": timeframe,
        }
        if limit:
            params["limit"] = limit

        if columns is not None:
            params["columns"] = columns
            return self._post("pair_candles", data=params)

        return self._get("pair_candles", params=params)

    def pair_history(self, pair, timeframe, strategy, timerange=None, freqaimodel=None):
        """Return historic, analyzed dataframe

        :param pair: Pair to get data for
        :param timeframe: Only pairs with this timeframe available.
        :param strategy: Strategy to analyze and get values for
        :param freqaimodel: FreqAI model to use for analysis
        :param timerange: Timerange to get data for (same format than --timerange endpoints)
        :return: json object
        """
        return self._get(
            "pair_history",
            params={
                "pair": pair,
                "timeframe": timeframe,
                "strategy": strategy,
                "freqaimodel": freqaimodel,
                "timerange": timerange if timerange else "",
            },
        )

    def sysinfo(self):
        """Provides system information (CPU, RAM usage)

        :return: json object
        """
        return self._get("sysinfo")

    def health(self):
        """Provides a quick health check of the running bot.

        :return: json object
        """
        return self._get("health")
