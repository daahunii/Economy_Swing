# Economy Swing development rules

- Read `README.md`, the relevant design document, and `docs/05-development-status.md` before changing a feature.
- Keep market/financial calculations in the Python domain layer. The web formats and presents API results.
- Keep HTTP handling, application orchestration, data access, and pure calculations separate. Do not introduce a framework dependency into pure calculation functions.
- Place UI code in its feature directory. Reuse shared UI/formatting only when actually shared.
- Generate web API types with `npm run contracts`; do not hand-edit `schema.d.ts`.
- Treat every current fixture as synthetic. Preserve visible demo labels and exclude demo values from any future real performance reports.
- Missing or invalid inputs must remain missing/invalid. Never replace API failures with plausible market numbers.
- Version scoring rules and preserve old analysis inputs/results when real persistence is introduced.
- Maintain the existing Vercel target: Next.js web, FastAPI API, external persistent storage. Do not publish to another host.
- Run checks relevant to the change: TypeScript/build for web changes; calculation/API tests for backend changes. Update development status and runbooks with material behavior changes.
- Never commit secrets, virtual environments, node_modules, generated build output, or private provider data.
