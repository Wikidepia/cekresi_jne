# Cek Resi JNE

Digunakan untuk mengecek resi JNE tanpa menggunakan API eksternal manapun.

## Installing

1. `git clone https://github.com/Wikidepia/cekresi_jne`, untuk mendownload source code.
2. `cd cekresi_jne`, untuk masuk ke direktori.
3. `pip3 install -U -r requirements.txt`, untuk menginstall semua requirement.

## Usage

``` python
import jne
info_resi = jne.cek_resi("CGK2H03789568816")
print(info_resi)
```

Terimakasih kepada Sampriti Panda karena telah memberikan [securimage_solver](https://github.com/sampritipanda/securimage_solver).
