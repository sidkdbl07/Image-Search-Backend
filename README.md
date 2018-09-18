# ImageSearch Backend
This is a Python-based backend to the ImageSearch tool. It has two parts:
1. Crawler - find, update and remove images from the search engine
2. Processor - process (i.e. classify, thumbnail, and search for duplicates)

## Crawler
```
python main.py -m crawler -d <str:local dir> -s <str:serverpath> -l <int:limit>
```
Will recursively search for images, and add them to the database.

## Processor
```
python main.py -m processor -d <str:local dir> -s <str:serverpath>
```
