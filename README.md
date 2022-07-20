# COVID-19 Vaccine Notification Bots
This repository contains some of the Python scripts I wrote in March 2021 to tweet out available COVID-19 vaccine appointments. The code was run 24/7 from 3/20/21 to 5/3/21 on an Azure VM. More than 17,000 appointments were tweeted out and were collectively viewed more that 950 thousand times. The accounts used to tweet were [@LongIslandVax](https://twitter.com/longislandvax), [@azvaccinebot](https://twitter.com/azvaccinebot), and [@ConnecticutVax](https://twitter.com/connecticutvax). Also, thanks to [Nick Muerdter](https://twitter.com/nickblah) for creating the Vaccine Spotter API. 



NOTE: To replicate, you must download [Chromedriver](https://chromedriver.chromium.org/) and fill in your own Twitter Developer API keys. Also, [cvs-vaccine-bot.py](cvs-vaccine-bot.py) cannot be used anymore because of changes to CVS website, however [ct-vaccine-bot.py](ct-vaccine-bot.py) can still be used as of Aug 2021. The final bot, [us-messaging-system.py](us-messaging-system.py) sends emails to subscribers instead of tweets, but was never released due to quantity limits and limited options of communication.
