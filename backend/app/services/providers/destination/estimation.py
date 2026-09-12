from typing import Dict, List
from app.models.destination import DestinationPlace, DestinationResults
from app.models.trip import TripRequest
from app.services.providers.destination.base import BaseDestinationProvider


class EstimationDestinationProvider(BaseDestinationProvider):
    # Extensible curated dataset of demonstration places for supported destinations
    DATASET: Dict[str, List[DestinationPlace]] = {
        "goa": [
            DestinationPlace(
                name="Baga Beach & Water Sports",
                category="activity",
                description="Popular beach offering parasailing, banana rides, and vibrant beach shacks.",
                estimated_cost_min=500.0,
                estimated_cost_max=2000.0,
                recommended_duration="3-4 hours",
                best_for=["beach", "water_sports", "adventure"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Fort Aguada",
                category="culture",
                description="17th-century Portuguese fort and lighthouse overlooking the Arabian Sea.",
                estimated_cost_min=50.0,
                estimated_cost_max=100.0,
                recommended_duration="1-2 hours",
                best_for=["history", "culture", "sightseeing"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Dudhsagar Waterfalls Trek",
                category="adventure",
                description="Four-tiered waterfall located on the Mandovi River amidst lush sanctuary jungle.",
                estimated_cost_min=1500.0,
                estimated_cost_max=3000.0,
                recommended_duration="Full day",
                best_for=["adventure", "nature", "trekking"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Fontainhas Latin Quarter Walk",
                category="culture",
                description="Historic quarter with narrow winding streets, colorful Portuguese houses, and art galleries.",
                estimated_cost_min=0.0,
                estimated_cost_max=300.0,
                recommended_duration="2 hours",
                best_for=["culture", "history", "photography"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Goan Fish Curry & Seafood Feast",
                category="food",
                description="Authentic coastal Goan cuisine experience featuring fresh catch fish curry and rice.",
                estimated_cost_min=400.0,
                estimated_cost_max=1200.0,
                recommended_duration="1-2 hours",
                best_for=["food", "seafood", "dining"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Anjuna Flea Market",
                category="shopping",
                description="Bustling open-air market with handicrafts, bohemian clothing, jewelry, and souvenirs.",
                estimated_cost_min=200.0,
                estimated_cost_max=1500.0,
                recommended_duration="2-3 hours",
                best_for=["shopping", "culture"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Palolem Beach Sunset & Kayaking",
                category="nature",
                description="Crescent-shaped serene beach in South Goa famous for calm waters and kayaking.",
                estimated_cost_min=300.0,
                estimated_cost_max=800.0,
                recommended_duration="2-3 hours",
                best_for=["beach", "nature", "relaxation"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Basilica of Bom Jesus",
                category="attraction",
                description="UNESCO World Heritage Site holding the mortal remains of St. Francis Xavier.",
                estimated_cost_min=0.0,
                estimated_cost_max=50.0,
                recommended_duration="1 hour",
                best_for=["history", "culture", "attraction"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Sahakari Spice Plantation Tour",
                category="nature",
                description="Guided tour of tropical spice farms accompanied by a traditional buffet lunch.",
                estimated_cost_min=500.0,
                estimated_cost_max=900.0,
                recommended_duration="3 hours",
                best_for=["nature", "food", "family"],
                is_estimate=True,
            ),
        ],
        "mumbai": [
            DestinationPlace(
                name="Gateway of India",
                category="attraction",
                description="Iconic arch monument built in the early 20th century overlooking the Mumbai harbor.",
                estimated_cost_min=0.0,
                estimated_cost_max=100.0,
                recommended_duration="1-2 hours",
                best_for=["history", "sightseeing", "attraction"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Marine Drive Sunset Promenade",
                category="nature",
                description="C-shaped 3.6 km boulevard along the coast known as the Queen's Necklace.",
                estimated_cost_min=0.0,
                estimated_cost_max=0.0,
                recommended_duration="2 hours",
                best_for=["nature", "relaxation", "beach"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Chhatrapati Shivaji Maharaj Vastu Sangrahalaya",
                category="culture",
                description="Premier art and history museum in Mumbai documenting Indian heritage.",
                estimated_cost_min=150.0,
                estimated_cost_max=500.0,
                recommended_duration="2-3 hours",
                best_for=["history", "culture"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Mumbai Street Food Tour at Girgaon Chowpatty",
                category="food",
                description="Sample famous Vada Pav, Pav Bhaji, Bhel Puri, and Kulfi along Chowpatty beach.",
                estimated_cost_min=200.0,
                estimated_cost_max=600.0,
                recommended_duration="1-2 hours",
                best_for=["food", "beach", "family"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Colaba Causeway Shopping Trail",
                category="shopping",
                description="Famous street shopping market offering fashion accessories, antiques, and clothes.",
                estimated_cost_min=200.0,
                estimated_cost_max=1000.0,
                recommended_duration="2 hours",
                best_for=["shopping"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Elephanta Caves Boat Trip",
                category="adventure",
                description="Ferry ride across Mumbai harbor to island rock-cut cave temples dedicated to Shiva.",
                estimated_cost_min=300.0,
                estimated_cost_max=700.0,
                recommended_duration="4-5 hours",
                best_for=["history", "adventure", "culture"],
                is_estimate=True,
            ),
        ],
        "delhi": [
            DestinationPlace(
                name="Red Fort Heritage Walk",
                category="history" if False else "attraction",  # category literal check
                description="Historic 17th-century Mughal fort constructed from red sandstone.",
                estimated_cost_min=50.0,
                estimated_cost_max=500.0,
                recommended_duration="2-3 hours",
                best_for=["history", "culture", "sightseeing"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Chandni Chowk Street Food & Rickshaw Ride",
                category="food",
                description="Explore Old Delhi's historic alleys for paranthas, jalebis, and chaat.",
                estimated_cost_min=200.0,
                estimated_cost_max=700.0,
                recommended_duration="2-3 hours",
                best_for=["food", "culture", "family"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Qutub Minar Complex",
                category="culture",
                description="UNESCO World Heritage Site featuring the world's tallest brick minaret.",
                estimated_cost_min=50.0,
                estimated_cost_max=600.0,
                recommended_duration="2 hours",
                best_for=["history", "culture"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Dilli Haat Crafts Market",
                category="shopping",
                description="Open-air food plaza and craft bazaar representing regional Indian states.",
                estimated_cost_min=100.0,
                estimated_cost_max=1000.0,
                recommended_duration="2-3 hours",
                best_for=["shopping", "food", "culture"],
                is_estimate=True,
            ),
        ],
        "jaipur": [
            DestinationPlace(
                name="Amer Fort Hilltop Tour",
                category="attraction",
                description="Majestic fortress overlooking Maota Lake known for artistic Hindu style elements.",
                estimated_cost_min=100.0,
                estimated_cost_max=500.0,
                recommended_duration="3 hours",
                best_for=["history", "culture", "sightseeing"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Hawa Mahal Outer & Rooftop View",
                category="culture",
                description="Palace of Winds constructed of red and pink sandstone with 953 small windows.",
                estimated_cost_min=50.0,
                estimated_cost_max=200.0,
                recommended_duration="1-2 hours",
                best_for=["history", "culture", "photography"],
                is_estimate=True,
            ),
            DestinationPlace(
                name="Johari Bazaar Shopping & Textiles",
                category="shopping",
                description="Historic pink city bazaar famous for Rajasthani jewelry, block prints, and handicrafts.",
                estimated_cost_min=200.0,
                estimated_cost_max=2000.0,
                recommended_duration="2-3 hours",
                best_for=["shopping", "culture"],
                is_estimate=True,
            ),
        ],
    }

    def get_destination_recommendations(
        self, request: TripRequest
    ) -> DestinationResults:
        dest_key = request.destination.strip().lower()

        # Check if destination exists in curated dataset
        if dest_key not in self.DATASET:
            return DestinationResults(
                destination=request.destination,
                supported=False,
                message=f"Recommendations for '{request.destination}' are currently unavailable in the curated dataset.",
                recommendations=[],
            )

        candidates = self.DATASET[dest_key]

        # Normalize preferences
        raw_prefs = [p.strip().lower() for p in request.preferences]

        # Score recommendations deterministically based on preference tag matches
        scored_places = []
        for place in candidates:
            score = 0
            if raw_prefs:
                # Check matches in place.best_for or category
                place_tags = [t.lower() for t in place.best_for] + [
                    place.category.lower()
                ]
                for pref in raw_prefs:
                    for tag in place_tags:
                        if pref in tag or tag in pref:
                            score += 1

            scored_places.append((score, place))

        # Sort deterministically by highest score first, then by place name
        scored_places.sort(key=lambda item: (-item[0], item[1].name))

        ranked_recommendations = [item[1] for item in scored_places]

        return DestinationResults(
            destination=request.destination,
            supported=True,
            recommendations=ranked_recommendations,
        )
