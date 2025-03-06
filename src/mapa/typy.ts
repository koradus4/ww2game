export interface Token {
    nation: string;
    unit_type: string;
    unit_size: string;
    movement_points: number;
    attack_range: number;
    attack_value: number;
    combat_value: number;
    supply_points: number;
    selected_supports?: string[];
    selected_transport?: string;
}

export interface TokenData {
    [key: string]: Token;
}

export type StronaKonfliktu = 'Polska' | 'Niemcy' | 'ZSRR' | 'UK' | 'USA';
export type RodzajJednostki = 'piechota' | 'pancerna' | 'artyleria' | 'lotnictwo';
export type WielkoscJednostki = 'druzyna' | 'pluton' | 'kompania' | 'batalion' | 'pulk' | 'dywizja';
export type PoraDoby = 'dzien' | 'noc' | 'swit' | 'zmierzch';
export type Pogoda = 'slonecznie' | 'pochmurno' | 'deszcz' | 'burza' | 'snieg';

export interface GraczInfo {
    strona: StronaKonfliktu;
    dostepneTokeny: string[];
    punktyZwyciestwa: number;
    sojusznicy: StronaKonfliktu[];
    zasoby: {
        amunicja: number;
        paliwo: number;
        zaopatrzenie: number;
    };
}

export interface StanGry {
    aktualnyGracz: StronaKonfliktu;
    numerTury: number;
    fazaGry: 'przygotowanie' | 'ruch' | 'walka' | 'zaopatrzenie';
    gracze: Record<StronaKonfliktu, GraczInfo>;
    pogoda: Pogoda;
    poraDoby: PoraDoby;
}

export interface JednostkaStats {
    morale: number;            // 0-100
    doswiadczenie: number;     // 0-100
    zmeczenie: number;         // 0-100
    amunicja: number;          // 0-100
    paliwo: number;           // 0-100
    zaopatrzenie: number;     // 0-100
}

export interface JednostkaNaMapie {
    id: string;
    pozycja: string;
    pozostalePunktyRuchu: number;
    token: Token;
    straty?: number;
    wycofana?: boolean;
    stats: JednostkaStats;
    rodzajJednostki: RodzajJednostki;
    wielkoscJednostki: WielkoscJednostki;
    dowodca?: string;
    podwladneJednostki?: string[];
}

export interface StanJednostek {
    [id: string]: JednostkaNaMapie;
}

export interface TerenHeksa {
    move_mod: number;
    defense_mod: number;
    type: string;
    passable: boolean;
    cover: number;
    supply_cost: number;
    blocks_los?: boolean;
    blocks_heavy?: boolean;
    victory_points?: number;
    strategic_value?: boolean;
    pogodaEffekt?: {
        deszcz?: number;
        snieg?: number;
        burza?: number;
    };
}

export interface PozycjaHeksa {
    x: number;
    y: number;
}

export interface DaneHeksa {
    terrain: TerenHeksa;
    position: PozycjaHeksa;
    attributes: {
        passable: boolean;
        blocks_los: boolean;
        blocks_heavy: boolean;
        victory_points: number;
    };
    kontrola?: StronaKonfliktu;
    objetoscZaopatrzenia?: number;
}

export interface MetadaneMapa {
    hex_size: number;
    creation_date: string;
    map_name: string;
    map_dimensions: {
        width: number;
        height: number;
    };
    last_modified: string;
    map_path: string;
}

export interface DaneMapy {
    map_metadata: MetadaneMapa;
    terrain_types: { [key: string]: TerenHeksa };
    hex_data: { [key: string]: DaneHeksa };
}

export interface WynikWalki {
    atakujacy: {
        id: string;
        straty: number;
        wycofany: boolean;
        zmianaMorale: number;
        zmianaDoswiadczenia: number;
    };
    obronca: {
        id: string;
        straty: number;
        wycofany: boolean;
        zmianaMorale: number;
        zmianaDoswiadczenia: number;
    };
    modyfikatory: {
        teren: number;
        wsparcie: number;
        zaopatrzenie: number;
        pogoda: number;
        poraDoby: number;
        morale: number;
        doswiadczenie: number;
    };
    przejecieKontroli?: boolean;
    zdobyteZaopatrzenie?: number;
}

export interface ModyfikatoryWalki {
    terenObroncy: number;
    przewagaLiczebna: number;
    wsparcie: number;
    zaopatrzenie: number;
    pogoda: number;
    poraDoby: number;
    morale: number;
    doswiadczenie: number;
}