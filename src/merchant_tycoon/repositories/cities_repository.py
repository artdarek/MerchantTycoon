"""Repository for accessing and querying cities.

This repository provides a clean, read-only interface to the CITIES domain constant,
encapsulating all lookup logic for game cities.
"""
from typing import List, Optional

from merchant_tycoon.domain.model.city import City
from merchant_tycoon.domain.cities import CITIES


class CitiesRepository:
    """Repository for querying game cities.

    Provides methods for retrieving cities by various criteria without directly
    exposing the underlying CITIES constant to services and UI components.

    Examples:
        >>> repo = CitiesRepository()
        >>> all_cities = repo.get_all()
        >>> london = repo.get_by_index(0)
        >>> paris = repo.get_by_name("Paris")
    """

    def __init__(self, cities: Optional[List[City]] = None):
        """Initialize repository with cities catalog.

        Args:
            cities: Optional custom cities list. Defaults to CITIES constant.
        """
        self._cities = cities if cities is not None else CITIES

    def get_all(self) -> List[City]:
        """Get all available cities.

        Returns:
            Complete list of all cities in the game.
        """
        return list(self._cities)

    def get_by_index(self, index: int) -> City:
        """Get a city by its index.

        Args:
            index: Zero-based index of the city in the cities list.

        Returns:
            The City at the specified index.

        Raises:
            IndexError: If index is out of bounds.

        Examples:
            >>> repo.get_by_index(0)
            City(name="London", country="UK", ...)
        """
        return self._cities[index]

    def get_by_name(self, name: str) -> Optional[City]:
        """Find a city by exact name match.

        Args:
            name: Exact name of the city (case-sensitive).

        Returns:
            The City if found, None otherwise.

        Examples:
            >>> repo.get_by_name("Paris")
            City(name="Paris", country="France", ...)
            >>> repo.get_by_name("NonExistent")
            None
        """
        for city in self._cities:
            if city.name == name:
                return city
        return None

    def get_index_by_name(self, name: str) -> Optional[int]:
        """Find a city's index by name.

        Args:
            name: Exact name of the city (case-sensitive).

        Returns:
            The zero-based index of the city if found, None otherwise.

        Examples:
            >>> repo.get_index_by_name("Paris")
            1
        """
        for index, city in enumerate(self._cities):
            if city.name == name:
                return index
        return None

    def get_by_country(self, country: str) -> List[City]:
        """Get all cities in a specific country.

        Args:
            country: Country name (case-insensitive).

        Returns:
            List of cities in the specified country.

        Examples:
            >>> repo.get_by_country("Germany")
            [City(name="Berlin", ...), City(name="Hamburg", ...)]
        """
        country_lower = str(country).lower()
        return [
            c for c in self._cities
            if str(getattr(c, "country", "")).lower() == country_lower
        ]

    def count(self) -> int:
        """Get total number of cities.

        Returns:
            Total count of available cities.
        """
        return len(self._cities)

    def exists(self, index: int) -> bool:
        """Check if a city index is valid.

        Args:
            index: City index to validate.

        Returns:
            True if index is valid (0 <= index < count), False otherwise.

        Examples:
            >>> repo.exists(0)
            True
            >>> repo.exists(999)
            False
        """
        return 0 <= index < len(self._cities)
