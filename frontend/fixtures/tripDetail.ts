import type { TripDetail } from "@/lib/types/trip";

export const tripDetailFixture: TripDetail = {
  id: "fixture-trip-id",
  prompt: "5 days in Tokyo, budget traveller, interested in temples, food markets, and local neighbourhoods",
  destination: "Tokyo, Japan",
  title: "Tokyo Essentials: Temples, Markets & Hidden Neighbourhoods",
  status: "completed",
  persona: "budget explorer",
  budget_level: "budget",
  total_days: 3,
  summary:
    "A curated 3-day Tokyo adventure balancing iconic temples, bustling food markets, and quieter local streets — all on a budget.",
  created_at: "2024-04-10T09:00:00Z",
  updated_at: "2024-04-10T09:45:00Z",
  conflicts: [
    {
      type: "timing_overlap",
      severity: "warning",
      day_number: 2,
      description:
        "Tsukiji Outer Market closes at 14:00 — the afternoon slot may arrive too late for the best stalls.",
      activities: ["Tsukiji Outer Market", "teamLab Borderless"],
    },
    {
      type: "distance",
      severity: "error",
      day_number: 3,
      description:
        "Nikko is over 2 hours from central Tokyo — this works best as a standalone day trip, not combined with afternoon city activities.",
      activities: ["Toshogu Shrine", "Kegon Falls"],
    },
  ],
  itinerary: {
    title: "Tokyo Essentials: Temples, Markets & Hidden Neighbourhoods",
    destination: "Tokyo, Japan",
    total_days: 3,
    budget_level: "budget",
    persona: "budget explorer",
    summary:
      "A curated 3-day Tokyo adventure balancing iconic temples, bustling food markets, and quieter local streets — all on a budget.",
    tips: [
      "Buy a Suica or Pasmo IC card at the airport — works on all trains, buses, and even convenience stores.",
      "Convenience stores (konbini) like 7-Eleven and Lawson serve excellent hot food for under ¥500.",
      "Most museums offer free admission on specific weekdays — check ahead.",
      "Google Maps works reliably for public transit directions in Tokyo.",
      "Cash is still preferred at many smaller restaurants and temples.",
    ],
    days: [
      {
        day_number: 1,
        date: "2024-04-10",
        title: "Asakusa & Ueno — Old Tokyo Foundations",
        weather: "16°C · Partly cloudy",
        day_summary:
          "Start with Tokyo's most historic quarter before moving to Ueno's cultural cluster — a dense, walkable day of temples, markets, and museums.",
        morning: {
          label: "morning",
          start_time: "09:00",
          end_time: "12:00",
          block_summary:
            "Explore Senso-ji temple complex and the surrounding Nakamise shopping street before crowds arrive.",
          activities: [
            {
              name: "Senso-ji Temple",
              description:
                "Tokyo's oldest Buddhist temple, founded in 645 AD. Walk through the iconic Kaminarimon gate, browse the Nakamise stalls for traditional souvenirs, and explore the temple grounds.",
              location: "Asakusa, Taito",
              latitude: 35.7148,
              longitude: 139.7967,
              duration_minutes: 90,
              cost_estimate: "Free",
              category: "culture",
              reasoning:
                "Senso-ji is the spiritual centrepiece of old Tokyo and an essential first stop — visiting early avoids the midday tour groups.",
            },
            {
              name: "Nakamise Shopping Street",
              description:
                "A 250-metre covered arcade leading to the temple, lined with stalls selling sembei rice crackers, yukata fabric, and traditional crafts.",
              location: "Asakusa, Taito",
              latitude: 35.7127,
              longitude: 139.7966,
              duration_minutes: 30,
              cost_estimate: "Optional — ¥200–500 per snack",
              category: "shopping",
              reasoning:
                "Inline with the temple approach — no extra travel time, and the snacks make a good budget breakfast.",
            },
          ],
        },
        afternoon: {
          label: "afternoon",
          start_time: "13:00",
          end_time: "17:00",
          block_summary:
            "Walk north to Ueno Park for museums and the famous cherry blossom avenue.",
          activities: [
            {
              name: "Ueno Park",
              description:
                "Tokyo's most famous park, home to cherry blossom trees, street performers, and a cluster of world-class museums. Walk the main avenue and visit the Toshogu shrine within the park.",
              location: "Ueno, Taito",
              latitude: 35.7156,
              longitude: 139.7745,
              duration_minutes: 60,
              cost_estimate: "Free",
              category: "nature",
              reasoning:
                "A short bus ride from Asakusa, Ueno connects a natural break with cultural depth and is entirely free to enter.",
            },
            {
              name: "Tokyo National Museum",
              description:
                "Japan's oldest and largest museum, housing over 110,000 items including samurai armour, ceramics, and Buddhist sculptures. The Honkan main building alone takes 1–2 hours.",
              location: "Ueno Park, Taito",
              latitude: 35.7188,
              longitude: 139.7764,
              duration_minutes: 90,
              cost_estimate: "¥1,000",
              category: "attraction",
              reasoning:
                "Best museum value in the city at ¥1,000 — aligns with the budget persona and provides historical depth before the food-heavy days ahead.",
            },
          ],
        },
        evening: {
          label: "evening",
          start_time: "18:00",
          end_time: "21:00",
          block_summary:
            "Head to Yanaka for dinner in a preserved Showa-era neighbourhood.",
          activities: [
            {
              name: "Yanaka Ginza",
              description:
                "A retro shopping street surviving from the 1950s, lined with small restaurants, tofu shops, and family-run izakayas. One of Tokyo's least touristy neighbourhoods.",
              location: "Yanaka, Taito",
              latitude: 35.7274,
              longitude: 139.7711,
              duration_minutes: 90,
              cost_estimate: "¥800–1,500 for dinner",
              category: "food",
              reasoning:
                "Yanaka preserves an authentic Tokyo that's largely disappeared elsewhere — perfect for a budget dinner and a slow evening wander.",
            },
          ],
        },
      },
      {
        day_number: 2,
        date: "2024-04-11",
        title: "Tsukiji, Shibuya & Harajuku — Food to Fashion",
        weather: "18°C · Sunny",
        day_summary:
          "An early market breakfast, a creative digital art detour, and an evening in Tokyo's most photogenic crosswalk district.",
        morning: {
          label: "morning",
          start_time: "08:00",
          end_time: "12:00",
          block_summary:
            "Hit Tsukiji Outer Market early for the freshest seafood breakfast in Tokyo.",
          activities: [
            {
              name: "Tsukiji Outer Market",
              description:
                "The public-facing outer ring of the old fish market, still buzzing with sushi vendors, tamagoyaki egg stalls, and fresh fruit stands. Arrive by 8–9am for the best selection.",
              location: "Tsukiji, Chuo",
              latitude: 35.6655,
              longitude: 139.7706,
              duration_minutes: 90,
              cost_estimate: "¥500–1,200 for breakfast",
              category: "food",
              reasoning:
                "Tsukiji closes many stalls by early afternoon — an 8am start ensures the best experience and avoids the conflict flagged for later visits.",
            },
          ],
        },
        afternoon: {
          label: "afternoon",
          start_time: "13:00",
          end_time: "17:00",
          block_summary:
            "Visit teamLab Borderless for an immersive digital art experience.",
          activities: [
            {
              name: "teamLab Borderless",
              description:
                "A borderless world of digital art where artworks move freely between rooms. Allow 2–3 hours to explore the full space without rushing.",
              location: "Azabudai Hills, Minato",
              latitude: 35.6564,
              longitude: 139.7415,
              duration_minutes: 150,
              cost_estimate: "¥3,200",
              category: "attraction",
              reasoning:
                "The new Azabudai location is less crowded than the original Odaiba venue — booking ahead is essential, and the afternoon slot fits naturally after the morning market.",
            },
          ],
        },
        evening: {
          label: "evening",
          start_time: "18:30",
          end_time: "21:30",
          block_summary:
            "Shibuya Crossing at dusk, then dinner in the backstreets of Harajuku.",
          activities: [
            {
              name: "Shibuya Crossing",
              description:
                "The world's busiest pedestrian intersection — best experienced from the Starbucks window or the rooftop of Shibuya Sky for an aerial view.",
              location: "Shibuya, Shibuya",
              latitude: 35.6595,
              longitude: 139.7005,
              duration_minutes: 30,
              cost_estimate: "Free (Shibuya Sky: ¥2,000)",
              category: "attraction",
              reasoning:
                "Evening light and rush-hour foot traffic make this the most dramatic time to visit — a quintessential Tokyo moment.",
            },
            {
              name: "Ura-Harajuku Dinner",
              description:
                "The backstreets behind Takeshita Street are lined with small ramen shops, yakitori joints, and curry houses — all reasonably priced and crowd-free.",
              location: "Harajuku, Shibuya",
              latitude: 35.6702,
              longitude: 139.7027,
              duration_minutes: 75,
              cost_estimate: "¥700–1,200",
              category: "food",
              reasoning:
                "Harajuku's back alleys offer the same quality as Shibuya restaurants at half the price — keeps the day within budget.",
            },
          ],
        },
      },
      {
        day_number: 3,
        date: "2024-04-12",
        title: "Shinjuku & Shimokitazawa — Megacity to Village",
        weather: "15°C · Light rain",
        day_summary:
          "A morning in Shinjuku's contrasts — park serenity next to neon chaos — followed by an afternoon in Tokyo's most bohemian neighbourhood.",
        morning: {
          label: "morning",
          start_time: "09:00",
          end_time: "12:00",
          block_summary:
            "Start the day in Shinjuku Gyoen for green space before the city noise takes over.",
          activities: [
            {
              name: "Shinjuku Gyoen National Garden",
              description:
                "A sprawling 58-hectare park blending Japanese, French formal, and English landscape garden styles. One of the best cherry blossom spots in Tokyo when in season.",
              location: "Shinjuku, Shinjuku",
              latitude: 35.6851,
              longitude: 139.71,
              duration_minutes: 90,
              cost_estimate: "¥500",
              category: "nature",
              reasoning:
                "A calm, budget-friendly counterpoint to the day's later energy — and practically next to the transit hub for Shimokitazawa.",
            },
            {
              name: "Omoide Yokocho",
              description:
                "Memory Lane — a narrow alley of tiny yakitori and ramen stalls, some operating since 1945. Atmospheric even by day, and an affordable lunch spot.",
              location: "Shinjuku, Shinjuku",
              latitude: 35.6938,
              longitude: 139.7004,
              duration_minutes: 45,
              cost_estimate: "¥800–1,200 for lunch",
              category: "food",
              reasoning:
                "A five-minute walk from the west exit of Shinjuku Station — no extra transit cost, and the atmosphere is unmissable.",
            },
          ],
        },
        afternoon: {
          label: "afternoon",
          start_time: "13:30",
          end_time: "17:30",
          block_summary:
            "Head south to Shimokitazawa, Tokyo's vinyl-and-vintage neighbourhood.",
          activities: [
            {
              name: "Shimokitazawa Vintage Browsing",
              description:
                "A labyrinthine neighbourhood packed with second-hand clothing shops, record stores, independent cafés, and small live music venues. Ideal for slow exploration.",
              location: "Shimokitazawa, Setagaya",
              latitude: 35.6612,
              longitude: 139.6675,
              duration_minutes: 120,
              cost_estimate: "Free to browse — optional vintage finds ¥500–3,000",
              category: "shopping",
              reasoning:
                "Shimokitazawa has the highest density of interesting independent shops in Tokyo without the Harajuku prices — perfect for a budget traveller who wants to take something home.",
            },
          ],
        },
        evening: {
          label: "evening",
          start_time: "18:30",
          end_time: "21:00",
          block_summary:
            "Final evening in Shinjuku — izakaya dinner, then optional walk through Kabukicho.",
          activities: [
            {
              name: "Shinjuku Izakaya Dinner",
              description:
                "Pick any of the dozens of izakayas east of Shinjuku Station for a leisurely final dinner of small plates, yakitori skewers, and draft beer.",
              location: "East Shinjuku, Shinjuku",
              latitude: 35.6929,
              longitude: 139.7043,
              duration_minutes: 90,
              cost_estimate: "¥1,200–2,000",
              category: "food",
              reasoning:
                "A fitting close to the trip — izakayas are the social backbone of Tokyo nightlife, and the east side of Shinjuku has dozens of options at all price points.",
            },
            {
              name: "Kabukicho Wander",
              description:
                "Tokyo's famous entertainment district — vivid neon, arcades, and the Godzilla head atop Shinjuku Toho Cinema. Best experienced as an evening walk rather than a destination.",
              location: "Kabukicho, Shinjuku",
              latitude: 35.696,
              longitude: 139.7036,
              duration_minutes: 30,
              cost_estimate: "Free",
              category: "nightlife",
              reasoning:
                "Zero cost, no planning required — a spontaneous end to the trip that captures the electric side of Tokyo.",
            },
          ],
        },
      },
    ],
  },
};
