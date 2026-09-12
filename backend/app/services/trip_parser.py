from datetime import date
import re
from typing import Any, Dict, List, Optional, Tuple


class TripParser:
    MONTH_NAMES = {
        "january": 1,
        "jan": 1,
        "february": 2,
        "feb": 2,
        "march": 3,
        "mar": 3,
        "april": 4,
        "apr": 4,
        "may": 5,
        "june": 6,
        "jun": 6,
        "july": 7,
        "jul": 7,
        "august": 8,
        "aug": 8,
        "september": 9,
        "sept": 9,
        "sep": 9,
        "october": 10,
        "oct": 10,
        "november": 11,
        "nov": 11,
        "december": 12,
        "dec": 12,
    }

    STOP_WORDS = {
        "i",
        "want",
        "to",
        "travel",
        "trip",
        "go",
        "jana",
        "hai",
        "se",
        "from",
        "tak",
        "on",
        "in",
        "for",
        "with",
        "budget",
        "cost",
        "price",
        "and",
        "october",
        "oct",
        "november",
        "nov",
        "december",
        "dec",
        "january",
        "jan",
        "february",
        "feb",
        "march",
        "mar",
        "april",
        "apr",
        "may",
        "june",
        "jun",
        "july",
        "jul",
        "august",
        "aug",
        "september",
        "sep",
        "sept",
    }

    PREFERENCE_KEYWORDS = [
        "veg",
        "vegetarian",
        "non-veg",
        "family",
        "beach",
        "luxury",
        "budget-friendly",
        "adventure",
        "relaxing",
        "sightseeing",
        "nature",
        "culture",
        "shopping",
    ]

    def parse(
        self, text: str, ref_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Parse natural language trip request into extracted dictionary."""
        if ref_date is None:
            ref_date = date.today()

        clean_text = text.strip()

        travelers = self._extract_travelers(clean_text)
        budget = self._extract_budget(clean_text)
        dates = self._extract_dates(clean_text, ref_date)
        origin, destination = self._extract_origin_destination(clean_text)
        preferences = self._extract_preferences(clean_text)

        result: Dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "start_date": dates[0] if dates else None,
            "end_date": dates[1] if dates else None,
            "budget": budget,
            "travelers": travelers,
            "preferences": preferences,
        }
        return result

    def _extract_travelers(self, text: str) -> Optional[int]:
        # Match patterns like: 2 people, 2 log, 2 persons, 2 travelers, for 2, 2 pax
        pax_match = re.search(
            r"\b(\d+)\s*(?:people|persons|person|travelers|traveler|log|pax|members|passengers)\b",
            text,
            re.IGNORECASE,
        )
        if pax_match:
            return int(pax_match.group(1))

        for_match = re.search(
            r"\bfor\s+(\d+)\b(?!\s*(?:k|K|rs|rupees|\₹|days|nights|oct|nov|dec|jan|feb|mar|apr|may|jun|jul|aug|sep|sept))",
            text,
            re.IGNORECASE,
        )
        if for_match:
            return int(for_match.group(1))

        return None

    def _extract_budget(self, text: str) -> Optional[float]:
        # Matches: budget 30000, budget 30k, budget of ₹30,000, 30k budget, 30000 rs, ₹30000
        budget_match = re.search(
            r"\b(?:budget|cost|price|rupees|rs|\₹)\s*(?:of|is|:)?\s*(?:rs|\₹)?\s*(\d+(?:\.\d+)?\s*[kK]?|\d{1,3}(?:,\d{3})+)\b",
            text,
            re.IGNORECASE,
        )
        if budget_match:
            raw_val = budget_match.group(1).replace(",", "").strip()
            return self._convert_number(raw_val)

        # Match standalone '30k' or '30K'
        k_match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*[kK]\b", text, re.IGNORECASE
        )
        if k_match:
            return float(k_match.group(1)) * 1000.0

        return None

    def _convert_number(self, val_str: str) -> float:
        val_str = val_str.lower()
        if val_str.endswith("k"):
            return float(val_str[:-1].strip()) * 1000.0
        return float(val_str)

    def _extract_origin_destination(
        self, text: str
    ) -> Tuple[Optional[str], Optional[str]]:
        patterns = [
            r"\bfrom\s+([A-Za-z]+)\s+(?:to|se)\s+([A-Za-z]+)\b",
            r"\b([A-Za-z]+)\s+(?:to|se)\s+([A-Za-z]+)\b",
        ]

        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                orig = match.group(1).strip()
                dest = match.group(2).strip()

                if (
                    orig.lower() in self.STOP_WORDS
                    or dest.lower() in self.STOP_WORDS
                ):
                    continue

                orig_clean = self._clean_city_name(orig)
                dest_clean = self._clean_city_name(dest)

                if (
                    orig_clean
                    and dest_clean
                    and orig_clean.lower() != dest_clean.lower()
                ):
                    return orig_clean, dest_clean

        return None, None

    def _clean_city_name(self, city: str) -> str:
        city = re.sub(
            r"\b(?:mujhe|want|to|travel|trip|go|jana|hai|se|from|tak)\b",
            "",
            city,
            flags=re.IGNORECASE,
        ).strip()
        return city.title() if city else ""

    def _extract_dates(
        self, text: str, ref_date: date
    ) -> Optional[Tuple[date, date]]:
        month_pattern = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        single_date_pat = (
            r"(?:"
            + month_pattern
            + r"\s+\d{1,2}(?:st|nd|rd|th)?(?:\s*,?\s*\d{4})?|\d{1,2}(?:st|nd|rd|th)?\s+"
            + month_pattern
            + r"(?:\s*,?\s*\d{4})?|\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4})"
        )

        range_pat = (
            r"("
            + single_date_pat
            + r")\s*(?:to|->|se|till|-|and)\s*("
            + single_date_pat
            + r")"
        )

        match = re.search(range_pat, text, re.IGNORECASE)
        if match:
            d1 = self._parse_single_date(match.group(1), ref_date)
            d2 = self._parse_single_date(match.group(2), ref_date)
            if d1 and d2:
                return (d1, d2)

        return None

    def _parse_single_date(
        self, date_str: str, ref_date: date
    ) -> Optional[date]:
        date_str = date_str.strip().lower()
        date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)

        numeric_match = re.match(
            r"^(\d{1,4})[-/.]([0-1]?\d)[-/.](\d{1,4})$", date_str
        )
        if numeric_match:
            g1, g2, g3 = (
                int(numeric_match.group(1)),
                int(numeric_match.group(2)),
                int(numeric_match.group(3)),
            )
            if g1 > 1000:
                return date(g1, g2, g3)
            else:
                return date(g3, g2, g1)

        words = re.findall(r"\b[a-z0-9]+\b", date_str)
        day = None
        month = None
        year = None

        for w in words:
            if w in self.MONTH_NAMES:
                month = self.MONTH_NAMES[w]
            elif w.isdigit():
                num = int(w)
                if num > 1000:
                    year = num
                elif num >= 1 and num <= 31 and day is None:
                    day = num

        if day and month:
            if year is None:
                year = ref_date.year
                if (month, day) < (ref_date.month, ref_date.day):
                    year += 1
            try:
                return date(year, month, day)
            except ValueError:
                return None

        return None

    def _extract_preferences(self, text: str) -> List[str]:
        found = []
        lower_text = text.lower()
        for kw in self.PREFERENCE_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower_text):
                found.append(kw)
        return found
