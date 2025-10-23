# Hitcher Vector-Sharing Platform — Product Requirements Document

## 1. Executive Summary
Hitcher is a crowdsourced, location-aware platform that enables users to efficiently share travel vectors—periods during which two or more users travel in the same direction and can ride together. The product removes friction from ad-hoc ridesharing by pairing "drivers" and "riders" (both considered users) who explicitly opt into sharing a journey, while providing transparency and trust through feedback profiles and verifiable identity data. The initial release targets urban and suburban commuters seeking flexible, cost-effective, and sustainable transportation alternatives. This PRD now also tracks the implementation blueprint guiding the first production build, covering backend services, the Android client, and supporting infrastructure.

## 2. Goals & Non-Goals
### 2.1 Goals
- Reduce the time and effort required to find compatible ride partners travelling along similar routes in real time or for scheduled trips.
- Provide reliable trust and safety signals through a unified reputation profile that can ingest external marketplace feedback (e.g., Facebook Marketplace, eBay) where legally permissible.
- Optimize route-matching to maximize vector efficiency (minimize detours, maximize shared distance/time).
- Ensure compliance with relevant transportation, data privacy, and platform liability regulations in pilot regions.
- Deliver an MVP composed of a production-ready backend service, a native Android client, and shared design system assets that enable iterative feature expansion.

### 2.2 Non-Goals (Initial Release)
- Processing in-app payments or escrow between users (allow expense splitting suggestions only).
- Providing commercial ride-hailing services or professional driver vetting.
- Supporting freight or large parcel delivery (limited to personal items riders can carry).
- Building a full-fledged social network or community forum beyond ride coordination and feedback.

## 3. Target Users & Personas
1. **Efficiency Commuter (Driver):** Mid-30s professional commuting 10–30 miles daily, willing to share empty seats to offset costs and promote sustainability.
2. **Budget Traveler (Rider):** Young professional/student with flexible schedule seeking low-cost rides vs. ride-hailing or public transit gaps.
3. **Micro-Logistics Sender (Item Rider):** Individuals or small businesses needing to send small items along existing routes (e.g., forgotten laptop). Requires high trust and tracking transparency.

## 4. User Experience Overview
- Users create a Hitcher profile, verify identity, and connect optional external reputation sources.
- Drivers publish live or scheduled vectors by setting start, waypoint, and end locations/time windows.
- Riders browse/search nearby or future vectors and request to "hook up" for overlapping segments.
- Both parties review each other’s trust profiles, negotiate optional cost-sharing, confirm match, and receive navigation guidance.
- Post-ride, participants rate each other and submit feedback to evolve trust metrics.
- Android MVP scope:
  - Core tabs: **Explore** (browse vectors), **My Trips** (upcoming/past rides), **Messages**, **Profile**.
  - Map view showing drivers, vector cards, and call-to-action for hook-up requests.
  - Background services for location updates (drivers) and push notifications.
  - Accessibility target: WCAG AA contrast, TalkBack labels on interactive elements.

## 5. User Stories
### Driver
- As a driver, I can publish an upcoming trip with start/end points, route preference, and seat availability so riders can request to join.
- As a driver, I can view rider requests with estimated detour impact, trust score, and proposed pickup/drop-off points before accepting.
- As a driver, I receive turn-by-turn navigation that integrates confirmed pickups/drop-offs while highlighting shared vector segments.

### Rider
- As a rider, I can set desired departure/arrival areas, time windows, and acceptable detour length to discover compatible drivers.
- As a rider, I can review driver trust metrics, vehicle details, and past feedback before requesting to hook up.
- As a rider, I receive notifications of driver acceptance and can track the driver’s live location en route to pickup.

### Shared
- As any user, I can connect external marketplace accounts (Facebook Marketplace, eBay, others) to import reputation metrics, subject to user consent and platform policies.
- As any user, I can report safety incidents or no-shows, triggering moderation workflows.
- As any user, I can message matched partners securely within the app to coordinate specifics.

## 6. Functional Requirements
### 6.1 Account & Identity
- Email/phone-based signup with multi-factor authentication.
- Optional social login (Apple, Google, Facebook) for faster onboarding.
- Identity verification: government ID upload + selfie, with third-party verification vendor integration.
- Profile fields: photo, bio, preferred communication, vehicle details (for drivers), accessibility info.

### 6.2 Reputation & Trust
- Internal rating system (1–5 stars + written feedback) per completed vector segment.
- Reputation score aggregation model weighting recency, volume, and severity of reports.
- External feedback import:
  - OAuth or secure scraping partnerships with Facebook Marketplace, eBay, or other marketplaces.
  - Normalize external ratings to Hitcher trust metrics with clear provenance labels.
  - Consent management UI allowing users to revoke data access.
- Trust badges: Verified Identity, Background Check (if offered), High Reliability, Top Helper.

### 6.3 Vector Creation & Discovery
- Drivers create vectors with: start/end locations, optional via waypoints, departure window, seats, luggage capacity, price suggestion (manual entry, not processed in-app).
- Riders create ride intents with: origin/destination areas (radius), time window, max detour tolerance, cost contribution preference.
- Matching engine requirements:
  - Spatial-temporal overlap detection using GIS algorithms (e.g., R-tree for geo queries) and predictive ETA modeling.
  - Vector similarity score combining direction alignment, overlap duration, and detour cost.
  - Real-time updates for live trips, recalculating matches as drivers move.
- Results list with ranked matches, estimated pickup/drop-off, shared time, and trust indicators.
- MVP constraint: initial implementation will simulate matching with heuristic scoring while data collection begins for full predictive model.

### 6.4 Hook-Up Confirmation Flow
- Riders send hook-up requests specifying pickup/drop-off suggestions and optional notes.
- Drivers review requests, adjust pickup/drop-off (within rider constraints), accept or decline.
- Mutual confirmation required before itinerary lock; autop-expire pending requests after configurable time.
- Once confirmed:
  - Both parties receive navigation guidance and calendar integration (optional).
  - In-app chat opens; push/SMS notifications triggered.
  - ETA sharing and live tracking activated.

### 6.5 Trip Execution
- Pre-trip reminders and check-in prompts to confirm readiness.
- Live GPS tracking for drivers, shareable with riders.
- Pick-up confirmation via in-app button or NFC handshake for item transfers.
- Post-drop-off flow requesting feedback, flagging incidents, and logging completion.

### 6.6 Safety & Moderation
- Panic/emergency button linking to local authorities and emergency contacts.
- Incident reporting with evidence upload, triaged by moderation tools.
- Automated detection of suspicious behavior (e.g., repeated cancellations, low ratings) triggering review.
- Block/ban functionality and audit trail for all enforcement actions.

### 6.7 Notifications & Communications
- Push notifications (iOS/Android), SMS, and email for key events (match found, request accepted, arrival reminders).
- In-app chat with read receipts and attachment support (photos of pickup spot, item).
- Notification preference center allowing granular control.

### 6.8 Analytics & Insights
- Core metrics: active users, vectors created, successful hookups, average shared distance/time, trust score distribution.
- Funnel analytics for onboarding, vector creation, hook-up acceptance, trip completion.
- Geo heatmaps for supply/demand, imbalance alerts.
- Admin dashboards for reputation data ingestion health and moderation queue.

## 7. Non-Functional Requirements
- **Platforms:** Native iOS & Android clients; responsive web MVP for discovery and profile management.
- **Scalability:** Support 10k daily active users in pilot regions with sub-second match queries; design matching service using scalable geospatial database (e.g., PostGIS, MongoDB with GeoJSON) and caching.
- **Reliability:** 99.5% uptime target for critical services; graceful degradation for real-time tracking.
- **Performance:** Location updates at least every 5 seconds during active trips; push notifications delivered within 10 seconds of triggers.
- **Security & Privacy:** GDPR/CCPA compliance, data minimization, encrypted data at rest/in transit, role-based admin access, audit logging.
- **Internationalization:** Prepare for multi-language support (English-first, others via localization pipeline).
- **Documentation:** Publish API reference, Android client handoff notes, and ops runbooks alongside each release.
- **Testing:** Maintain automated unit, integration, and UI test coverage thresholds defined per component.

## 8. Data & Integrations
- **Mapping & Routing:** Integrate with providers (Mapbox, Google Maps, HERE) for routing, traffic, and geocoding.
- **Identity Verification:** Partner APIs (e.g., Persona, Onfido) for KYC checks.
- **External Reputation Data:** OAuth integrations; legal review to ensure ToS compliance when importing external feedback. Implement refresh cadence and data provenance logs.
- **Messaging & Notifications:** Firebase Cloud Messaging, Apple Push Notification service, SMS aggregator (Twilio).
- **Analytics:** Data warehouse (Snowflake/BigQuery) fed via ETL from operational DB; use Segment or custom event pipeline.

## 8.1 Product Scope for MVP (Phase 0)
- Identity and profile creation with manual admin approval for verification completion.
- Vector publishing for drivers and ride intent creation for riders with heuristic-based matching results.
- Hook-up confirmation workflow with in-app chat MVP (text only) and push notification stubs.
- Ratings submission and moderation queue to resolve disputes.
- Foundational analytics counters covering daily active users, vectors, and hook-up conversion rate.

## 9. Technical Architecture Overview
### 9.1 System Components
- **Mobile Client (Android/Kotlin):** Native app managing onboarding, vector workflows, chat, and background location services for drivers.
- **Backend Service (FastAPI/Python):** RESTful API handling authentication (MVP token-based), vector lifecycle, matching heuristics, chat message relay, and analytics ingestion.
- **Database:** PostgreSQL with PostGIS extension (planned) accessed via SQLAlchemy models and Alembic migrations.
- **Real-Time Messaging:** WebSocket endpoints for chat and live location streaming targeted for Phase 1; Firebase Cloud Messaging provides push delivery in MVP.
- **External Services:** Mapbox APIs for maps/geocoding, Persona for identity verification, Twilio for SMS fallbacks.

### 9.2 Data Flow
1. Users authenticate via email/OTP; backend issues JWT access/refresh tokens.
2. Drivers submit vectors; backend persists route geometry and calculates compatibility heuristics.
3. Riders request matches; backend returns ranked vectors and manages hook-up confirmations.
4. Chat and notification events propagate through messaging services; trip completion triggers feedback tasks.

### 9.3 Deployment Strategy
- Backend deployed as containerized service on managed Kubernetes (e.g., GKE/EKS) with GitHub Actions CI/CD, automated testing, and infrastructure-as-code (Terraform) for environments.
- Android client distributed through Firebase App Distribution for internal testing prior to Play Store beta rollout.
- Observability includes OpenTelemetry traces, Prometheus metrics, and centralized structured logging (ELK stack).

### 9.4 Security & Compliance Enhancements
- Secrets managed with cloud secret manager, rotated quarterly and restricted via IAM policies.
- Privacy impact assessments executed before integrating third-party reputation data sources.
- Data retention policy: anonymize personal trip/location data after 180 days while retaining aggregated insights.

## 10. Design & Research Plan
- Conduct moderated usability testing on Explore and Hook-Up flows with diverse participants.
- Implement design tokens shared between Android and future web clients to ensure consistency.
- Document motion/animation guidelines emphasizing predictability and confirmation states to reinforce trust.
- Maintain accessibility review checklist per release including TalkBack/VoiceOver audits.

## 11. Delivery Roadmap Snapshot
- **Sprint 1:** Backend scaffolding, authentication MVP, Android project setup with onboarding and Explore placeholders.
- **Sprint 2:** Vector creation/listing endpoints and Android UI with local persistence for drafts.
- **Sprint 3:** Matching heuristic service, push notification integration (stub), and trip state machine implementation.
- **Sprint 4:** Chat MVP, analytics instrumentation, and beta readiness checklist execution.
- **Beta Exit Criteria:** 1k completed trips, <5% crash rate, positive qualitative feedback on trust and safety features.

## 12. Legal, Compliance, & Risk
- Review transportation regulations for ridesharing/carpooling in target geographies (insurance, liability, occupancy limits).
- Develop terms of service clarifying that Hitcher facilitates peer connections, not commercial transport.
- Implement consent flows for data sharing and background checks.
- Prepare incident response playbook covering law enforcement requests, data breaches, and safety escalations.
- Mitigate external data ingestion risks (data accuracy, revocation handling, rate limits).

## 13. Launch Plan
- **Phase 0 (3 months):** Internal alpha with employees/friends, focus on matching algorithm accuracy, identity verification, and UI feedback.
- **Phase 1 (6 months):** Closed beta in one metro area (e.g., Austin), 500 users; monitor supply-demand balance, refine reputation score UX.
- **Phase 2 (9–12 months):** Expand to additional cities, introduce item rider workflows, optimize retention loops.
- **Success Metrics:** 40% hook-up conversion rate, NPS > 45, average rating ≥ 4.6, incident rate < 0.5% of completed trips.

## 14. Open Questions & Future Enhancements
- Monetization model: subscription vs. per-trip fee vs. employer partnerships.
- Insurance coverage partnerships for drivers during shared vectors.
- Dynamic pricing guidance based on gas prices and demand.
- Integration with public transit schedules for multi-modal planning.
- API for third-party logistics partners to request vectors for item delivery.

## 15. Stakeholders
- Product: PM, UX Designer, Research Lead.
- Engineering: Mobile leads (iOS, Android), Backend lead, Data scientist (matching & trust models).
- Operations: Trust & Safety manager, Customer Support, Legal counsel.
- External: Identity vendor, mapping provider, marketplace partners for reputation data.

