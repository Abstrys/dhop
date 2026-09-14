#!/bin/bash
DIST_DIR="dist/abstrys-dhop-linux"
VERSION="2.0.2"
cargo clean && cargo build --release
rm -rf $DIST_DIR
echo "Making package directory"
mkdir -p $DIST_DIR/bin
echo "Copying files..."
cp install_files/install.sh $DIST_DIR
cp install_files/uninstall.sh $DIST_DIR
cp README.rst $DIST_DIR/README.txt
cp LICENSE.txt $DIST_DIR
cp target/release/abstrys-dhop $DIST_DIR/bin
cp install_files/dhop.sh $DIST_DIR/bin
echo "Packaging"
cd dist
echo "Creating abstrys-dhop-linux-$VERSION.tar.gz"
tar -czvf abstrys-dhop-linux-$VERSION.tar.gz abstrys-dhop-linux
echo "Creating abstrys-dhop-linux-$VERSION.tar.bz2"
tar -cjvf abstrys-dhop-linux-$VERSION.tar.bz2 abstrys-dhop-linux
echo "Creating abstrys-dhop-linux-$VERSION.zip"
zip -r abstrys-dhop-linux-$VERSION.zip abstrys-dhop-linux
