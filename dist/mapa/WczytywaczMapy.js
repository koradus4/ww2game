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
exports.WczytywaczMapy = void 0;
const fs = __importStar(require("fs"));
class WczytywaczMapy {
    constructor() {
        // Bezpośrednia ścieżka do pliku mapy w projekcie
        this.sciezkaMapy = "C:/Users/klif/ww2-game/src/mapa/mapa.json";
        this.daneMapy = null;
    }
    async wczytajMape() {
        try {
            console.log("Próba wczytania mapy z:", this.sciezkaMapy);
            // Sprawdzenie czy plik istnieje
            if (!fs.existsSync(this.sciezkaMapy)) {
                throw new Error(`Plik mapy nie istnieje pod ścieżką: ${this.sciezkaMapy}`);
            }
            // Wczytanie i parsowanie danych
            const dane = fs.readFileSync(this.sciezkaMapy, 'utf8');
            this.daneMapy = JSON.parse(dane);
            // Walidacja metadanych
            if (!this.daneMapy?.map_metadata) {
                throw new Error("Nieprawidłowy format pliku mapy - brak metadanych");
            }
            // Wyświetlenie informacji o mapie
            console.log("Metadane mapy:", {
                nazwa: this.daneMapy.map_metadata.map_name,
                rozmiarHeksa: this.daneMapy.map_metadata.hex_size,
                wymiary: this.daneMapy.map_metadata.map_dimensions
            });
            const liczbaHeksow = Object.keys(this.daneMapy.hex_data || {}).length;
            console.log(`Wczytano ${liczbaHeksow} heksów`);
        }
        catch (error) {
            console.error("Błąd wczytywania mapy:", error);
            throw new Error(`Nie udało się wczytać mapy: ${error instanceof Error ? error.message : 'Nieznany błąd'}`);
        }
    }
    pobierzDaneMapy() {
        if (!this.daneMapy) {
            console.warn("Próba pobrania danych mapy przed jej wczytaniem");
            return null;
        }
        return this.daneMapy;
    }
    pobierzHeks(id) {
        const heks = this.daneMapy?.hex_data[id];
        if (!heks) {
            console.warn(`Nie znaleziono heksa o ID: ${id}`);
            return null;
        }
        return heks;
    }
    pobierzMetadane() {
        const metadata = this.daneMapy?.map_metadata;
        if (!metadata) {
            console.warn("Próba pobrania metadanych przed wczytaniem mapy");
            return null;
        }
        return metadata;
    }
    pobierzSciezkeObrazuMapy() {
        const metadata = this.pobierzMetadane();
        if (!metadata?.map_path) {
            console.warn("Brak ścieżki do obrazu mapy w metadanych");
            return null;
        }
        return metadata.map_path;
    }
    czyMapaJestWczytana() {
        return this.daneMapy !== null;
    }
}
exports.WczytywaczMapy = WczytywaczMapy;
