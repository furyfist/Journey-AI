interface WeatherStripProps {
  weather: string;
}

function conditionEmoji(weather: string): string {
  const lower = weather.toLowerCase();
  if (lower.includes("snow") || lower.includes("blizzard")) return "❄️";
  if (lower.includes("rain") || lower.includes("shower") || lower.includes("drizzle")) return "🌧";
  if (lower.includes("cloud") || lower.includes("overcast") || lower.includes("foggy")) return "🌤";
  if (lower.includes("thunder") || lower.includes("storm")) return "⛈";
  if (lower.includes("wind")) return "💨";
  return "☀️";
}

export default function WeatherStrip({ weather }: WeatherStripProps) {
  const emoji = conditionEmoji(weather);
  return (
    <p className="text-sm text-text-muted">
      {emoji} {weather}
    </p>
  );
}
