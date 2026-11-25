// Box.asm - Nand to Tetris capstone, K = 41
//
// While any key is pressed, a black box is drawn on the screen.
// When the key is released, the box is cleared (white).
//
// My box (K = 41):
//   starts at row K = 41
//   20 rows tall           -> rows 41 .. 60
//   16 * ((41 mod 4) + 1) = 16 * 2 = 32 pixels wide = 2 words, from the left edge
//
// Screen facts: one row = 32 words, one word = 16 pixels.
// Row r starts at address SCREEN + 32*r.
//
// To change the box, edit only the three numbers in SETUP:
//   @41 = first row,  @20 = height in rows,  @2 = width in words.

(MAIN)
    // ---- check the keyboard: color = -1 (black) if a key is down, else 0 ----
    @KBD
    D=M
    @PRESSED
    D;JNE
    @color
    M=0             // no key -> white
    @SETUP
    0;JMP
(PRESSED)
    @color
    M=-1            // key -> black (all 16 bits = 1)

(SETUP)
    // ---- box size ----
    @41
    D=A
    @row
    M=D             // row = 41 (first row of the box)
    @20
    D=A
    @height
    M=D             // height = 20 rows
    @2
    D=A
    @width
    M=D             // width = 2 words = 32 pixels

    // ---- addr = SCREEN + 32*row  (32*row = row doubled 5 times) ----
    @row
    D=M
    D=D+M           // 2*row
    @temp
    M=D
    D=D+M           // 4*row
    M=D
    D=D+M           // 8*row
    M=D
    D=D+M           // 16*row
    M=D
    D=D+M           // 32*row
    @SCREEN
    D=D+A
    @addr
    M=D             // addr = first word of the box

    @height
    D=M
    @rowsLeft
    M=D             // rowsLeft = height

(ROWLOOP)
    // ---- paint one row: 'width' words starting at addr ----
    @addr
    D=M
    @ptr
    M=D             // ptr = addr
    @width
    D=M
    @wordsLeft
    M=D             // wordsLeft = width
(WORDLOOP)
    @color
    D=M
    @ptr
    A=M
    M=D             // RAM[ptr] = color
    @ptr
    M=M+1           // ptr = ptr + 1
    @wordsLeft
    MD=M-1
    @WORDLOOP
    D;JGT           // more words in this row?

    // ---- move to the next row ----
    @32
    D=A
    @addr
    M=D+M           // addr = addr + 32
    @rowsLeft
    MD=M-1
    @ROWLOOP
    D;JGT           // more rows?

    @MAIN
    0;JMP           // check the keyboard again, forever
