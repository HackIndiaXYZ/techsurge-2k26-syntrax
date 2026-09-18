# Source Material Index

| Source | Classification | How used |
| --- | --- | --- |
| `PS_F03.pdf` supplied by the team, 18 Sep 2026 | Official PS requirement | Primary authority for problem, minimum flow, safety boundaries, evaluation and deliverable |
| Official PDF reference links | External references named by organizers | Context only; not independently treated as implementation requirement |
| This repository’s team/branch record | Team fact | Ownership and workflow |
| Synthetic fixtures defined in `database/DATA_SEEDING.md` | Team design decision | Reproducible demo/test input |
| [NASA GPM IMERG](https://gpm.nasa.gov/data/imerg) | External verified data reference | Candidate public precipitation reference only; its products have different temporal resolutions and rate/accumulation units, so any adapter must normalize before use |
| [IMD API list](https://mausamaudit.imd.gov.in/Forecast/marquee_data/API_doc.pdf) | External verified data reference | Candidate public weather-data reference only; no access, contract or live integration is assumed |
| [The Byzantine Generals Problem](https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/) | External verified technical reference | Defines the fault-agreement concept; does not make this MVP formally Byzantine fault tolerant |

No proprietary organizer dataset, data-provider contract, real payment credential, or real customer record is present or required.
