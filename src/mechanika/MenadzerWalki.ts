import { JednostkaNaMapie, WynikWalki, ModyfikatoryWalki } from '../mapa/typy';
import { WczytywaczMapy } from '../mapa/WczytywaczMapy';

export class MenadzerWalki {
    private wczytywaczMapy: WczytywaczMapy;

    constructor(wczytywaczMapy: WczytywaczMapy) {
        this.wczytywaczMapy = wczytywaczMapy;
    }

    obliczModyfikatory(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie): ModyfikatoryWalki {
        const heksObroncy = this.wczytywaczMapy.pobierzHeks(obronca.pozycja);
        
        // Obliczanie modyfikatorów pogodowych
        const pogodaModyfikator = this.obliczModyfikatorPogody(heksObroncy?.terrain);
        const poraDobyModyfikator = this.obliczModyfikatorPoryDoby();
        
        return {
            terenObroncy: heksObroncy?.terrain.defense_mod || 0,
            przewagaLiczebna: this.obliczPrzewageLiczebna(atakujacy, obronca),
            wsparcie: 0, // TODO: Implementacja wsparcia
            zaopatrzenie: this.obliczModyfikatorZaopatrzenia(atakujacy, obronca),
            pogoda: pogodaModyfikator,
            poraDoby: poraDobyModyfikator,
            morale: this.obliczModyfikatorMorale(atakujacy, obronca),
            doswiadczenie: this.obliczModyfikatorDoswiadczenia(atakujacy, obronca)
        };
    }

    private obliczPrzewageLiczebna(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie): number {
        const wartosciWielkosci = {
            'druzyna': 1,
            'pluton': 3,
            'kompania': 9,
            'batalion': 27,
            'pulk': 81,
            'dywizja': 243
        };

        const silaAtakujacego = wartosciWielkosci[atakujacy.wielkoscJednostki];
        const silaObroncy = wartosciWielkosci[obronca.wielkoscJednostki];

        return Math.log2(silaAtakujacego / silaObroncy);
    }

    private obliczModyfikatorPogody(teren?: { pogodaEffekt?: { [key: string]: number } }): number {
        if (!teren?.pogodaEffekt) return 0;
        // TODO: Implementacja wpływu pogody
        return 0;
    }

    private obliczModyfikatorPoryDoby(): number {
        // TODO: Implementacja wpływu pory doby
        return 0;
    }

    private obliczModyfikatorZaopatrzenia(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie): number {
        const modAtakujacy = (atakujacy.stats.amunicja + atakujacy.stats.zaopatrzenie) / 200;
        const modObronca = (obronca.stats.amunicja + obronca.stats.zaopatrzenie) / 200;
        return modAtakujacy - modObronca;
    }

    private obliczModyfikatorMorale(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie): number {
        return (atakujacy.stats.morale - obronca.stats.morale) / 100;
    }

    private obliczModyfikatorDoswiadczenia(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie): number {
        return (atakujacy.stats.doswiadczenie - obronca.stats.doswiadczenie) / 100;
    }

    rozstrzygnijWalke(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie): WynikWalki {
        console.log(`\nRozpoczęcie walki: ${atakujacy.id} vs ${obronca.id}`);

        const modyfikatory = this.obliczModyfikatory(atakujacy, obronca);
        
        const silaAtaku = atakujacy.token.attack_value;
        const silaObrony = obronca.token.combat_value;

        const efektywnaSilaAtaku = silaAtaku + 
            modyfikatory.przewagaLiczebna + 
            modyfikatory.wsparcie + 
            modyfikatory.zaopatrzenie +
            modyfikatory.morale +
            modyfikatory.doswiadczenie;

        const efektywnaSilaObrony = silaObrony + 
            modyfikatory.terenObroncy -
            modyfikatory.pogoda -
            modyfikatory.poraDoby;

        console.log("Modyfikatory walki:", modyfikatory);
        console.log(`Siła ataku: ${silaAtaku} (efektywna: ${efektywnaSilaAtaku})`);
        console.log(`Siła obrony: ${silaObrony} (efektywna: ${efektywnaSilaObrony})`);

        const stratyObroncy = Math.max(0, Math.floor((efektywnaSilaAtaku - efektywnaSilaObrony) / 2));
        const stratyAtakujacego = Math.max(0, Math.floor((efektywnaSilaObrony - efektywnaSilaAtaku) / 3));

        const wynik: WynikWalki = {
            atakujacy: {
                id: atakujacy.id,
                straty: stratyAtakujacego,
                wycofany: stratyAtakujacego > 2,
                zmianaMorale: stratyAtakujacego > 0 ? -10 : 5,
                zmianaDoswiadczenia: 10
            },
            obronca: {
                id: obronca.id,
                straty: stratyObroncy,
                wycofany: stratyObroncy > 2,
                zmianaMorale: stratyObroncy > 0 ? -15 : 0,
                zmianaDoswiadczenia: 5
            },
            modyfikatory: {
                teren: modyfikatory.terenObroncy,
                wsparcie: modyfikatory.wsparcie,
                zaopatrzenie: modyfikatory.zaopatrzenie,
                pogoda: modyfikatory.pogoda,
                poraDoby: modyfikatory.poraDoby,
                morale: modyfikatory.morale,
                doswiadczenie: modyfikatory.doswiadczenie
            },
            przejecieKontroli: stratyObroncy > 0 && stratyAtakujacego === 0,
            zdobyteZaopatrzenie: stratyObroncy > 0 ? Math.floor(Math.random() * 20) : 0
        };

        this.aktualizujStanJednostek(atakujacy, obronca, wynik);
        this.wyswietlWynikWalki(atakujacy, obronca, wynik);

        return wynik;
    }

    private aktualizujStanJednostek(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie, wynik: WynikWalki): void {
        // Aktualizacja atakującego
        atakujacy.straty = (atakujacy.straty || 0) + wynik.atakujacy.straty;
        atakujacy.wycofana = wynik.atakujacy.wycofany;
        atakujacy.stats.morale = Math.max(0, Math.min(100, atakujacy.stats.morale + wynik.atakujacy.zmianaMorale));
        atakujacy.stats.doswiadczenie = Math.min(100, atakujacy.stats.doswiadczenie + wynik.atakujacy.zmianaDoswiadczenia);
        atakujacy.stats.amunicja = Math.max(0, atakujacy.stats.amunicja - 10);
        atakujacy.stats.zmeczenie = Math.min(100, atakujacy.stats.zmeczenie + 15);
        
        // Aktualizacja obrońcy
        obronca.straty = (obronca.straty || 0) + wynik.obronca.straty;
        obronca.wycofana = wynik.obronca.wycofany;
        obronca.stats.morale = Math.max(0, Math.min(100, obronca.stats.morale + wynik.obronca.zmianaMorale));
        obronca.stats.doswiadczenie = Math.min(100, obronca.stats.doswiadczenie + wynik.obronca.zmianaDoswiadczenia);
        obronca.stats.amunicja = Math.max(0, obronca.stats.amunicja - 5);
        obronca.stats.zmeczenie = Math.min(100, obronca.stats.zmeczenie + 10);
    }

    private wyswietlWynikWalki(atakujacy: JednostkaNaMapie, obronca: JednostkaNaMapie, wynik: WynikWalki): void {
        console.log("\nWynik walki:", {
            atakujacy: {
                id: atakujacy.id,
                straty: wynik.atakujacy.straty,
                wycofany: wynik.atakujacy.wycofany,
                morale: atakujacy.stats.morale,
                doswiadczenie: atakujacy.stats.doswiadczenie,
                amunicja: atakujacy.stats.amunicja,
                zmeczenie: atakujacy.stats.zmeczenie
            },
            obronca: {
                id: obronca.id,
                straty: wynik.obronca.straty,
                wycofany: wynik.obronca.wycofany,
                morale: obronca.stats.morale,
                doswiadczenie: obronca.stats.doswiadczenie,
                amunicja: obronca.stats.amunicja,
                zmeczenie: obronca.stats.zmeczenie
            },
            modyfikatory: wynik.modyfikatory,
            przejecieKontroli: wynik.przejecieKontroli,
            zdobyteZaopatrzenie: wynik.zdobyteZaopatrzenie
        });
    }
}