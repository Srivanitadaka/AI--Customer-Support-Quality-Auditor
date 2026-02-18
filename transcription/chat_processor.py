import os
import json

# -------------------------
# Paths
# -------------------------
CHAT_FOLDER = "../sample_data/chats"
OUTPUT_FOLDER = "../transcription/sample_outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("💬 Processing chats...\n")

'''count = 1

for file in os.listdir(CHAT_FOLDER):

    if file.endswith(".txt"):

        path = os.path.join(CHAT_FOLDER, file)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        data = {
            "chat_id": f"chat_{count}",
            "file_name": file,
            "conversation": text
        }

        out_file = os.path.join(
            OUTPUT_FOLDER,
            f"chat_{count:03}.json"
        )

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"Processed → {file}")

        count += 1

print("\n✅ Chat JSON files saved")'''

# -------------------------
# SINGLE FILE
# -------------------------
def process_chat_file(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return {
        "conversation": text
    }


# -------------------------
# FOLDER BATCH
# -------------------------
def process_chat_folder(folder_path=CHAT_FOLDER):

    results = []
    count = 1

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):

            path = os.path.join(folder_path, file)

            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            data = {
                "chat_id": f"chat_{count}",
                "file_name": file,
                "conversation": text
            }

            out_file = os.path.join(
                OUTPUT_FOLDER,
                f"chat_{count:03}.json"
            )

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            results.append(data)
            count += 1

    print("\n✅ Chat JSON files saved")
    return results

if __name__ == "__main__":
    process_chat_folder()



