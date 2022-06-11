prefix=/home/marcusyh/code/crypto_wallets
code_dir=$prefix/src
wallet_dir=$prefix/wallet
qrcode_dir=$prefix/qrcode
logs_dir=$prefix/logs

mkdir -p $wallet_dir $qrcode_dir $logs_dir
docker \
  run \
    -it \
    --publish 8888:8888 \
    --rm \
    --device=/dev/ttyACM0 \
    --device=/dev/random \
    --mount type=bind,src=$code_dir,dst=/app/code \
    --mount type=bind,src=$wallet_dir,dst=/app/wallet \
    --mount type=bind,src=$qrcode_dir,dst=/app/qrcode \
    --mount type=bind,src=$logs_dir,dst=/app/logs \
    wallet:latest \
    /bin/bash

#jsconsole --allow-root --ip 0.0.0.0 --no-browser 
