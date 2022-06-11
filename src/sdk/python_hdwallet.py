#!/usr/bin/env python
import sys
import inspect
from typing import Optional
from hdwallet import ( HDWallet, cryptocurrencies )
from hdwallet.derivations import ( BIP32Derivation )


def get_cryptocurrencies():
    documents = []
    for name, cryptocurrency in inspect.getmembers(cryptocurrencies):
        if not inspect.isclass(cryptocurrency):
            continue
        if not issubclass(cryptocurrency, cryptocurrencies.Cryptocurrency):
            continue
        if cryptocurrency == cryptocurrencies.Cryptocurrency:
            continue
        if cryptocurrency.NETWORK not in ["mainnet", "testnet"]:
            continue

        if cryptocurrency.NETWORK == "mainnet":
            document: dict = {
                "name": cryptocurrency.NAME,
                "symbol": cryptocurrency.SYMBOL,
                "source_code": cryptocurrency.SOURCE_CODE,
                "mainnet": "Yes" if cryptocurrency.NETWORK == "mainnet" else "No",
                "testnet": "Yes" if cryptocurrency.NETWORK == "testnet" else "No",
                "segwit": "Yes" if cryptocurrency.SEGWIT_ADDRESS.HRP else "No",
                "coin_type": cryptocurrency.COIN_TYPE.INDEX,
                "default_path": cryptocurrency.DEFAULT_PATH,
                "sdk": "hdwallet"
            }
            documents.append(document)
        elif cryptocurrency.NETWORK == "testnet":
            for index, document in enumerate(documents):
                if document["name"] == cryptocurrency.NAME:
                    documents[index]["symbol"] = f"{document['symbol']}, {cryptocurrency.SYMBOL}"
                    documents[index]["testnet"] = "Yes"

    return documents


def generate_address(symbol: str, entropy: Optional[str], semantic: str):
    try:
        hdwallet: HDWallet = HDWallet(
            symbol=symbol, semantic=semantic
        )
        hdwallet.from_entropy(
            entropy=entropy, language="english", passphrase=None
        )

        account, address, change = 0, 0, False
        cryptocurrency: cryptocurrencies.Cryptocurrency = cryptocurrencies.get_cryptocurrency(symbol=symbol)
        bip32_derivation: BIP32Derivation = BIP32Derivation(
            purpose=(
                44, True
            ),
            coin_type=(
                cryptocurrency.COIN_TYPE.INDEX,
                cryptocurrency.COIN_TYPE.HARDENED
            ),
            account=(
                account, True
            ),
            change=change,
            address=address
        )
        hdwallet.from_path(path=bip32_derivation)

        rslt = hdwallet.dumps()
        return {
            "private_key": rslt["private_key"],
            "public_key": rslt["public_key"],
            "address": rslt["addresses"][semantic],
            "hash": rslt["hash"],
        }

    except Exception as exception:
        print(f"Error: {str(exception)}")
        sys.exit()


if __name__ == "__main__":
    rslt = generate_address(
        "BTC",
        "reveal trial cup eight seek able number smooth cargo latin zebra vessel liquid exile total seat hamster online material vicious among stable drip route",
        "p2pkh"
    )
    import json
    from hdwallet.cli import ( click )
    click.echo(json.dumps(rslt, indent=4, ensure_ascii=False))
