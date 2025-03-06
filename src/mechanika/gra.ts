import { TokenData, JednostkaNaMapie, StanGry, StronaKonfliktu, RodzajJednostki, WielkoscJednostki } from '../mapa/typy';
import { WczytywaczMapy } from '../mapa/WczytywaczMapy';
import { MenadzerJednostek } from './MenadzerJednostek';
import { MenadzerWalki } from './MenadzerWalki';
import * as fs from 'fs';

export class Gra {
    private sciezkaTokenow: string;
    private tokeny: TokenData | null;
    private wczytywaczMapy: WczytywaczMapy;
    private menadzerJednostek: MenadzerJednostek;
    private menadzerWalki: MenadzerWalki;
    private stanGry: StanGry;

    constructor() {
        this.sciezkaTokenow = "C:/Users/klif/ww2-game/src/tokeny/token_data.json";
        this.tokeny = null;
        this.wczytywaczMapy = new WczytywaczMapy();
        this.menadzerJednostek = new MenadzerJednostek(this.wczytywaczMapy);
        this.menadzerWalki = new MenadzerWalki(this.wczytywaczMapy);
        this.stanGry = {
            aktualnyGracz: "Polska",
            numerTury: 1,
            fazaGry: 'przygotowanie',
            gracze: {
                "Polska": {
                    strona: "Polska",
                    dostepneTokeny: [],
                    punktyZwyciestwa: 0,
                    sojusznicy: ["UK", "USA"],
                    zasoby: {
                        amunicja: 100,
                        paliwo: 100,
                        zaopatrzenie: 100
                    }
                },
                "Niemcy": {
                    strona: "Niemcy",
                    dostepneTokeny: [],
                    punktyZwyciestwa: 0,
                    sojusznicy: ["ZSRR"],
                    zasoby: {
                        amunicja: 100,
                        paliwo: 100,
                        zaopatrzenie: 100
                    }
                },
                "ZSRR": {
                    strona: "ZSRR",
                    dostepneTokeny: [],
                    punktyZwyciestwa: 0,
                    sojusznicy: ["Niemcy"],
                    zasoby: {
                        amunicja: 100,
                        paliwo: 100,
                        zaopatrzenie: 100
                    }
                },
                "UK": {
                    strona: "UK",
                    dostepneTokeny: [],
                    punktyZwyciestwa: 0,
                    sojusznicy: ["Polska", "USA"],
                    zasoby: {
                        amunicja: 100,
                        paliwo: 100,
                        zaopatrzenie: 100
                    }
                },
                "USA": {
                    strona: "USA",
                    dostepneTokeny: [],
                    punktyZwyciestwa: 0,
                    sojusznicy: ["Polska", "UK"],
                    zasoby: {
                        amunicja: 100,
                        paliwo: 100,
                        zaopatrzenie: 100
                    }
                }
            },
            pogoda: 'slonecznie',
            poraDoby: 'dzien'
        };
    }

    public async start(): Promise<void> {
        console.log("=== ROZPOCZĘCIE GRY ===");
        console.log(`Tura ${this.stanGry.numerTury}, Gracz: ${this.stanGry.aktualnyGracz}`);
        
        try {
            await this.inicjalizujGre();
            await this.testujPelnaMechanike();
        } catch (error) {
            console.error("Błąd podczas inicjalizacji gry:", error);
            throw error;
        }
    }

    private async inicjalizujGre(): Promise<void> {
        console.log("\n--- Inicjalizacja komponentów ---");
        await this.wczytajTokeny();
        await this.wczytajMape();
        await this.przygotujJednostki();
        this.stanGry.fazaGry = 'ruch';
        console.log("Gra została zainicjalizowana pomyślnie");
    }

    private async testujPelnaMechanike(): Promise<void> {
        console.log("\n=== TESTY MECHANIKI GRY ===");
        
        // Test 1: Ruch jednostek
        console.log("\n--- Test ruchu jednostek ---");
        await this.testujRuchJednostek();

        // Test 2: System walki
        console.log("\n--- Test systemu walki ---");
        await this.testujSystemWalki();

        // Test 3: Zmiana faz i graczy
        console.log("\n--- Test zmiany faz i graczy ---");
        await this.testujZmianyFaz();
    }

    private async testujRuchJednostek(): Promise<void> {
        console.log("Stan początkowy:", this.pobierzStanGry());
        
        const wynikRuchuPolski = this.wykonajRuchJednostki("POLSKA_1", "11_5");
        console.log(`Ruch jednostki polskiej: ${wynikRuchuPolski ? "sukces" : "niepowodzenie"}`);

        const wynikRuchuNiemiecki = this.wykonajRuchJednostki("NIEMCY_1", "11_6");
        console.log(`Ruch jednostki niemieckiej: ${wynikRuchuNiemiecki ? "sukces" : "niepowodzenie"}`);
    }

    private async testujSystemWalki(): Promise<void> {
        while (this.stanGry.fazaGry !== 'walka') {
            this.zmienFazeGry();
        }

        console.log("Stan przed walką:", this.pobierzStanGry());

        console.log("\nTest 1: Walka dozwolona (Polska vs Niemcy)");
        const wynikWalki1 = this.wykonajWalke("POLSKA_1", "NIEMCY_1");
        console.log(`Rezultat: ${wynikWalki1 ? "wykonano" : "odrzucono"}`);

        console.log("\nTest 2: Walka niedozwolona (Niemcy vs Polska)");
        const wynikWalki2 = this.wykonajWalke("NIEMCY_1", "POLSKA_1");
        console.log(`Rezultat: ${wynikWalki2 ? "wykonano" : "odrzucono"}`);
    }

    private async testujZmianyFaz(): Promise<void> {
        console.log("\nPrzejście przez wszystkie fazy:");
        for (let i = 0; i < 4; i++) {
            console.log(this.pobierzStanGry());
            this.zmienFazeGry();
        }
    }

    private async wczytajTokeny(): Promise<void> {
        try {
            console.log("Próba wczytania tokenów z:", this.sciezkaTokenow);
            const dane = fs.readFileSync(this.sciezkaTokenow, 'utf8');
            this.tokeny = JSON.parse(dane);
            
            const liczbaTokenow = Object.keys(this.tokeny || {}).length;
            console.log(`Pomyślnie wczytano ${liczbaTokenow} tokenów`);
            
            if (this.tokeny && Object.keys(this.tokeny).length > 0) {
                const przykladowyToken = Object.values(this.tokeny)[0];
                console.log("Przykładowy token:", przykladowyToken);
            }
        } catch (error) {
            console.error("Błąd wczytywania tokenów:", error);
            throw new Error("Nie udało się wczytać tokenów");
        }
    }

    private async wczytajMape(): Promise<void> {
        try {
            await this.wczytywaczMapy.wczytajMape();
            
            if (this.wczytywaczMapy.czyMapaJestWczytana()) {
                const metadane = this.wczytywaczMapy.pobierzMetadane();
                console.log("Mapa została wczytana:", {
                    nazwa: metadane?.map_name,
                    wymiary: metadane?.map_dimensions
                });
            }
        } catch (error) {
            console.error("Błąd wczytywania mapy:", error);
            throw error;
        }
    }

    private async przygotujJednostki(): Promise<void> {
        // Jednostka polska
        const pozycjaPolska = "10_5";
        const jednostkaPolska: JednostkaNaMapie = {
            id: "POLSKA_1",
            pozycja: pozycjaPolska,
            pozostalePunktyRuchu: 4,
            token: {
                nation: "Polska",
                unit_type: "piechota",
                unit_size: "batalion",
                movement_points: 4,
                attack_range: 1,
                attack_value: 3,
                combat_value: 4,
                supply_points: 3
            },
            stats: {
                morale: 80,
                doswiadczenie: 50,
                zmeczenie: 0,
                amunicja: 100,
                paliwo: 100,
                zaopatrzenie: 100
            },
            rodzajJednostki: 'piechota',
            wielkoscJednostki: 'batalion'
        };

        // Jednostka niemiecka
        const pozycjaNiemiecka = "10_6";
        const jednostkaNiemiecka: JednostkaNaMapie = {
            id: "NIEMCY_1",
            pozycja: pozycjaNiemiecka,
            pozostalePunktyRuchu: 4,
            token: {
                nation: "Niemcy",
                unit_type: "piechota",
                unit_size: "batalion",
                movement_points: 4,
                attack_range: 1,
                attack_value: 4,
                combat_value: 3,
                supply_points: 3
            },
            stats: {
                morale: 90,
                doswiadczenie: 70,
                zmeczenie: 0,
                amunicja: 100,
                paliwo: 100,
                zaopatrzenie: 100
            },
            rodzajJednostki: 'piechota',
            wielkoscJednostki: 'batalion'
        };

        this.menadzerJednostek.dodajJednostke(jednostkaPolska);
        this.menadzerJednostek.dodajJednostke(jednostkaNiemiecka);
        console.log("Przygotowano jednostki testowe");
    }

    wykonajRuchJednostki(jednostkaId: string, doHeksa: string): boolean {
        if (this.stanGry.fazaGry !== 'ruch') {
            console.warn("Ruch możliwy tylko w fazie ruchu!");
            return false;
        }

        const jednostka = this.menadzerJednostek.pobierzJednostke(jednostkaId);
        if (!jednostka) {
            console.warn("Nie znaleziono jednostki!");
            return false;
        }

        if (jednostka.token.nation !== this.stanGry.aktualnyGracz) {
            console.warn("Ta jednostka należy do przeciwnika!");
            return false;
        }

        return this.menadzerJednostek.wykonajRuch(jednostkaId, doHeksa);
    }

    wykonajWalke(atakujacyId: string, obroncaId: string): boolean {
        if (this.stanGry.fazaGry !== 'walka') {
            console.warn("Walka możliwa tylko w fazie walki!");
            return false;
        }

        const atakujacy = this.menadzerJednostek.pobierzJednostke(atakujacyId);
        const obronca = this.menadzerJednostek.pobierzJednostke(obroncaId);

        if (!atakujacy || !obronca) {
            console.warn("Nie znaleziono jednej z jednostek!");
            return false;
        }

        if (atakujacy.token.nation !== this.stanGry.aktualnyGracz) {
            console.warn("Ta jednostka należy do przeciwnika!");
            return false;
        }

        const wynik = this.menadzerWalki.rozstrzygnijWalke(atakujacy, obronca);
        return true;
    }

    zmienGracza(): void {
        this.stanGry.aktualnyGracz = this.stanGry.aktualnyGracz === "Polska" ? "Niemcy" : "Polska";
        console.log(`Zmieniono gracza na: ${this.stanGry.aktualnyGracz}`);
    }

    zmienFazeGry(): void {
        const fazy: ('przygotowanie' | 'ruch' | 'walka' | 'zaopatrzenie')[] = 
            ['przygotowanie', 'ruch', 'walka', 'zaopatrzenie'];
        
        const obecnyIndex = fazy.indexOf(this.stanGry.fazaGry);
        const nastepnyIndex = (obecnyIndex + 1) % fazy.length;
        
        this.stanGry.fazaGry = fazy[nastepnyIndex];
        
        if (this.stanGry.fazaGry === 'przygotowanie') {
            this.stanGry.numerTury++;
            this.resetujPunktyRuchu();
        } else if (this.stanGry.fazaGry === 'ruch') {
            this.zmienGracza();
        }
        
        console.log(`Zmieniono fazę na: ${this.stanGry.fazaGry}`);
        if (this.stanGry.fazaGry === 'przygotowanie') {
            console.log(`Nowa tura: ${this.stanGry.numerTury}`);
        }
    }

    private resetujPunktyRuchu(): void {
        const jednostki = this.menadzerJednostek.pobierzWszystkieJednostki();
        for (const jednostka of jednostki) {
            jednostka.pozostalePunktyRuchu = jednostka.token.movement_points;
        }
        console.log("Zresetowano punkty ruchu wszystkich jednostek");
    }

    pobierzStanGry(): string {
        return `Tura ${this.stanGry.numerTury}, Faza: ${this.stanGry.fazaGry}, Gracz: ${this.stanGry.aktualnyGracz}`;
    }
}