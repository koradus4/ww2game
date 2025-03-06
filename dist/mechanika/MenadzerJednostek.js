"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MenadzerJednostek = void 0;
class MenadzerJednostek {
    constructor(wczytywaczMapy) {
        this.jednostki = {};
        this.wczytywaczMapy = wczytywaczMapy;
    }
    dodajJednostke(jednostka) {
        this.jednostki[jednostka.id] = jednostka;
        console.log(`Dodano jednostkę ${jednostka.id} na pozycji ${jednostka.pozycja}`);
    }
    pobierzJednostke(id) {
        const jednostka = this.jednostki[id];
        if (!jednostka) {
            console.warn(`Nie znaleziono jednostki o ID: ${id}`);
            return null;
        }
        return jednostka;
    }
    pobierzWszystkieJednostki() {
        return Object.values(this.jednostki);
    }
    obliczKosztRuchu(jednostka, doHeksa) {
        const heks = this.wczytywaczMapy.pobierzHeks(doHeksa);
        if (!heks) {
            console.warn(`Nie znaleziono heksa o ID: ${doHeksa}`);
            return Infinity;
        }
        const teren = heks.terrain;
        let koszt = teren.move_mod;
        if (!teren.passable)
            return Infinity;
        if (teren.blocks_heavy && jednostka.token.unit_type === 'czolg')
            return Infinity;
        return Math.max(1, koszt);
    }
    moznaWykonacRuch(jednostka, doHeksa) {
        const koszt = this.obliczKosztRuchu(jednostka, doHeksa);
        const mozliwy = koszt <= jednostka.pozostalePunktyRuchu;
        if (!mozliwy) {
            console.log(`Ruch niemożliwy - koszt: ${koszt}, dostępne punkty: ${jednostka.pozostalePunktyRuchu}`);
        }
        return mozliwy;
    }
    wykonajRuch(jednostkaId, doHeksa) {
        const jednostka = this.pobierzJednostke(jednostkaId);
        if (!jednostka)
            return false;
        if (!this.moznaWykonacRuch(jednostka, doHeksa))
            return false;
        const koszt = this.obliczKosztRuchu(jednostka, doHeksa);
        jednostka.pozycja = doHeksa;
        jednostka.pozostalePunktyRuchu -= koszt;
        console.log(`Wykonano ruch jednostki ${jednostkaId} na heks ${doHeksa}`);
        console.log(`Pozostałe punkty ruchu: ${jednostka.pozostalePunktyRuchu}`);
        return true;
    }
}
exports.MenadzerJednostek = MenadzerJednostek;
