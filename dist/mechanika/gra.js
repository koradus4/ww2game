"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.Gra = void 0;
const WczytywaczMapy_1 = require("../mapa/WczytywaczMapy");
const MenadzerJednostek_1 = require("./MenadzerJednostek");
const MenadzerWalki_1 = require("./MenadzerWalki");
const fs = __importStar(require("fs"));
class Gra {
    constructor() {
        this.sciezkaTokenow = "C:/Users/klif/ww2-game/src/tokeny/token_data.json";
        this.tokeny = null;
        this.wczytywaczMapy = new WczytywaczMapy_1.WczytywaczMapy();
        this.menadzerJednostek = new MenadzerJednostek_1.MenadzerJednostek(this.wczytywaczMapy);
        this.menadzerWalki = new MenadzerWalki_1.MenadzerWalki(this.wczytywaczMapy);
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
    async start() {
        console.log("=== ROZPOCZĘCIE GRY ===");
        console.log(`Tura ${this.stanGry.numerTury}, Gracz: ${this.stanGry.aktualnyGracz}`);
        try {
            await this.inicjalizujGre();
            await this.testujPelnaMechanike();
        }
        catch (error) {
            console.error("Błąd podczas inicjalizacji gry:", error);
            throw error;
        }
    }
    async inicjalizujGre() {
        console.log("\n--- Inicjalizacja komponentów ---");
        await this.wczytajTokeny();
        await this.wczytajMape();
        await this.przygotujJednostki();
        this.stanGry.fazaGry = 'ruch';
        console.log("Gra została zainicjalizowana pomyślnie");
    }
    async testujPelnaMechanike() {
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
    async testujRuchJednostek() {
        console.log("Stan początkowy:", this.pobierzStanGry());
        const wynikRuchuPolski = this.wykonajRuchJednostki("POLSKA_1", "11_5");
        console.log(`Ruch jednostki polskiej: ${wynikRuchuPolski ? "sukces" : "niepowodzenie"}`);
        const wynikRuchuNiemiecki = this.wykonajRuchJednostki("NIEMCY_1", "11_6");
        console.log(`Ruch jednostki niemieckiej: ${wynikRuchuNiemiecki ? "sukces" : "niepowodzenie"}`);
    }
    async testujSystemWalki() {
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
    async testujZmianyFaz() {
        console.log("\nPrzejście przez wszystkie fazy:");
        for (let i = 0; i < 4; i++) {
            console.log(this.pobierzStanGry());
            this.zmienFazeGry();
        }
    }
    async wczytajTokeny() {
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
        }
        catch (error) {
            console.error("Błąd wczytywania tokenów:", error);
            throw new Error("Nie udało się wczytać tokenów");
        }
    }
    async wczytajMape() {
        try {
            await this.wczytywaczMapy.wczytajMape();
            if (this.wczytywaczMapy.czyMapaJestWczytana()) {
                const metadane = this.wczytywaczMapy.pobierzMetadane();
                console.log("Mapa została wczytana:", {
                    nazwa: metadane?.map_name,
                    wymiary: metadane?.map_dimensions
                });
            }
        }
        catch (error) {
            console.error("Błąd wczytywania mapy:", error);
            throw error;
        }
    }
    async przygotujJednostki() {
        // Jednostka polska
        const pozycjaPolska = "10_5";
        const jednostkaPolska = {
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
        const jednostkaNiemiecka = {
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
    wykonajRuchJednostki(jednostkaId, doHeksa) {
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
    wykonajWalke(atakujacyId, obroncaId) {
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
    zmienGracza() {
        this.stanGry.aktualnyGracz = this.stanGry.aktualnyGracz === "Polska" ? "Niemcy" : "Polska";
        console.log(`Zmieniono gracza na: ${this.stanGry.aktualnyGracz}`);
    }
    zmienFazeGry() {
        const fazy = ['przygotowanie', 'ruch', 'walka', 'zaopatrzenie'];
        const obecnyIndex = fazy.indexOf(this.stanGry.fazaGry);
        const nastepnyIndex = (obecnyIndex + 1) % fazy.length;
        this.stanGry.fazaGry = fazy[nastepnyIndex];
        if (this.stanGry.fazaGry === 'przygotowanie') {
            this.stanGry.numerTury++;
            this.resetujPunktyRuchu();
        }
        else if (this.stanGry.fazaGry === 'ruch') {
            this.zmienGracza();
        }
        console.log(`Zmieniono fazę na: ${this.stanGry.fazaGry}`);
        if (this.stanGry.fazaGry === 'przygotowanie') {
            console.log(`Nowa tura: ${this.stanGry.numerTury}`);
        }
    }
    resetujPunktyRuchu() {
        const jednostki = this.menadzerJednostek.pobierzWszystkieJednostki();
        for (const jednostka of jednostki) {
            jednostka.pozostalePunktyRuchu = jednostka.token.movement_points;
        }
        console.log("Zresetowano punkty ruchu wszystkich jednostek");
    }
    pobierzStanGry() {
        return `Tura ${this.stanGry.numerTury}, Faza: ${this.stanGry.fazaGry}, Gracz: ${this.stanGry.aktualnyGracz}`;
    }
}
exports.Gra = Gra;
