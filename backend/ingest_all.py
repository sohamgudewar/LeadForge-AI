from rag.ingest import ingest_pdf

companies = [
    "uploads/slack.pdf",
    "uploads/openai.pdf",
    "uploads/salesforce.pdf",
]

for pdf in companies:
    ingest_pdf(pdf)

print("All PDFs ingested successfully")
