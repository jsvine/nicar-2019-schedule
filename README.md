# NICAR 2019 Schedule as Structured Data

This repository contains the [NICAR 2019 conference schedule](https://www.ire.org/events-and-training/conferences/nicar-2019/schedule) as JSON and CSV files, plus the underlying Python scraper.

*Going to NICAR? You might be interested in the [data, analyses, and tools we've open-sourced at BuzzFeed News](https://github.com/buzzfeednews/everything).*

## Get the data

*Last updated March 9, 2019 @ 9:00am Pacific*

- [JSON schedule](schedule/nicar-2019-schedule.json?raw=true)
- [CSV schedule](schedule/nicar-2019-schedule.csv?raw=true)

## Run the scraper yourself

To run the scraper, you'll need Python 3. To get started, execute the following commands in your terminal:

```bash
mkvirtualenv nicar-2019-schedule # Optional, recommended
git clone https://github.com/jsvine/nicar-2019-schedule.git
cd nicar-2019-schedule
pip install -r requirements.txt
```

To run the scraper, execute this command:

```bash
make schedule
```

## Look beneath the hood

You can find the Python script that extracts and formats the schedule [here](scripts/scrape.py).

## Fix/improve things

Pull requests are welcome.
