import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export interface FiltersState{
  location: string;
  beds: number;
  baths: number;
  propertyType: string;
  amenities: string[];
  availableFrom: string;
  priceRange: [number, number] | [null, null];
  squareFeet: [number, number] | [null, null];
  coordinates: [number, number] | [null, null];
  favoriteIds?: number[];
}

interface IntialStateTypes{
  filters: FiltersState;
  isFiltersFullOpen: boolean;
  viewMode: "grid" | "list";
}

export const initialState: IntialStateTypes = {
  filters:{
    location: "Los Angeles",
    beds: 0,
    baths: 0,
    propertyType: "any",
    amenities: [] as string[],
    availableFrom: "any",
    priceRange: [null, null],
    squareFeet: [null, null],
    coordinates: [-118.25, 34.05],
    favoriteIds: [],
  },
  isFiltersFullOpen: false,
  viewMode: "grid",
};

export const globalSlice = createSlice({
  name: "global",
  initialState,
  reducers: {
    setFilters: (state: any, action: PayloadAction<Partial<FiltersState>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    toggleFiltersFullOpen: (state: any) => {
      state.isFiltersFullOpen = !state.isFiltersFullOpen;
    },
    setViewMode: (state: any, action: PayloadAction<"grid" | "list">) => {
      state.viewMode = action.payload;
    }, 
  },
});

export const {setFilters, toggleFiltersFullOpen, setViewMode} = globalSlice.actions;

export default globalSlice.reducer;
