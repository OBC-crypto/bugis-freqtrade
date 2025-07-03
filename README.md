# bugis-freqtrade

# 

**Bugis-freqtrade Bot** adalah versi modifikasi dari [Freqtrade](https://github.com/freqtrade/freqtrade), sebuah open-source cryptocurrency trading bot, yang telah saya sesuaikan dengan konfigurasi, strategi, dan kebutuhan eksperimen saya sendiri.

Command :
sudo apt install screen -y
chmod +x setup.sh
./setup.sh
./setup.sh -i

source .venv/bin/activate freqtrade --version

freqtrade hyperopt --config config.json --strategy MyStrategy
 
freqtrade backtesting --config config.json --strategy NaiveStrategy

freqtrade trade --config config.json --strategy NaiveStrategy --dry-run


