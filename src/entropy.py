import os
import binascii
import serial
import argparse
import random
from datetime import datetime


ENTROPY_LEN = 32 # 32 = 256 bits / 8 bits_per_Byte


def _add_argument_parser():
    parser = argparse.ArgumentParser(description = 'Generate entropy')
    parser.add_argument(
        "-s",
        "--symbol",
        nargs = "?",
        required = True,
        help = "Symbol name of cryptocurrency"
    )
    parser.add_argument(
        "-c",
        "--count",
        type = int,
        nargs = "?",
        required = True,
        help = "How many of entropy entropies to generate."
    )
    parser.add_argument(
        "-d",
        "--default_dir_path",
        nargs = "?",
        default = "/app/wallet",
        help = "Root path of wallet."
    )
    parser.add_argument(
        "-m",
        "--message",
        nargs = "?",
        required = True,
        help = "Message for reminding about this batch of entropy."
    )
    args = parser.parse_args()
    return args


def _read_rng():
    """
	stty raw -echo </dev/ttyACM1	# put the tty device into raw mode (no echo, treat special
					# like any other characters)
	echo	cmd0 >/dev/ttyACM1	# put the device into the avalanche/whitening mode
	echo	cmdO >/dev/ttyACM1	# turn on the feed to the USB
        reference link: http://moonbaseotago.com/onerng/
    """
    with serial.Serial('/dev/ttyACM0') as _rng_dev:
        _rng_dev.write(b'cmd0')
        _rng_dev.write(b'cmdO')

        rslt = 0
        for index in range(10):
            raw_entropy = _rng_dev.read(ENTROPY_LEN)
            entropy_str = binascii.hexlify(raw_entropy).decode('ascii')
            if index % 2:
                chars_list = list(entropy_str)
                random.shuffle(chars_list)
                entropy_str = ''.join(chars_list)
            entropy = int(entropy_str, base=16)
            rslt = rslt ^ entropy

    return rslt


def _read_random():
    """
        Generate a random number from a specified device
    """
    with open("/dev/random", "rb") as _random_source:
        raw_entropy = _random_source.read(ENTROPY_LEN)
        entropy = binascii.hexlify(raw_entropy).decode('ascii')
    return int(entropy, base=16)


def generate_entropies(count):
    """
       generate an 256 bits entropy number by /dev/random xor /dev/ttypACM0 
    """
    entropies = []

    for current in range(count):
        print(f"Generating the {current+1}th entropy ...")
        entropy = ""

        rdm_num = _read_random()
        while len(entropy) != ENTROPY_LEN * 2:
            hwrng_num = _read_rng()
            xor_rslt = rdm_num ^ hwrng_num
            entropy = hex(xor_rslt).lstrip('0x')

        entropies.append(entropy)

    return entropies


def save_entropies(root_dir, symbol, entropies):
    filepath = os.path.join(root_dir, symbol)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filepath, 'a') as p:
        p.write(f"# {args.message}\n")
        p.write(f"# Generated time {current_time}\n")
        for entropy in entropies:
            p.write(f"{entropy}\n")
        p.write('\n\n\n')


def load_entropies(root_dir, symbol, all_lines=True):
    filepath = os.path.join(root_dir, symbol)
    if not os.path.isfile(filepath):
        print(f"Symbol {symbol}'s entropy file not exits")
        exit()

    entropies = [] 
    with open(filepath) as p:
        for line in p.readlines():
            entropy = line.strip()
            if all_lines:
                entropies.append(entropy)
                continue
            if not entropy or entropy.startswith('#'):
                continue
            entropies.append(entropy)

    return entropies


if __name__ == "__main__":
    args = _add_argument_parser()
    entropies = generate_entropies(args.count)
    save_entropies(args.default_dir_path, args.symbol, entropies)
    for entropy in entropies:
        print(entropy)
