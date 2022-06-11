#!/usr/bin/env python
import os
import json
import argparse
import qrcode
#import tqdm
import subprocess
import binascii
from mnemonic import Mnemonic
from tabulate import tabulate
from hdwallet.cli import ( click, sys )
from sdk import ( python_hdwallet, symbol, stellar, waves )
from entropy import load_entropies

MODELS = {
    "XYM": {
            "model": symbol,
            "network": "mainnet",
            "semantic": None
        },
    "XYMTEST": {
            "model": symbol,
            "network": "testnet",
            "semantic": None
        },
    "XLM": {
            "model": stellar,
            "network": "mainnet",
            "semantic": None
        },
    "WAVES": {
            "model": waves,
            "network": "mainnet",
            "semantic": None
        },
}

JSMODELS = {
    "DOT": {
            "model": "polkadot",
            "network": "Polkadot",
            "semantic": None
        },
    "DOTKSM": {
            "model": "polkadot",
            "network": "Kusama",
            "semantic": None
        },
    "DOTSUB": {
            "model": "polkadot",
            "network": "Substrate",
            "semantic": None
        },
}

def add_argument_parser():
    parser = argparse.ArgumentParser(description = 'Print wallet info.')
    sub_parser = parser.add_subparsers(help='sub-command help', title='sub commands', description='valid subcommands')
    add_list_parser(sub_parser)
    add_generate_parser(sub_parser)
    return parser.parse_args()

    
# list sub command
def add_list_parser(sub_parser):
    parser = sub_parser.add_parser('list', aliases=['l'], help='Show supported cryptocurrencies list.')
    parser.add_argument(
        "-s",
        "--search_key_words",
        nargs = "?",
        required = False,
        help = "Show fited cryptocurrencies only that the specified key words included in whose symbol or name."
    )
    parser.set_defaults(func=list_cryptocurrencies)
 

# generate sub command
def add_generate_parser(sub_parser):
    parser = sub_parser.add_parser('generate', aliases=['g'], help='Convert entropy to address, public_key, private_key, mnemonic, seed.')
    parser.add_argument(
        "-s",
        "--symbol",
        nargs = "?",
        required = True,
        help = "Symbol name of cryptocurrency"
    )
    parser.add_argument(
        "--wallet_dir_path",
        nargs = "?",
        default = "/app/wallet",
        help = "Root path of wallet, default value is /app/wallet."
    )
    parser.add_argument(
        "--qr_save_dir",
        nargs = "?",
        default = "/app/qrcode",
        help = "Root path of qr code, default value is /app/qrcode."
    )
    parser.add_argument(
        "-a",
        "--address",
        required = False,
        default = False,
        action = 'store_true',
        help = "show address"
    )
    parser.add_argument(
        "-x",
        "--public_key",
        required = False,
        default = False,
        action = 'store_true',
        help = "show public key."
    )
    parser.add_argument(
        "-i",
        "--private_key",
        required = False,
        default = False,
        action = 'store_true',
        help = "show private key."
    )
    parser.add_argument(
        "-e",
        "--seed",
        required = False,
        default = False,
        action = 'store_true',
        help = "show seed."
    )
    parser.add_argument(
        "-m",
        "--mnemonic",
        required = False,
        default = False,
        action = 'store_true',
        help = "show whole words of mnemonic, else, show only the head 3 words of mnemonic"
    )
    parser.add_argument(
        "-k",
        "--entropy",
        required = False,
        default = False,
        action = 'store_true',
        help = "show entropy."
    )
    parser.add_argument(
        "-qr",
        "--qr_code",
        required = False,
        default = False,
        action = 'store_true',
        help = "save the generated qr code of address."
    )
    parser.set_defaults(func=generate_address)


def generate_address(args):
    symbol = args.symbol

    # load content of entropy file
    raw_list = load_entropies(args.wallet_dir_path, symbol)

    last_is_comment = True
    rslt = []
    entropy_list = []
    for entropy in raw_list:
        # deal comment lines of entropy file
        if not entropy or entropy.startswith('#'):
            if not last_is_comment:
                rslt.append([True, entropy_list])
                entropy_list = []
            rslt.append([False, entropy])
            last_is_comment = True
            continue
        
        # generate key, seed, address from entropy
        mnemonic = Mnemonic(language="english").to_mnemonic(data=binascii.unhexlify(entropy))
        seed = binascii.hexlify(Mnemonic.to_seed(mnemonic=mnemonic, passphrase="")).decode()

        if symbol in MODELS:
            crypto = MODELS[symbol]
            document = crypto["model"].generate_address(
                mnemonic,
                crypto["semantic"],
                crypto["network"]
            )
        elif symbol in JSMODELS:
            crypto = JSMODELS[symbol]
            subrslt = subprocess.run(
                [
                    "node",
                    os.path.join("/app/code/js", f'{crypto["model"]}.js'),
                    mnemonic,
                    '', 
                    crypto["network"]
                ],
                capture_output = True
            )
            if subrslt.stderr:
                print(subrslt.stderr)
                exit()
            document = json.loads(subrslt.stdout.decode("ascii"))
        else:
            document = python_hdwallet.generate_address(symbol, entropy, "p2pkh")
        
        document.update({
            "mnemonic": mnemonic,
            "seed": seed,
            "entropy": entropy
        })

        if last_is_comment:
            entropy_list = []
        entropy_list.append(document)
        last_is_comment = False

    if not last_is_comment:
        rslt.append([True, entropy_list])


    # show generated information
    show_dict = {
        "line no.": True,
        "mnemonic": args.mnemonic,
        "address": args.address,
        "public_key": args.public_key,
        "private_key": args.private_key,
        "seed": args.seed,
        "entropy": args.entropy,
    }
    order_number = 0
    for flag, documents in rslt:
        if not flag:
            print(documents)
            continue

        table, headers = [], []
        for item, value in show_dict.items():
            if value:
                headers.append(item)
 
        for document in documents:
            order_number += 1
            element = [order_number]
            for item, value in show_dict.items():
                if item == 'line no.':
                    continue
                if value:
                    element.append(document[item])
            table.append(element)

        click.echo(tabulate(table, headers, tablefmt="github"))


    # save qr image
    if not args.qr_code or not args.qr_save_dir:
        return
    save_dir = os.path.join(args.qr_save_dir, symbol)
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    order_number = 0
    for flag, documents in rslt:
        if not flag:
            continue
        for document in documents:
            order_number += 1
            address = document["address"]
            img = qrcode.make(address)
            img.save(os.path.join(save_dir, f"{str(order_number).zfill(4)}.{address}.png"))



def list_cryptocurrencies(args):
    if args.search_key_words:
        search_key_words = args.search_key_words.lower()
    else:
        search_key_words = None

    table, headers = [], [
        "Cryptocurrency", "Symbol", "Mainnet", "Testnet", "Segwit", "SDK"
    ]

    # hdwallet
    documents = python_hdwallet.get_cryptocurrencies()
    for document in documents:
        if search_key_words and search_key_words not in document["name"].lower() and search_key_words not in document["symbol"].lower():
            continue 
        table.append([
            document["name"],
            document["symbol"],
            document["mainnet"],
            document["testnet"],
            document["segwit"],
            document["sdk"],
        ])

    # symbol
    if not search_key_words or search_key_words in 'symbol xym xymtest':
        table.append(["symbol", "XYM, XYMTEST", "Yes", "Yes", "No", "symbol"])

    # XLM
    if not search_key_words or search_key_words in 'lumens stellar str xlm':
        table.append(["lumens", "XLM", "Yes", "No", "No", "stellar"])

    # waves
    if not search_key_words or search_key_words in 'waves WAVES':
        table.append(["waves", "WAVES", "Yes", "No", "No", "waves"])

    # polkadot
    if not search_key_words or search_key_words in 'polkadot kusama substrate ksm':
        table.append(["polkadot", "DOT, DOTKSM, DOTSUB", "Yes", "Yes", "No", "polkadot"])

    click.echo(tabulate(table, headers, tablefmt="github"))


if __name__ == "__main__":
    """
    list_cryptocurrencies()
    rslt = generate_address(
        "XYM",
        ["b87d04d6a37c3000a5de6722afaffe7988249f79761268b35e23f9c07fa790cd"],
        show_dict = {
            "entropy": False,
            "mnemonic": True,
            "seed": False,
            "private_key": False,
            "public_key": True,
            "address": True
        }
    )
    click.echo(json.dumps(rslt, indent=4, ensure_ascii=False))
    """
    args = add_argument_parser()
    args.func(args)
