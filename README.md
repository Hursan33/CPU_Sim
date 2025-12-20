# CPU_Sim
Simple cpu simulation designed in Digital

To run the code compiled via the `compiler.py` file:
```
python3 compiler.py <your_file.cpu>
```
Add the program.hex file into the ROM component in `main.dig`.

Please do not use the STR and LOD instructions, they are for internal use only, instead use STA and LDA which can be
used with both register and specific address.

To add the colors and text finishing install the mycpu_lang extension in the project using `INSTALL from VSIX` option and into user settings in vscode insert
```
"editor.tokenColorCustomizations": {
        "textMateRules": [
            {
                "scope": "label.cpu",
                "settings": {
                    "foreground": "#e63e49",  // Grey color for comments
                    //"fontStyle": "italic"     // Optional: make comments italic
                }
            },
            {
                "scope": "register.cpu",
                "settings": {
                    "foreground": "#f3b256",  // Grey color for comments
                    //"fontStyle": "italic"     // Optional: make comments italic
                }
            },
            {
                "scope": "var.cpu",
                "settings": {
                    "foreground": "#8cf5db",  // Grey color for comments
                    //"fontStyle": "italic"     // Optional: make comments italic
                }
            }
        ]
    }
```
