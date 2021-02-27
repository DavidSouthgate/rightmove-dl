# Rightmove DL
A simple script to download assets and data from Rightmove.

## Example
```bash
python src/rightmove-dl.py https://www.rightmove.co.uk/properties/98180450/
```

## Rightmove CSV
This project also contains a script called `rightmove-csv`. This is a simple script that reads all of the directories created by `rightmove-dl` in the current working directory - and generates a CSV file `properties.csv` for comparison.

## Quick Installation
1. Clone repo
2. Setup alias to point to rightmove-dl.sh for the command rightmove-dl

E.g. Where repo is cloned to `/Users/d/repos/rightmove-dl`
```
alias rightmove-dl="/Users/d/repos/rightmove-dl/bin/rightmove-dl.sh"
alias rightmove-csv="/Users/d/repos/rightmove-dl/bin/rightmove-csv.sh"
```