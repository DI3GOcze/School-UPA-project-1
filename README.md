Pro zprovoznění projektu nejprve nutné naistalovat závislosti. Nainstalujete následujícím příkazem:

```
pip install -r requirements.txt
```

Dále je potřeba mít sprovozněnou databázi mongodb.

V souboru config.py si nastavte connection string na vaši mongodb databázi a název databáze, do které se budou ukládat data.

Následně je možné program spustit ve 4 módech:

1. Stažení a nahrání nejnovější verze dat:
```
python main.py --parse_all
```

<br/>

1. Stažení a nahrání základních dat 
```
python main.py --parse_base
```

<br/>

1. Stažení a nahrání dat z konkrétního měsíce
```
python main.py --parse_month <month>
```
- &lt;month&gt; ve formátu YYYY-mm určuje který měsíc se vybere


<br/>

4. Stažení a nahrání nejnovější verze dat:
```
python main.py --search <startStation> <destStation> <date> 
```
- &lt;startStation&gt; název startovací stanice ve formátu string

- &lt;destStation&gt; název cílové stanice ve formátu string

- &lt;date&gt; datum spoje ve formátu YYYY-mm-dd 
