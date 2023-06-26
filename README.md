
## Local install

```sh
# create venv in git bash
conda create -n immo-fr python=3.8
conda init bash # restart shell window
conda activate immo-fr

conda install -c conda-forge pydrive  dateparser beautifulsoup4 selenium lxml

# python3 -m venv facture-approchement

pip3 install ipykernel
# conda deactivate
# launch notebook
jupyter notebook --debug
```


## Entry function:

```py
simple_match(releves_pd_cleaned[['settlement_date_local', 'counterpart_name','amount', 'amount_currency']],receipts)
```


## Output:

```sh
Checking ADEO*LEROY MERLIN
...Average similarity 65 over 1 lines.
......Find a line: lerov merlin nanterre with similarity ration 65/100
"...Found matched receipts: ['cas detaillé avec TVA.txt']"
Found -123,85 matchs 123.85 in line "sum" of "cas detaillé avec TVA.txt".

Checking NANIWA-YA
...Average similarity 78 over 1 lines.
......Find a line: haniwa-va with similarity ration 78/100
"...Found matched receipts: ['cas detaillé avec TVA caractères spéciaux.txt']"
Found -35,00 matchs 35.00 in line "sum" of "cas detaillé avec TVA caractères spéciaux.txt".

Checking TOTAL
...Average similarity 100 over 1 lines.
......Find a line: total vous remercie  with similarity ration 100/100
...Average similarity 100 over 1 lines.
......Find a line: total 35,00 eur with similarity ration 100/100
...Average similarity 100 over 1 lines.
......Find a line: total (eur) 123.85  with similarity ration 100/100
...Average similarity 100 over 1 lines.
......Find a line: total with similarity ration 100/100
...Average similarity 100 over 1 lines.
......Find a line: total €24.29 with similarity ration 100/100
...Average similarity 100 over 1 lines.
......Find a line: total euro : 44,90 with similarity ration 100/100
("...Found matched receipts: ['cas detaillé avec chiffre volumineux.txt', 'cas "
 "detaillé avec TVA caractères spéciaux.txt', 'cas detaillé avec TVA.txt', "
 "'cas detaillé montant non conforme.txt', 'cas detaillé nom non "
 "conforme.txt', 'cas ecriture releve absent.txt']")
Found -67,76 matchs 67,76 in line "67, 76 eur " of "cas detaillé avec chiffre volumineux.txt".

Checking AMZN Digital
...Average similarity 80 over 1 lines.
......Find a line: ald with similarity ration 80/100
...Average similarity 60 over 1 lines.
......Find a line: total with similarity ration 60/100
("...Found matched receipts: ['cas detaillé avec chiffre volumineux.txt', 'cas "
 "detaillé montant non conforme.txt']")
Not match found for -50,00

Checking AMZN Mktp FR*RY2WT2TN5
No matched filename found. Blind searching...
Found -26,99 matchs 26,99 in line "07-oct-20 1 21.0 €26.99 €24.29 €4.22 €20.07" of "cas detaillé nom non conforme.txt".

Checking AMZN Mktp FR amazon.fr LU
...Average similarity 60 over 1 lines.
......Find a line: veuillez contacter le service client en visitant le lien suivant: www.amazon.fr/contact-us with similarity ration 60/100
"...Found matched receipts: ['cas detaillé montant non conforme.txt']"
Not match found for -25,82

Checking LA POSTE L920730 SURESNES PAL FR
No matched filename found. Blind searching...
Not match found for -6,00
```


