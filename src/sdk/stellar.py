import sys
import hashlib
from stellar_sdk import Keypair

def generate_address(mnemonic: str, semantic: str, network: str):
    key_pair = Keypair.from_mnemonic_phrase(mnemonic)
    private_key = key_pair.secret
    public_key = key_pair.public_key
    address = public_key
    hash_str = ''

    return {
        "private_key": private_key,
        "public_key": public_key,
        "address": address,
        "hash": hash_str,
    }


if __name__ == "__main__":
    #list_cryptocurrencies()
    rslt = generate_address(
        "reveal trial cup eight seek able number smooth cargo latin zebra vessel liquid exile total seat hamster online material vicious among stable drip route",
        "p2pkh"
    )
    import json
    from hdwallet.cli import ( click )
    click.echo(json.dumps(rslt, indent=4, ensure_ascii=False))
