BTL_bigdata/
├── README.md
├── requirements.txt
├── config.yaml
├── .env.example
├── .gitignore
├── app.py
├── TEAM_ASSIGNMENT.md
│
├── src/
│   ├── __init__.py
│   ├── schemas.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── collector.py        ← CHI
│   │   ├── parser.py           ← CHI
│   │   └── manifest.py         ← CHI
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── spark_etl.py        ← THANH
│   │   └── chunker.py          ← THANH
│   └── rag/
│       ├── __init__.py
│       ├── indexer.py          ← THANH
│       ├── retriever.py        ← THANH
│       └── answerer.py         ← THANH
│
├── data/
│   ├── sources.csv
│   ├── raw/               (gitignored, generated)
│   ├── parsed/            (gitignored, generated)
│   ├── processed/         (gitignored, generated)
│   ├── chunks/            (gitignored, generated)
│   ├── manifests/         (gitignored, generated)
│   └── bronze/
│       ├── international/
│       │   ├── eu/        ← CHI fills with 2 PDFs
│       │   ├── nist/      ← CHI fills with 3 PDFs
│       │   ├── oecd/      ← CHI fills with 2 PDFs
│       │   ├── unesco/    ← CHI fills with 2 PDFs
│       │   └── other/     ← CHI fills with 6 PDFs
│       ├── vietnam/
│       │   ├── government/ ← THANH ✅ (9 PDFs added)
│       │   ├── ministries/
│       │   └── strategy/  ← THANH ✅ (6 PDFs added)
│       ├── supplementary/
│       │   ├── asean/
│       │   ├── research/
│       │   └── standards/
│       └── metadata/
│           ├── international_documents.csv  ← CHI
│           └── vietnam_documents.csv        ← THANH ✅
│
├── scripts/
│   ├── run_collect.py      ← CHI
│   ├── run_parse.py        ← CHI
│   ├── run_etl.py          ← THANH
│   ├── run_chunk.py        ← THANH
│   ├── run_index.py        ← THANH
│   ├── run_pipeline.py     ← TRANG
│   └── generate_checksums.py
│
├── tests/
│   ├── __init__.py
│   ├── test_schemas.py     ← TRANG
│   └── test_integration.py ← TRANG (TC01-TC09)
│
└── evaluation/
    ├── qa_eval_set.csv     ← TRANG (30 câu hỏi)
    └── eval_runner.py      ← TRANG
