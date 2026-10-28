# Bark personal Apple signing — one-time setup

Prepared in code; Apple provisioning and deployment are **not yet complete**.

Team: `NA6HPWARQ2`
Main Bundle ID: `com.davidpovarsky.bark`
Widget: `com.davidpovarsky.bark.Widget`
Notification Service: `com.davidpovarsky.bark.NotificationServiceExtension`
Notification Content: `com.davidpovarsky.bark.NotificationContent`
App Group: `group.com.davidpovarsky.bark`

## Apple Developer actions

In https://developer.apple.com/account/resources/identifiers/list, register the four explicit App IDs if absent. Enable Push Notifications for the main App ID, enable App Groups for all four, register the group and associate all four targets. Reuse an existing active Apple Distribution certificate with accessible private key. Create four App Store Connect provisioning profiles, one per target, with matching Team, Bundle IDs, App Group, and production APNs for the main app. Do not revoke existing certificates.

Verify whether the local `AuthKey_BMFQPP6252.p8` is a valid APNs key for the paid team. An App Store Connect API key is not necessarily an APNs key. If required, create an APNs Auth Key with Apple Push Notifications service enabled, record its Key ID and securely retain its one-time downloadable private key. For TestFlight, create the App Store Connect app record for `com.davidpovarsky.bark`.

## GitHub Actions secrets

At https://github.com/davidpovarsky/Bark/settings/secrets/actions set:

- `APPLE_CERTIFICATE_P12_B64`: base64 of distribution certificate including private key
- `APPLE_CERTIFICATE_PASSWORD`: password for the p12
- `APPLE_MAIN_PROVISIONING_PROFILE_B64`: base64 of main App Store profile
- `APPLE_WIDGETS_PROVISIONING_PROFILE_B64`: base64 of Widget App Store profile
- `APPLE_SERVICE_PROVISIONING_PROFILE_B64`: base64 of Notification Service profile
- `APPLE_CONTENT_PROVISIONING_PROFILE_B64`: base64 of Notification Content profile
- For TestFlight: `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_P8` (PEM contents)

The manual workflow `personal-apple-signed-ipa.yml` validates the profiles, imports signing credentials into a temporary keychain, archives and verifies all signed bundles, then uploads an IPA artifact. TestFlight upload is opt-in. It does not publish to the App Store.

## Cloudflare Worker

In the `bark-worker` Cloudflare Worker, set secrets `APNS_PRIVATE_KEY` (actual APNs p8 PEM) and `APNS_KEY_ID` (matching APNs key ID). The Worker branch `fix/apns-config` sets nonsecret `APNS_TEAM_ID=NA6HPWARQ2`, `APNS_TOPIC=com.davidpovarsky.bark`, `APNS_ENVIRONMENT=production`. Deploy only after the secrets are present: the original embedded vendor APNs key was removed.

## Testing

Install via TestFlight so Apple Push entitlements remain intact. Open Bark, allow notifications, confirm registration with the private Worker and test a real push. The unsigned IPA re-signed by SideStore is not a valid APNs verification path. Existing upstream Deflector files are untouched; the signed identity overlay is applied only during the manual signing build.
