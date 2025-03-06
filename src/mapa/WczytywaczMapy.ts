import { DaneMapy, DaneHeksa, MetadaneMapa } from './typy';
import * as fs from 'fs';
import * as path from 'path';

export class WczytywaczMapy {
    private sciezkaMapy: string;
    private daneMapy: DaneMapy | null;

    constructor() {
        // Bezpośrednia ścieżka do pliku mapy w projekcie
        this.sciezkaMapy = "C:/Users/klif/ww2-game/src/mapa/mapa.json";
        this.daneMapy = null;
    }

    async wczytajMape(): Promise<void> {
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

        } catch (error) {
            console.error("Błąd wczytywania mapy:", error);
            throw new Error(`Nie udało się wczytać mapy: ${error instanceof Error ? error.message : 'Nieznany błąd'}`);
        }
    }

    pobierzDaneMapy(): DaneMapy | null {
        if (!this.daneMapy) {
            console.warn("Próba pobrania danych mapy przed jej wczytaniem");
            return null;
        }
        return this.daneMapy;
    }

    pobierzHeks(id: string): DaneHeksa | null {
        const heks = this.daneMapy?.hex_data[id];
        if (!heks) {
            console.warn(`Nie znaleziono heksa o ID: ${id}`);
            return null;
        }
        return heks;
    }

    pobierzMetadane(): MetadaneMapa | null {
        const metadata = this.daneMapy?.map_metadata;
        if (!metadata) {
            console.warn("Próba pobrania metadanych przed wczytaniem mapy");
            return null;
        }
        return metadata;
    }

    pobierzSciezkeObrazuMapy(): string | null {
        const metadata = this.pobierzMetadane();
        if (!metadata?.map_path) {
            console.warn("Brak ścieżki do obrazu mapy w metadanych");
            return null;
        }
        return metadata.map_path;
    }

    czyMapaJestWczytana(): boolean {
        return this.daneMapy !== null;
    }
}