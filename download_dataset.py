import json
from pathlib import Path
from datasets import load_dataset

def main():
    print("Downloading hotpot_qa validation dataset...")
    # Lấy tập train để có đủ các level: easy, medium, hard
    dataset = load_dataset("hotpot_qa", "distractor", split="train")

    # In số lượng data mỗi level
    print(f"Number of easy samples: {len([x for x in dataset if x['level'] == 'easy'])}")
    print(f"Number of medium samples: {len([x for x in dataset if x['level'] == 'medium'])}")
    print(f"Number of hard samples: {len([x for x in dataset if x['level'] == 'hard'])}")
    
    easy_samples = []
    medium_samples = []
    hard_samples = []
    
    for item in dataset:
        if item["level"] == "easy" and len(easy_samples) < 33:
            easy_samples.append(item)
        elif item["level"] == "medium" and len(medium_samples) < 33:
            medium_samples.append(item)
        elif item["level"] == "hard" and len(hard_samples) < 34:
            hard_samples.append(item)
            
        if len(easy_samples) == 33 and len(medium_samples) == 33 and len(hard_samples) == 34:
            break
            
    subset = easy_samples + medium_samples + hard_samples
    
    formatted_data = []
    for item in subset:
        # Context is a dict with titles and sentences. We combine them.
        context_chunks = []
        for title, sentences in zip(item["context"]["title"], item["context"]["sentences"]):
            context_chunks.append({
                "title": title,
                "text": " ".join(sentences)
            })
            
        formatted_example = {
            "qid": item["id"],
            "difficulty": item["level"],
            "question": item["question"],
            "gold_answer": item["answer"],
            "context": context_chunks
        }
        formatted_data.append(formatted_example)
        
    out_path = Path("data/hotpot_100.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(formatted_data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved 100 examples to {out_path}")

if __name__ == "__main__":
    main()
