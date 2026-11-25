# Capstone: Make the Computer Draw a Box

Nand to Tetris – I (ETCCNT301), K.R. Mangalam University

**Name:** Harsh | **Roll no:** 2501730341 | **K = 41**

| Item | Value for K = 41 |
|---|---|
| Box first row | 41 (rows 41 to 60) |
| Box height | 20 rows |
| Box width | 16 × ((41 mod 4) + 1) = 16 × 2 = **32 px** (2 words) from the left edge |
| Assembler extra feature | 41 mod 3 = **2**: clear error message with the line number |

## Folder layout

```
capstone/
├── hdl/                 Part A: CPU.hdl, Memory.hdl, Computer.hdl + my gates and ALU
├── lab-chips/           My project 03 chips (Bit, Register, RAM8..RAM16K, PC)
├── assembler.py         Part B: two-pass Hack assembler in Python
├── Box.asm              Part C: the box program
├── Box.hack             Box.asm assembled with MY assembler
├── tests/
│   ├── compare.sh       assembles Add/Max/Rect/Pong and compares with the official output
│   ├── asm/             test programs + official assembler output
│   ├── Bad.asm          a program full of mistakes (for the error feature)
│   └── Bad_output.txt   what my assembler prints for it
└── screenshots/         test results and the box
```

## Part A – Build the computer

`hdl/` holds `CPU.hdl`, `Memory.hdl`, `Computer.hdl` plus my own gates and ALU from
projects 01–02. To test, copy the official `.tst`/`.cmp` files from `projects/05`
into `hdl/`, open the Hardware Simulator, load each script and run it.

Results: `CPU.tst`, `Memory.tst`, `ComputerAdd.tst`, `ComputerMax.tst` and
`ComputerRect.tst` all end with *"Comparison ended successfully"*
(screenshots `A1`–`A5`).

**Built-in chips used:** `PC`, `ARegister`, `DRegister`, `RAM16K`, `Screen`,
`Keyboard`, `ROM32K`. The official Computer tests read `PC[]` and `RAM16K[]`
directly, which only works with the built-in versions. My own gate-level
`RAM16K` also ran out of Java heap memory in the simulator. My own versions are
in `lab-chips/`, and each one passes its own project 03 test.

## Part B – Assembler

```
python3 assembler.py Prog.asm            # writes Prog.hack
bash tests/compare.sh                    # checks Add, Max, Rect, Pong
```

* **First reading:** removes comments and blank lines and stores each label `(LOOP)` with its ROM address.
* **Second reading:** turns each line into 16 bits. New variables get RAM 16, 17, 18, …
* **Extra feature (K mod 3 = 1):** a wrong line prints `Line N: invalid instruction '...'`.
  All errors are listed and no `.hack` file is written. See `tests/Bad.asm`.

The output matches the official assembler byte for byte on Add, Max, Rect and Pong (27,483 lines).

## Part C – Box.asm

The main loop reads `KBD`. If a key is down, `color = -1` (black), otherwise `color = 0` (white).
It then paints 20 rows × 2 words starting at `SCREEN + 32*61`.

`32*row` is worked out by doubling `row` five times. That way the box can be moved by
changing a single number.

| To change | Edit in `Box.asm` (SETUP) |
|---|---|
| first row (move box down/up) | `@61` |
| height | `@20` |
| width (in 16-px words) | `@2` |

Then re-assemble with `python3 assembler.py Box.asm` and load `Box.hack` in the CPU Emulator.
