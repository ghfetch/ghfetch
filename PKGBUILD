# Maintainer: Daniel Milenov <nullgaro@gmail.com>
# Contributor: Mario Sánchez <icutum@hotmail.com>
pkgname='ghfetch'
pkgver='1.3.0'
pkgrel=1
pkgdesc="A nice way to display CLI Github user / repo / organization info inspired in neofetch"
arch=('any')
url="https://github.com/ghfetch/ghfetch"
license=('MIT')
depends=('python' 'python-setuptools' 'python-aiohttp' 'python-requests' 'python-pillow' 'python-rich')
makedepends=('git')
source=("${pkgname}-v${pkgver}.tar.gz::https://github.com/ghfetch/ghfetch/archive/refs/tags/v${pkgver}.tar.gz")
md5sums=('SKIP')

build() {
    cd "${pkgname}-${pkgver}"
    python setup.py build
}

package() {
    cd "${pkgname}-${pkgver}"
    install -d "${pkgdir}/usr/lib/${pkgname}"
    install -D -m 755 ./ghfetch/* "${pkgdir}/usr/lib/${pkgname}"
    # install -Dm755 ./ghfetch/main.py "${pkgdir}/usr/bin/${pkgname}"
    install -Dm644 ./README.md "${pkgdir}/usr/share/doc/${pkgname}"
    install -Dm644 ./LICENSE "${pkgdir}/usr/share/licenses/${pkgname}"
}
