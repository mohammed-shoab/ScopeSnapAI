/**
 * HoustonAddressAutocomplete
 * Google Places API autocomplete for US (Houston) market address entry.
 * Gates: only renders autocomplete when NEXT_PUBLIC_GOOGLE_MAPS_API_KEY is set.
 * Falls back to a plain <input> on load error or missing key.
 * Stage 3 — Track F C.2 | DEC-074
 * Market gate: detectMarket() === "US" enforced by the caller (assess/page.tsx).
 *
 * Note: Uses direct <script> injection instead of @react-google-maps/api useLoadScript
 * to avoid the `loading=async` + `callback=initMap` 503 conflict (DEC-075).
 */
"use client";
import { useEffect, useRef, useState } from "react";

const MAPS_SCRIPT_ID = "google-maps-places-loader";

/** Inject the Maps JS script once and resolve when places library is ready. */
function ensureMapsScript(apiKey: string): Promise<void> {
  return new Promise((resolve, reject) => {
    // Already available
    if (
      typeof google !== "undefined" &&
      google?.maps?.places
    ) {
      resolve();
      return;
    }
    // Script tag already in DOM — attach listeners
    const existing = document.getElementById(
      MAPS_SCRIPT_ID
    ) as HTMLScriptElement | null;
    if (existing) {
      if (existing.dataset.loaded === "1") {
        resolve();
        return;
      }
      existing.addEventListener("load", () => {
        existing.dataset.loaded = "1";
        resolve();
      });
      existing.addEventListener("error", reject);
      return;
    }
    // Inject fresh script — plain URL, no loading=async, no callback param
    const script = document.createElement("script");
    script.id = MAPS_SCRIPT_ID;
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(
      apiKey
    )}&libraries=places`;
    script.async = true;
    script.onload = () => {
      script.dataset.loaded = "1";
      resolve();
    };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

export interface HoustonAddressAutocompleteProps {
  value: string;
  onChange: (val: string) => void;
  onFocus?: () => void;
  onPlaceSelected?: () => void;
  placeholder?: string;
  className?: string;
  required?: boolean;
}

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
      onChange={(e) => onChange(e.target.value)}
      onFocus={onFocus}
      placeholder={placeholder}
      className={className}
      required={required}
    />
  );
}

export default function HoustonAddressAutocomplete(
  props: HoustonAddressAutocompleteProps
) {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;
  const inputRef = useRef<HTMLInputElement>(null);
  const acRef = useRef<google.maps.places.Autocomplete | null>(null);
  // Keep a ref to latest props so the place_changed listener never stales
  const propsRef = useRef(props);
  propsRef.current = props;

  const [isLoaded, setIsLoaded] = useState(false);
  const [loadError, setLoadError] = useState(false);

  // Load script on mount (only when key is present)
  useEffect(() => {
    if (!apiKey) return;
    ensureMapsScript(apiKey)
      .then(() => setIsLoaded(true))
      .catch((e) => {
        console.warn("[HoustonAddressAutocomplete] Google Maps failed to load:", e);
        setLoadError(true);
      });
  }, [apiKey]);

  // Attach native Autocomplete once script is ready
  useEffect(() => {
    if (!isLoaded || !inputRef.current || acRef.current) return;
    try {
      const ac = new google.maps.places.Autocomplete(inputRef.current, {
        componentRestrictions: { country: "us" },
        fields: ["formatted_address"],
        types: ["address"],
      });
      ac.addListener("place_changed", () => {
        const place = ac.getPlace();
        if (place?.formatted_address) {
          propsRef.current.onChange(place.formatted_address);
          propsRef.current.onPlaceSelected?.();
        }
      });
      acRef.current = ac;
    } catch (e) {
      console.warn(
        "[HoustonAddressAutocomplete] Failed to initialize Autocomplete:",
        e
      );
      setLoadError(true);
    }
  }, [isLoaded]);

  if (!apiKey || loadError) {
    return <PlainInput {...props} />;
  }

  return (
    <input
      ref={inputRef}
      type="text"
      value={props.value}
      onChange={(e) => props.onChange(e.target.value)}
      onFocus={props.onFocus}
      placeholder={
        isLoaded
          ? props.placeholder
          : props.placeholder ?? "Loading address suggestions…"
      }
      className={props.className}
      required={props.required}
    />
  );
}
