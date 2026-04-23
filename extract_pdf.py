from pypdf import PdfReader

reader = PdfReader("diplom.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

with open("diplom.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Text extracted to diplom.txt")