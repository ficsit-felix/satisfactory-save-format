# satisfactory-save-format


---
**IMPORTANT** 
This repository is currently not maintained. It was mainly created to reverse engineer the save files and is not very performant. You can find a maintained version written in TypeScript at [satisfactory-json](https://github.com/ficsit-felix/satisfactory-json).

---

Repository containing the scripts I used to dissect the save files of Satisfactory.

Contains two scripts to convert to a readable json format and back to a sav file.

```
usage: sav2json.py [-h] [--output OUTPUT] [--pretty] FILE

Converts Satisfactory save games into a more readable format
```

```
usage: json2sav.py [-h] [--output OUTPUT] FILE

Converts from the more readable format back to a Satisfactory save game
```

## Other useful repositories

https://github.com/Vilsol/satisfactory-tool  
Save file to json converter written in Go

https://github.com/bitowl/ficsit-felix  
Web app to visualize save files

https://github.com/Goz3rr/SatisfactorySaveEditor  
Save file editor for Windows written in C#
