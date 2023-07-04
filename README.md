
## Local install

```sh
# create venv in git bash
conda create -n immo-fr python=3.8
conda init bash # restart shell window
conda activate immo-fr

conda install -c conda-forge pydrive  dateparser beautifulsoup4 selenium lxml PIL

# python3 -m venv facture-approchement

pip3 install ipykernel
# conda deactivate
# launch notebook
jupyter notebook --debug
```

## Steps

### 1. Collect geoinfo

```sh

python infobailleur.py

```

### 2. Collect rent info

```sh

python immoScaper.py

```

### 3. Collect pap

```sh

python papScraper.py

```

### 4. Analyze pap

```sh

python papAnlyzer.py

```

### 5. Collect seloger

```sh

python selogerScraper.py

```

### 4. Analyze seloger

The analysis output is in output folder.

```sh

python selogerAnlyzer.py

```
