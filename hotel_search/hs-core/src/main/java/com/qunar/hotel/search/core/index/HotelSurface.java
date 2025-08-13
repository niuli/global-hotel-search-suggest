package com.qunar.hotel.search.core.index;

/**
 * @author hotel-search
 * @version 1.0
 *
 * @description The hotel surface is for adapter suggest kernel and API.
 */
class HotelSurface {
    final String query;
    final String surface;

    public HotelSurface(String query, String surface) {
        this.query = query;
        this.surface = surface;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof HotelSurface)) {
            return false;
        }

        HotelSurface surface1 = (HotelSurface) o;
        return !(surface != null ? !surface.equals(surface1.surface) : surface1.surface != null);
    }

    @Override
    public int hashCode() {
        return surface != null ? surface.hashCode() : 0;
    }
} 