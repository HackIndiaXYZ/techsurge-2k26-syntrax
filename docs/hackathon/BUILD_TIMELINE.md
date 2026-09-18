# Build Timeline

The only hard dependency chain is schema -> backend contracts -> deterministic evidence path -> UI integration -> failure rehearsal. Frontend starts immediately from fixtures; it does not wait for backend deployment. Deployment begins only once clean trigger and retry pass locally. The final hour is reserved for repetition and recovery, not a new feature.
