# Maintainer: Daniel Milenov <ghfetch.contact@gmail.com>
pkgname='ghfetch'
pkgver='1.0.0'
pkgrel=1
pkgdesc="A nice way to display CLI Github user / repo / organization info inspired in neofetch "
arch=('x86_64')
url="https://github.com/ghfetch/ghfetch"
license=('MIT')
depends=('python-pip3' 'python>=3.11.0', 'python-pillow>=10.0.0', 'python-aiohttp>=3.8.4', 'python-rich>=12.5.1')
makedepends=('git' 'python-pip3' 'python>=3.11.0' 'python-pillow>=10.0.0', 'python-aiohttp>=3.8.4', 'python-rich>=12.5.1')
source=('ghfetch::git://github.com/ghfetch/ghfetch.git')
md5sums=('SKIP')

build() {
	cd "$pkgname"
	make
}

package() {
  cd "$pkgname"
  install -Dm755 ./ghfetch "$pkgdir/usr/bin/ghfetch"
  install -Dm644 ./README.md "$pkgdir/usr/share/doc/$pkgname"
}