const { Keyring } = require('@polkadot/keyring');

const ss58format = {
    'Polkadot': 0, // polkadot main network
    'Kusama': 2, // kusama testing network
    'Substrate': 42 //substrate generic. default value
};

const generate_address = (mnemonic, semantic, network) => {
    /*
    * crypto type can be ed25519, sr25519, ecdsa. the default value is ed25519
    */
    if(!ss58format.hasOwnProperty(network)){
        return false;
    }

    const keyring = new Keyring({
        type: 'ed25519',
        ss58Format: ss58format[network]
    });

    // type: ed25519, ssFormat: 42 (all defaults)
    const pair = keyring.createFromUri(mnemonic);

    return JSON.stringify({
        "private_key": "",
        "public_key": pair.publicKey.map(i => {return i.toString(16)}).join(""),
        "address": pair.address,
        "hash": "",
    })
}

// testing code
const testing = () => {
    const rslt = generate_address(
        "reveal trial cup eight seek able number smooth cargo latin zebra vessel liquid exile total seat hamster online material vicious among stable drip route",
        "",
        "Polkadot"
    )
    console.log(rslt)
}

if (require.main === module) {
    const mnemonic = process.argv[2];
    const semantic = process.argv[3];
    const network = process.argv[4];

    const rslt = generate_address(mnemonic, semantic, network)
    console.log(rslt)
}
