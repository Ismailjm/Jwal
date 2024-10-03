from langdetect import detect, detect_langs

text = "how are you"

# Detect the language
language = detect(text)

print(f"The detected language is: {language}")

# Detect language probabilities
probabilities = detect_langs(text)
print(f"Language probabilities: {probabilities}")
