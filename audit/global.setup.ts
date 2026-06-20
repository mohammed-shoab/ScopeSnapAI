import { clerkSetup } from "@clerk/testing/playwright";

// Fetches a Clerk Testing Token (bypasses bot detection) using
// CLERK_PUBLISHABLE_KEY + CLERK_SECRET_KEY from the environment.
export default async function globalSetup() {
  await clerkSetup();
}
