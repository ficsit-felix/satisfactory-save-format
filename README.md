# satisfactory-save-format
Repository containing the scripts I used to dissect the save files of Satisfactory.

Contains two scripts to convert to a readable json format and back to a sav file.

```
usage: sav2json.py [-h] [--output OUTPUT] [--pretty] [--split] FILE

Converts Satisfactory save games into a more readable format
```

```
usage: json2sav.py [-h] [--output OUTPUT] [--split] FILE

Converts from the more readable format back to a Satisfactory save game
```

## Split into multiple 
If the option `--split` is used the big json file is split into multiple smaller json files in different directories with the following structure:
```
output-name
│   index.json
│
└───actors
│   │   0.json
│   │   1.json
│   │   ...
│   
└───components
    │   0.json
    │   1.json
    │   ...
```


## Other useful repositories

https://github.com/Vilsol/satisfactory-tool  
Save file to json converter written in Go

https://github.com/bitowl/ficsit-felix  
Web app to visualize save files

https://github.com/Goz3rr/SatisfactorySaveEditor  
Save file editor for Windows written in C#
