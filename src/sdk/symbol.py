import sys
import hashlib
import binascii
from symbolchain.CryptoTypes import PrivateKey
from symbolchain.symbol.KeyPair import KeyPair
from symbolchain.facade.SymbolFacade import SymbolFacade
from symbolchain.Bip32 import Bip32

def generate_address(mnemonic: str, semantic: str, network: str):
    facade = SymbolFacade(network)

    """
    # use entroy directly
    private_key = PrivateKey(entropy)
    key_pair = SymbolFacade.KeyPair(private_key)
    """

    # use derive path
    bip_id, change, index = 44, 0, 0
    path = [bip_id, facade.BIP32_COIN_ID, 0, change, index]

    bip = Bip32(facade.BIP32_CURVE_NAME)
    root_node = bip.from_mnemonic(mnemonic, "")
    child_node = root_node.derive_path(path)
    key_pair = facade.bip32_node_to_key_pair(child_node)
    
    private_key = key_pair.private_key
    public_key = key_pair.public_key
    address = facade.network.public_key_to_address(public_key)
    hash_str = hashlib.new("ripemd160", hashlib.sha256(binascii.unhexlify(str(public_key))).digest()).hexdigest()

    return {
        "private_key": private_key.bytes.hex(),
        "public_key": public_key.bytes.hex(),
        "address": str(address),
        "hash": hash_str,
    }


if __name__ == "__main__":
    #list_cryptocurrencies()
    rslt = generate_address(
        "XYM",
        "reveal trial cup eight seek able number smooth cargo latin zebra vessel liquid exile total seat hamster online material vicious among stable drip route",
        "p2pkh"
    )
    import json
    from hdwallet.cli import ( click )
    click.echo(json.dumps(rslt, indent=4, ensure_ascii=False))
