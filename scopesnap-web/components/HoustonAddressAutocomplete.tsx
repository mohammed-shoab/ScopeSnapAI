/**
 * HoustonAddressAutocomplete
 *
 * Google Places API autocomplete for US (Houston) market address entry.
 * Gates: only renders autocomplete when NEXT_PUBLIC_GOOGLE_MAPS_API_KEY is set.
 * Falls back to a plain <input> on load error or missing key.
 *
 * Stage 3 — Track F C.2  |  DEC-074
 * Market gate: detectMarket() === "US" enforced by the caller (assess/page.tsx).
 */
"use client";

import { useRef } from "react";
import { useLoadScript, Autocomplete } from "@react-google-maps/api";

const LIBRARIES: ("places")[] = ["places"];

export interface HoustonAddressAutocompleteProps {
  value: string;
  onChange: (val: string) => void;
  /** Called when the input gains focus (e.g. to show existing-property suggestions) */
  onFocus?: () => void;
  /** Called when a Google Places result is selected (e.g. to hide existing-property suggestions) */
  onPlaceSelected?: () => void;
  placeholder?: string;
  className?: string;
  required?: boolean;
}

// ─── Plain fallback ───────────────────────────────────────────────────────────
function PlainInput({
  value,
  onChange,
  onFocus,
  placeholder,
  className,
  required,
}: HoustonAddressAutocompleteProps) {
  return (
    <input
      type="text"
      value={value}
      onChange={e => onChange(e.target.value)}
      onFocus={onFocus}
      placeholder={placeholder}
      className={className}
      required={required}
    />
  );
}

// ─── Inner component that owns the useLoadScript hook ────────────────────────
// Rendered only when apiKey is present (avoids conditional hook call).
function AutocompleteInput(props: HoustonAddressAutocompleteProps) {
  const { value, onChange, onFocus, onPlaceSelected, placeholder, className, required } = props;
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!;
  const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(null);

  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: apiKey,
    libraries: LIBRARIES,
  });

  if (loadError) {
    console.warn("[HoustonAddressAutocomplete] Google Maps failed to load:", loadError);
    return <PlainInput {...props} />;
  }

  // While script loads, show a responsive plain input (still functional for typing)
  if (!isLoaded) {
    return <PlainInput {...props} placeholder={placeholder ?? "Loading address suggestions…"} />;
  }

  const onPlaceChanged = () => {
    const place = autocompleteRef.current?.getPlace();
    if (place?.formatted_address) {
      onChange(place.formatted_address);
      onPlaceSelected?.();
    }
  };

  return (
    <Autocomplete
      onLoad={a => { autocompleteRef.current = a; }}
      onPlaceChanged={onPlaceChanged}
      options={{
        componentRestrictions: { country: "us" },
        fields: ["formatted_address"],
        types: ["address"],
      }}
    >
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        onFocus={onFocus}
        placeholder={placeholder}
        className={className}
        required={required}
      />
    </Autocomplete>
  );
}

// ─── Public export ─────────────────────────────────────────────────────────
/**
 * Renders Google Places autocomplete for US Houston address entry.
 * Falls back to a plain <input> if NEXT_PUBLIC_GOOGLE_MAPS_API_KEY is not set,
 * allowing the dev/staging environment to work without the key configured.
 */
export default function HoustonAddressAutocomplete(props: HoustonAddressAutocompleteProps) {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

  // No key → plain input (dev, staging without key, or env var missing)
  if (!apiKey) {
    return <PlainInput {...props} />;
  }

  return <AutocompleteInput {...props} />;
}
