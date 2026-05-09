"use client";

/**
 * PostHogUserSync
 * Identifies the logged-in Clerk user in PostHog so events are attributed
 * to the correct person. Must be rendered inside <ClerkProvider>.
 *
 * Place this in the authenticated app layout — it runs once per session and
 * calls posthog.identify() with the Clerk userId + email/name traits.
 */

import { useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import posthog from "posthog-js";

export default function PostHogUserSync() {
  const { isLoaded, isSignedIn, user } = useUser();

  useEffect(() => {
    if (!isLoaded) return;

    if (isSignedIn && user) {
      const email = user.primaryEmailAddress?.emailAddress;
      posthog.identify(user.id, {
        email,
        name: user.fullName ?? undefined,
        created_at: user.createdAt?.toISOString(),
      });
    } else {
      // User signed out — reset PostHog so the next person starts fresh
      posthog.reset();
    }
  }, [isLoaded, isSignedIn, user]);

  return null;
}
