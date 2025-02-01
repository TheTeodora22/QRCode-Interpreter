import concatenate as ct
import sys
"""
Reed-Solomon Encoder for a QR Code (Single Block)

This script demonstrates how to compute RS error correction codewords
for a QR code using a single block containing:
    - 19 data codewords
    - 7 ECC codewords

The field GF(256) is built with the primitive polynomial:
    x^8 + x^4 + x^3 + x^2 + 1  (hex 0x11D)

The generator polynomial is computed as:
    g(x) = (x - α^0)(x - α^1) ... (x - α^(nsym-1))
where nsym is the number of ECC codewords (7 in this example).
"""

# -------------------------------------------------------------------
# GF(256) arithmetic using lookup tables
# -------------------------------------------------------------------

def init_tables(primitive=0x11d):
    """
    Initializes the exponential and logarithm tables for GF(256).

    Returns:
        exp_table: list of 512 elements (to simplify multiplication mod 255)
        log_table: list of 256 elements
    """
    exp_table = [0] * 512
    log_table = [0] * 256
    x = 1
    for i in range(255):
        exp_table[i] = x
        log_table[x] = i
        x <<= 1
        if x & 0x100:  # if degree >= 8, reduce modulo the primitive polynomial
            x ^= primitive
    # Duplicate the first 255 elements to avoid modular reduction in multiplication
    for i in range(255, 512):
        exp_table[i] = exp_table[i - 255]
    return exp_table, log_table

def gf_mul(x, y, exp_table, log_table):
    """
    Multiply two numbers in GF(256).
    """
    if x == 0 or y == 0:
        return 0
    return exp_table[log_table[x] + log_table[y]]

def gf_poly_mul(p, q, exp_table, log_table):
    """
    Multiply two polynomials over GF(256).

    p and q are lists of coefficients (lowest order first).
    """
    result = [0] * (len(p) + len(q) - 1)
    for i, coef_p in enumerate(p):
        for j, coef_q in enumerate(q):
            result[i+j] ^= gf_mul(coef_p, coef_q, exp_table, log_table)
    return result

# -------------------------------------------------------------------
# Reed-Solomon encoding routines
# -------------------------------------------------------------------

def rs_generator_poly(nsym, exp_table, log_table):
    """
    Generate the Reed–Solomon generator polynomial for nsym ECC codewords.
    
    The generator polynomial is:
        g(x) = (x - α^0)(x - α^1)...(x - α^(nsym-1))
    
    Returns:
        A list of coefficients for g(x) (lowest order first).
    """
    g = [1]
    for i in range(nsym):
        # Note: (x - α^i) is equivalent to (x + α^i) in GF(256)
        g = gf_poly_mul(g, [1, exp_table[i]], exp_table, log_table)
    return g

def rs_encode_msg(msg_in, nsym, exp_table, log_table):
    """
    Given a message (list of data codewords) and the number of ECC symbols nsym,
    compute the Reed–Solomon ECC codewords.

    The algorithm works by dividing the message polynomial multiplied by x^(nsym)
    by the generator polynomial and returning the remainder.
    
    Args:
        msg_in: list of integers (data codewords)
        nsym: number of ECC codewords to generate
        exp_table, log_table: lookup tables for GF(256)

    Returns:
        List of ECC codewords.
    """
    gen = rs_generator_poly(nsym, exp_table, log_table)
    # Make a copy of msg_in and append nsym zeroes (this is like multiplying by x^(nsym))
    msg_out = msg_in[:] + [0] * nsym
    for i in range(len(msg_in)):
        coef = msg_out[i]
        if coef != 0:
            # Multiply the generator polynomial by coef and subtract (XOR in GF(256))
            for j in range(1, len(gen)):
                msg_out[i+j] ^= gf_mul(gen[j], coef, exp_table, log_table)
    # The remainder (last nsym coefficients) are the ECC codewords.
    ecc = msg_out[len(msg_in):]
    return ecc

# -------------------------------------------------------------------
# Main: Demonstration using your QR code parameters
# -------------------------------------------------------------------

def final_codewords(input_text):
    # Initialize GF(256) tables.
    exp_table, log_table = init_tables()

    # Data codewords for block 0 (provided in your model)
    # (Note: They are given in hexadecimal.)
    data_codewords = ct.concatenate(input_text)

    nsym = 20  # Number of ECC codewords

    # Compute the ECC codewords using the RS encoder.
    ecc_codewords = rs_encode_msg(data_codewords, nsym, exp_table, log_table)

    # Final sequence: Data followed by ECC.
    final_codewords = data_codewords + ecc_codewords

    # Print out the results in hexadecimal.
    return ("".join(f"{cw:08b}" for cw in final_codewords))

