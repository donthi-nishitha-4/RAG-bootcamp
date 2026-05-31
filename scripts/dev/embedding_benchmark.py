import json
import os
import time

import matplotlib.pyplot as plt
import torch
import umap
from sentence_transformers import SentenceTransformer

DATA_FILE = os.path.join("data", "dmrc", "dmrc_Synthetic_Dataset.json")
OUTPUT_DIR = os.path.join("docs")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")

MODELS = [
    "all-MiniLM-L6-v2",
    "BAAI/bge-large-en-v1.5",
    "nomic-ai/nomic-embed-text-v1.5",
]


def load_dmrc_texts(path):
    if not os.path.exists(path):
        return [], [], []
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    texts = [rec.get("text", "").strip() for rec in records if rec.get("text")]
    categories = [rec.get("category", "unknown") for rec in records if rec.get("text")]
    ids = [rec.get("id", str(i)) for i, rec in enumerate(records, start=1) if rec.get("text")]
    return texts, categories, ids


def ensure_dirs():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_umap(embeddings, n_neighbors=15, min_dist=0.1, random_state=42):
    reducer = umap.UMAP(
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric="cosine",
        random_state=random_state,
    )
    return reducer.fit_transform(embeddings)


def plot_umap(coords, categories, model_name, filename):
    palette = {
        "contract_clause": "#1f77b4",
        "ncr_description": "#ff7f0e",
        "dpr_narrative": "#2ca02c",
        "unknown": "#7f7f7f",
    }
    plt.figure(figsize=(8, 6))
    for category in sorted(set(categories)):
        idx = [i for i, cat in enumerate(categories) if cat == category]
        plt.scatter(
            coords[idx, 0],
            coords[idx, 1],
            label=category,
            alpha=0.8,
            s=40,
            c=palette.get(category, "#444444"),
        )
    plt.legend()
    plt.title(f"UMAP projection — {model_name}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()


def compare_models():
    ensure_dirs()
    texts, categories, ids = load_dmrc_texts(DATA_FILE)

    if not texts:
        raise FileNotFoundError(
            f"No synthetic DMRC data found at {DATA_FILE}. "
            "Please confirm the file path and dataset."
        )

    results = [
        "# Embedding Model Comparison",
        "",
        "| Model | Dim | Latency (ms/doc) | Device |",
        "|---|---|---|---|",
    ]

    for model_name in MODELS:
        print(f"\nLoading {model_name}...")
        try:
            kwargs = {}
            if "nomic" in model_name:
                kwargs["trust_remote_code"] = True
            model = SentenceTransformer(model_name, **kwargs)

            start_time = time.time()
            embeddings = model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=16,
            )
            latency = ((time.time() - start_time) / len(texts)) * 1000
            dim = embeddings.shape[1]
            device = "GPU" if torch.cuda.is_available() else "CPU"

            results.append(f"| {model_name} | {dim} | {latency:.2f} | {device} |")

            coords = build_umap(embeddings)
            plot_file = os.path.join(IMAGE_DIR, f"umap_{model_name.replace('/', '_')}.png")
            plot_umap(coords, categories, model_name, plot_file)
            print(f"Saved UMAP plot to {plot_file}")
        except Exception as exc:
            print(f"Failed to process {model_name}: {exc}")
            results.append(f"| {model_name} | N/A | FAILED | N/A |")

    combined_image = os.path.join(IMAGE_DIR, "umap_comparison.png")
    available_images = [
        os.path.join(IMAGE_DIR, f"umap_{model_name.replace('/', '_')}.png")
        for model_name in MODELS
        if os.path.exists(os.path.join(IMAGE_DIR, f"umap_{model_name.replace('/', '_')}.png"))
    ]

    if available_images:
        plt.figure(figsize=(12, 4))
        for i, img_path in enumerate(available_images):
            ax = plt.subplot(1, len(available_images), i + 1)
            ax.imshow(plt.imread(img_path))
            ax.set_title(os.path.basename(img_path).replace("umap_", "").replace(".png", ""))
            ax.axis("off")
        plt.tight_layout()
        plt.savefig(combined_image, dpi=200)
        plt.close()
        results.append("")
        results.append(f"![UMAP Comparison](images/umap_comparison.png)")

    output_md = os.path.join(OUTPUT_DIR, "embedding_comparison.md")
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"\nSaved markdown results to {output_md}")


if __name__ == "__main__":
    compare_models()