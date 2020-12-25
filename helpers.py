INT8 = [(i ^ 0x80) - 0x80 for i in range(256)]
BITX = [[i >> j & 0x1 for i in range(256)] for j in range(8)]
BIT0, BIT1, BIT2, BIT3, BIT4, BIT5, BIT6, BIT7 = BITX
RES0, RES1, RES2, RES3, RES4, RES5, RES6, RES7 = [[i & ~(0x1 << j) for i in range(256)] for j in range(8)]
SET0, SET1, SET2, SET3, SET4, SET5, SET6, SET7 = [[i | 0x1 << j for i in range(256)]for j in range(8)]
BITS1_0 = [i & 0x3 for i in range(256)]