[P1] Correct the claim that every agent operation enforces an active grant — docs/SECURITY_AND_PRIVACY.md:31

`AgentAPI.get_capabilities()` performs no grant or observation-authorization check, while `get_access_grant()` returns `None` for an expired or disabled grant. A still-valid token can therefore invoke these operations after grant expiry, contrary to this security statement and the equivalent claim in `docs/AGENT_INTEGRATION.md`. Narrow the documentation or change the implementation in a later, appropriately scoped phase.

[P1] Make the clean-checkout installation path self-contained — docs/INSTALLATION.md:21

The procedure assumes that a correctly named sibling `asw-spec-codex` checkout and Windows App Runtime 2.3.1 already exist. It supplies neither repository acquisition/commit-checkout instructions nor an actionable runtime installation and verification path. A new user starting from the public release surface cannot reproduce the documented installation.

[P2] Do not tell GUI users they can select event types — README.md:76

The GUI subscription flow accepts applications, categories, and destinations but always writes `event_types: []`; it exposes no event-type selector. The README and user guide describe optional event-type selection as part of the current GUI journey, sending users looking for a control that does not exist.

[P2] Remove the nonexistent Applications-page navigation route — docs/USER_GUIDE.md:39

The guide says the Applications view provides a route to permissions and subscriptions, but the implementation only displays application rows and a `Register application` action. Permissions and subscriptions are separate top-level pages, so this description misdirects first-time users.

[P2] Freeze or record the qualified Python dependency set — docs/INSTALLATION.md:16

The installation guide presents the dependency file as the qualified versions, but `requirements-windows.txt` uses open-ended lower bounds such as `watchdog>=6.0` and `psutil>=7.0`. A future clean installation may resolve materially different bridge versions from the accepted runtime, preventing reproducible installation and qualification.

Overall assessment: Phase 9B is not ready for sign-off. The observe-versus-subscribe journey, core agent request envelopes, local-data warnings, and signal-authority boundaries are otherwise explained clearly and generally match the implementation.

Material test gaps: there is no documentation-to-GUI test covering exposed subscription controls or Applications-page actions; agent tests do not exercise capability/grant operations with an expired grant while the token remains valid; and no recorded clean-checkout test proves repository acquisition, Windows App Runtime setup, and dependency resolution from the public instructions. No files were modified.